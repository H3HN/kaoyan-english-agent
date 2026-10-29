import io
import json
import re
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from pypdf import PdfReader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import connect, init_db
from exam_import import (
    ImportValidationError, LETTERS, QUESTION_TYPES, expected_numbers,
    locate_quote, normalize_passage, parse_answer_key, split_passage, validate_extraction,
)
from llm import (
    analyze_writing,
    analyze_imported_question,
    analyze_imported_questions_batch,
    analyze_sentence_breakdown,
    extract_exam_text,
    status as llm_status,
)
from tools import (
    add_to_vocab_book,
    check_syllabus_vocab,
    get_meta,
    get_question,
    get_rare_words,
    get_report,
    get_sentence,
    get_state,
    get_trap_rules,
    list_questions,
    list_sentences,
    list_vocab,
    record_option_attempt,
    remove_word,
    review_word,
    search_past_exams,
    search_vocab,
)
from workflows import run_chat_workflow, run_options_workflow, run_sentence_workflow
from agent_os import run_agent_turn
from knowledge_cards import get_learner_profile, get_trap_card, list_trap_cards
from learner import get_goal, save_goal, save_reading_session
from reader import get_source, import_source, list_sources, publish_source
from vocab_quiz import MODES, build_quiz
from sentence_library import (
    add_word_from_sentence,
    get_analysis,
    list_library,
    save_analysis,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="研英智学 Agent API",
    description="考研英语领域知识库、工具调用与工作流服务",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


DB = Annotated[sqlite3.Connection, Depends(get_db)]


def _team_cli_only():
    raise HTTPException(status_code=410, detail="题库管理已迁移到团队离线命令行 scripts/question_bank.py，学生接口不接受导入或管理操作")



class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    context_id: str = Field(default="", max_length=80)


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    client_context: dict[str, Any] = Field(default_factory=dict)
    trigger_mode: str = Field(default="USER_CHAT", max_length=20)


class SentenceRequest(BaseModel):
    sentence_id: str = Field(min_length=1, max_length=80)


class OptionsRequest(BaseModel):
    question_id: str = Field(min_length=1, max_length=80)
    user_answer: str | None = Field(default=None, max_length=4)


class ScheduleCompleteRequest(BaseModel):
    completed: bool = True


class LearnerGoalRequest(BaseModel):
    target_score: int = Field(default=70, ge=0, le=100)
    exam_date: str = Field(default="", max_length=20)
    daily_minutes: int = Field(default=30, ge=5, le=600)
    current_level: str = Field(default="基础", max_length=20)


class ReaderImportRequest(BaseModel):
    title: str = Field(default="未命名文章", max_length=200)
    text: str = Field(min_length=200, max_length=80000)
    source_url: str = Field(default="", max_length=1000)
    license: str = Field(default="", max_length=200)


class WritingReviewRequest(BaseModel):
    prompt: str = Field(default="考研英语写作练习", max_length=500)
    draft: str = Field(min_length=20, max_length=12000)


class ReadingSessionRequest(BaseModel):
    passage_id: str = Field(min_length=1, max_length=120)
    started_at: str = Field(min_length=1, max_length=40)
    duration_seconds: int = Field(ge=0, le=86400)
    answered: int = Field(ge=0, le=200)
    correct: int = Field(ge=0, le=200)


class SentenceSaveRequest(BaseModel):
    sentence_en: str = Field(min_length=1, max_length=5000)
    source_label: str = Field(default="自定义精析", max_length=160)
    exam_sentence_id: str | None = None
    sentence_data: dict[str, Any]


class WordFromSentenceRequest(BaseModel):
    word: str = Field(min_length=1, max_length=80)
    sentence_en: str = Field(min_length=1, max_length=5000)
    sentence_data: dict[str, Any]
    analysis_id: str | None = None
    source_label: str = Field(default="自定义精析", max_length=160)


class WordCreateRequest(BaseModel):
    spelling: str = Field(min_length=1, max_length=80)
    meaning: str = Field(min_length=1, max_length=500)
    source: str = Field(default="", max_length=200)
    context: str = Field(default="", max_length=1000)


class ReviewRequest(BaseModel):
    spelling: str = Field(min_length=1, max_length=80)
    remembered: bool | None = None
    quality: int | None = Field(default=None, ge=0, le=5)


class RecordRequest(BaseModel):
    question_id: str
    question_type: str
    user_answer: str
    correct_answer: str


class VocabCheckRequest(BaseModel):
    text: str | None = None
    words: list[str] | None = None


class AutoImportRequest(BaseModel):
    url: str | None = Field(default=None, max_length=2000)
    text: str | None = Field(default=None, max_length=50000)
    year: int = Field(ge=2000, le=2100)
    exam_type: str = Field(pattern=r"^英语[一二]$")
    text_number: int = Field(default=1, ge=1, le=4)
    answer_key: str = Field(default="", max_length=200)
    answer_source_note: str = Field(default="", max_length=500)


class ExamImportRequest(BaseModel):
    year: int = Field(ge=2000, le=2100)
    exam_type: str = Field(pattern=r"^英语[一二]$")
    text_number: int = Field(default=1, ge=1, le=20)
    passage: str = Field(min_length=50, max_length=20000)
    question_type: str = Field(default="细节题", max_length=20)
    content: str = Field(min_length=5, max_length=2000)
    options: dict[str, str]
    correct_answer: str = Field(pattern=r"^[ABCD]$")


@app.get("/")
def root():
    return {
        "service": "研英智学 Agent API",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health(conn: DB):
    meta = get_meta(conn)
    return {"status": "ok", "database": "connected", **meta, **llm_status()}


@app.get("/api/meta")
def meta(conn: DB):
    return get_meta(conn)


@app.get("/api/state")
def state(conn: DB):
    return get_state(conn)


@app.get("/api/sentences")
def sentences(conn: DB):
    return {"items": list_sentences(conn)}


@app.get("/api/passages")
def passages(conn: DB):
    rows = conn.execute(
        """
        SELECT p.id, p.year, p.exam_type, p.text_number,
               LENGTH(p.text) AS char_count,
               SUBSTR(p.text, 1, 160) AS preview,
               (SELECT COUNT(*) FROM exam_sentences s WHERE s.passage_id = p.id) AS sentence_count,
               (SELECT COUNT(*) FROM exam_questions q WHERE q.passage_id = p.id) AS question_count
        FROM exam_passages p
        WHERE p.publication_status = 'published'
        ORDER BY p.year DESC, p.text_number, p.id
        """
    ).fetchall()
    groups: dict[tuple[int, str, int], dict[str, Any]] = {}
    for row in rows:
        item = {
            "id": row["id"],
            "year": row["year"],
            "exam_type": row["exam_type"],
            "text_number": row["text_number"],
            "char_count": row["char_count"],
            "preview": row["preview"],
            "sentence_count": row["sentence_count"],
            "question_count": row["question_count"],
            "imported": str(row["id"]).startswith("auto_"),
        }
        key = (item["year"], item["exam_type"], item["text_number"])
        current = groups.get(key)
        if current is None:
            groups[key] = item
            continue
        if item["imported"] and not current["imported"]:
            groups[key] = item
        elif item["imported"] == current["imported"] and item["question_count"] > current["question_count"]:
            groups[key] = item
    items = sorted(
        groups.values(),
        key=lambda item: (-item["year"], item["exam_type"], item["text_number"]),
    )
    return {"items": items}


@app.get("/api/passages/{passage_id}/sentences")
def passage_sentences(passage_id: str, conn: DB):
    passage = conn.execute(
        "SELECT id, year, exam_type, text_number, text FROM exam_passages WHERE id = ? AND publication_status = 'published'",
        (passage_id,),
    ).fetchone()
    if not passage:
        raise HTTPException(status_code=404, detail="passage not found")
    rows = conn.execute(
        """
        SELECT id, sentence_index, paragraph, text, source_label
        FROM exam_sentences WHERE passage_id = ?
        ORDER BY paragraph, sentence_index
        """,
        (passage_id,),
    ).fetchall()
    items = []
    for row in rows:
        word_count = len([word for word in re.split(r"\s+", row["text"]) if word])
        items.append(
            {
                "id": row["id"],
                "index": row["sentence_index"],
                "paragraph": row["paragraph"],
                "text": row["text"],
                "source": row["source_label"],
                "word_count": word_count,
                "is_long": word_count >= 25,
            }
        )
    return {
        "passage": {
            "id": passage["id"],
            "year": passage["year"],
            "exam_type": passage["exam_type"],
            "text_number": passage["text_number"],
        },
        "items": items,
    }


@app.get("/api/sentences/{sentence_id}/breakdown")
def sentence_breakdown(sentence_id: str, conn: DB):
    row = conn.execute(
        "SELECT s.* FROM exam_sentences s JOIN exam_passages p ON p.id=s.passage_id WHERE s.id = ? AND p.publication_status='published'", (sentence_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="sentence not found")
    cached = conn.execute(
        "SELECT data_json, llm_used FROM sentence_breakdowns WHERE sentence_id = ?",
        (sentence_id,),
    ).fetchone()
    if cached:
        data = json.loads(cached["data_json"])
        data["llmUsed"] = bool(cached["llm_used"])
        return data

    text = row["text"]
    words = [word for word in re.split(r"\s+", text) if word]
    generated = analyze_sentence_breakdown(text)
    llm_used = bool(generated)
    if generated:
        data = generated
    else:
        data = {
            "isLong": len(words) >= 25,
            "main": text,
            "mainNote": "当前为工具兜底拆解：先保留整句，再按标点与连接词人工核对从句和修饰。",
            "clauseNote": "后端未返回结构化语法树，请结合下方工具链中的词库与真题切片核对。",
            "clauses": [],
            "modifiers": [],
            "translation": "",
            "translationLayers": [],
            "grammar": [],
            "examPoints": ["先找谓语，再判断从句修饰对象。"],
            "tree": [{"role": "整句", "label": text}],
            "segments": [{"text": text, "tone": "slate", "label": ""}],
        }
    data.update(
        {
            "id": row["id"],
            "index": row["sentence_index"],
            "source": row["source_label"],
            "original": text,
            "wordCount": len(words),
            "isLong": bool(data.get("isLong", len(words) >= 25)),
        }
    )
    conn.execute(
        "INSERT OR REPLACE INTO sentence_breakdowns (sentence_id, data_json, llm_used) VALUES (?, ?, ?)",
        (sentence_id, json.dumps(data, ensure_ascii=False), 1 if llm_used else 0),
    )
    conn.commit()
    data["llmUsed"] = llm_used
    return data


@app.get("/api/questions")
def questions(conn: DB):
    return {"items": list_questions(conn)}


@app.get("/api/learner/goal")
def learner_goal(conn: DB):
    return {"goal": get_goal(conn)}


@app.put("/api/learner/goal")
def update_learner_goal(payload: LearnerGoalRequest, conn: DB):
    return {"ok": True, "goal": save_goal(conn, **payload.model_dump())}


@app.post("/api/reading/sessions")
def create_reading_session(payload: ReadingSessionRequest, conn: DB):
    if payload.correct > payload.answered:
        raise HTTPException(status_code=422, detail="correct cannot exceed answered")
    return {"ok": True, "session": save_reading_session(conn, **payload.model_dump())}


@app.get("/api/reader/sources")
def reader_sources(conn: DB, status: str | None = None):
    return {"items": list_sources(conn, status)}


@app.post("/api/reader/import")
def reader_import(payload: ReaderImportRequest, conn: DB):
    try:
        source = import_source(
            conn,
            title=payload.title,
            text=payload.text,
            source_url=payload.source_url,
            license=payload.license,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "source": source}


@app.get("/api/reader/sources/{source_id}")
def reader_source(source_id: int, conn: DB):
    source = get_source(conn, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="reader source not found")
    return source


@app.post("/api/reader/sources/{source_id}/publish")
def reader_publish(source_id: int, conn: DB):
    source = publish_source(conn, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="reader source not found")
    return {"ok": True, "source": source}


@app.post("/api/writing/review")
def review_writing(payload: WritingReviewRequest, conn: DB):
    feedback = analyze_writing(payload.prompt, payload.draft)
    if not feedback:
        feedback = {
            "scores": {},
            "summary": "后端模型暂不可用，先保留作文。可以检查：是否回应题目、每段是否有中心句、是否出现拼写/主谓一致错误。",
            "issues": [],
            "minimum_revision": payload.draft,
            "rewrite_excerpt": "",
            "next_action": "先补一个明确的段落中心句，再重写主体段。",
            "llm_used": False,
        }
    conn.execute(
        "INSERT INTO writing_reviews (prompt, draft, feedback_json) VALUES (?, ?, ?)",
        (payload.prompt, payload.draft, json.dumps(feedback, ensure_ascii=False)),
    )
    conn.commit()
    return feedback


@app.get("/api/trap-cards")
def trap_cards():
    return {"items": list_trap_cards()}


@app.get("/api/trap-cards/{name}")
def trap_card(name: str):
    card = get_trap_card(name)
    if not card:
        raise HTTPException(status_code=404, detail="trap card not found")
    return card


@app.get("/api/learner/profile")
def learner_profile(conn: DB):
    return get_learner_profile(conn)


@app.get("/api/knowledge")
def knowledge(conn: DB):
    return {
        "traps": get_trap_rules(conn),
        "rare_words": get_rare_words(conn),
        "meta": get_meta(conn),
    }


@app.post("/api/workflow/sentence")
def sentence_workflow(payload: SentenceRequest, conn: DB):
    result = run_sentence_workflow(conn, payload.sentence_id)
    if not result:
        raise HTTPException(status_code=404, detail="sentence not found")
    return result


@app.post("/api/workflow/options")
def options_workflow(payload: OptionsRequest, conn: DB):
    result = run_options_workflow(conn, payload.question_id, payload.user_answer)
    if not result:
        raise HTTPException(status_code=404, detail="question not found")
    return result


@app.post("/api/workflow/chat")
def chat_workflow(payload: ChatRequest, conn: DB):
    return run_chat_workflow(conn, payload.message, payload.context_id)


@app.post("/api/agent/chat")
def agent_chat(payload: AgentChatRequest, conn: DB):
    return run_agent_turn(
        conn,
        payload.message,
        payload.client_context,
        payload.trigger_mode,
    )


@app.get("/api/sentences/library")
def sentence_library(conn: DB):
    return list_library(conn)


@app.get("/api/sentences/analyses/{analysis_id}")
def sentence_analysis(analysis_id: str, conn: DB):
    result = get_analysis(conn, analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="sentence analysis not found")
    return result


@app.post("/api/sentences/save")
def save_sentence_analysis(payload: SentenceSaveRequest, conn: DB):
    try:
        result = save_analysis(
            conn,
            {
                "sentence_en": payload.sentence_en,
                "source_label": payload.source_label,
                "exam_sentence_id": payload.exam_sentence_id,
                "sentence_data": payload.sentence_data,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, **result}


@app.post("/api/wordbook/from-sentence")
def word_from_sentence(payload: WordFromSentenceRequest, conn: DB):
    try:
        result = add_word_from_sentence(
            conn,
            word=payload.word,
            sentence_en=payload.sentence_en,
            sentence_data=payload.sentence_data,
            analysis_id=payload.analysis_id,
            source_label=payload.source_label,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@app.get("/api/schedule")
def schedule(conn: DB):
    rows = conn.execute(
        "SELECT * FROM study_schedule_tasks ORDER BY scheduled_date, id"
    ).fetchall()
    return {"items": [dict(row) for row in rows]}


@app.post("/api/schedule/{task_id}/complete")
def complete_schedule_task(task_id: int, payload: ScheduleCompleteRequest, conn: DB):
    status = "completed" if payload.completed else "pending"
    cursor = conn.execute(
        "UPDATE study_schedule_tasks SET status = ? WHERE id = ?",
        (status, task_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="task not found")
    row = conn.execute(
        "SELECT * FROM study_schedule_tasks WHERE id = ?", (task_id,)
    ).fetchone()
    return {"ok": True, "task": dict(row)}


@app.get("/api/vocab/quiz")
def vocab_quiz(conn: DB, limit: int = 8, mode: str = "choice"):
    if mode not in MODES:
        raise HTTPException(status_code=422, detail="unsupported quiz mode")
    return {"items": build_quiz(conn, limit=max(1, min(limit, 20)), mode=mode)}


@app.get("/api/wordbook")
def wordbook(conn: DB):
    return {"items": get_state(conn)["words"]}


@app.post("/api/wordbook")
def create_word(payload: WordCreateRequest, conn: DB):
    word, trace = add_to_vocab_book(
        conn,
        payload.spelling,
        context=payload.context,
        source=payload.source,
    )
    return {"ok": bool(word), "word": word, "tool_trace": trace}


@app.delete("/api/wordbook/{spelling}")
def delete_word(spelling: str, conn: DB):
    removed = remove_word(conn, spelling)
    if not removed:
        raise HTTPException(status_code=404, detail="word not found")
    return {"ok": True, "spelling": spelling}


@app.post("/api/wordbook/review")
def review_vocab(payload: ReviewRequest, conn: DB):
    updated = review_word(
        conn, payload.spelling, payload.remembered, payload.quality
    )
    if not updated:
        raise HTTPException(status_code=404, detail="word not found")
    return {"ok": True, "word": updated}


@app.post("/api/records")
def create_record(payload: RecordRequest, conn: DB):
    question = get_question(conn, payload.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="published question not found")
    if payload.user_answer not in LETTERS:
        raise HTTPException(status_code=422, detail="answer must be A/B/C/D")
    record, _ = record_option_attempt(conn, question, payload.user_answer)
    return {"ok": True, "record": record}



@app.get("/api/report")
def report(conn: DB):
    return get_report(conn)


def _full_question(conn: sqlite3.Connection, question_id: str, *, include_drafts=True):
    question = get_question(conn, question_id, include_drafts=include_drafts)
    if not question:
        return None
    source = (
        get_sentence(conn, question["source_sentence_id"], include_drafts=include_drafts)
        if question.get("source_sentence_id")
        else None
    )
    passage_row = conn.execute(
        "SELECT text FROM exam_passages WHERE id = ?",
        (question["passage_id"],),
    ).fetchone()
    return {
        "id": question["id"],
        "number": question["number"],
        "questionType": question["question_type"],
        "content": question["content"],
        "options": question["options"],
        "correctAnswer": question["correct_answer"],
        "analysis": question["analysis"],
        "steps": question["steps"],
        "location": source["source"] if source and question["location_status"] == "exact_quote" else "待人工定位",
        "sourceSentence": source["text"] if source and question["location_status"] == "exact_quote" else "",
        "sourceSentenceId": question["source_sentence_id"] if question["location_status"] == "exact_quote" else None,
        "answerSource": question["answer_source"],
        "answerSourceNote": question["answer_source_note"],
        "reviewStatus": question["review_status"],
        "locationStatus": question["location_status"],
        "sourceQuote": question["source_quote"],
        "sourceHighlights": [],
        "passage": passage_row["text"] if passage_row else "",
        "passageId": question["passage_id"],
        "year": question["year"],
        "examType": question["exam_type"],
        "textNumber": question["text_number"],
    }


@app.get("/api/questions/full")
def questions_full(conn: DB):
    rows = conn.execute(
        "SELECT q.id FROM exam_questions q JOIN exam_passages p ON p.id=q.passage_id WHERE p.publication_status='published' ORDER BY q.year DESC, q.passage_id, q.number"
    ).fetchall()
    items = [
        item
        for item in (_full_question(conn, row["id"], include_drafts=False) for row in rows)
        if item is not None
    ]
    return {"items": items}


def _validation_error(exc: ImportValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail={
        "code": "invalid_exam", "message": "真题校验失败，未入库", "issues": exc.issues,
    })


def _insert_sentences(conn, passage_id, payload, passage_text, prefix):
    rows = split_passage(passage_text)
    for global_index, row in enumerate(rows, 1):
        row["id"] = f"{passage_id}_s{global_index}"
        row["source"] = (
            f"{prefix} · {payload.year} {payload.exam_type} Text {payload.text_number} · "
            f"第{row['paragraph']}段第{row['sentence_index']}句"
        )
        conn.execute(
            "INSERT INTO exam_sentences "
            "(id, passage_id, year, exam_type, text_number, paragraph, sentence_index, "
            "text, grammar_tags, source_label, char_start, char_end) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, '[]', ?, ?, ?)",
            (row["id"], passage_id, payload.year, payload.exam_type, payload.text_number,
             row["paragraph"], row["sentence_index"], row["text"], row["source"],
             row["char_start"], row["char_end"]),
        )
    return rows


def _analysis_fields(question, analyzed=None):
    analyzed = analyzed or {}
    raw = analyzed.get("analysis") or {}
    analysis = {}
    for key in LETTERS:
        item = raw.get(key) if isinstance(raw.get(key), dict) else {}
        trap = item.get("trapType", "待分析")
        explanation = item.get("explanation", "")
        if key == question["correct_answer"]:
            if trap and trap != "正确":
                explanation = "模型分析与当前答案冲突，请复核。"
            trap = "正确"
            explanation = explanation or "按当前导入答案标记，尚未人工复核。"
        elif trap == "正确":
            trap = "待分析"
            explanation = "模型分析与当前答案冲突，请复核。"
        analysis[key] = {"trapType": trap or "待分析",
                         "explanation": explanation or "尚未生成该选项分析。"}
    qtype = analyzed.get("question_type") or question.get("question_type", "细节题")
    if qtype not in QUESTION_TYPES:
        qtype = "细节题"
    steps = analyzed.get("steps") or [
        "识别题型与题干关键词。", "回到原文核对证据，无法定位时人工复核。",
        "逐项比对，标注陷阱类型。", "依据可靠答案核对结论。",
    ]
    return qtype, analysis, steps


def _insert_question(conn, passage_id, payload, question, analyzed, sentence_rows,
                     passage_text, answer_source, source_note):
    qtype, analysis, steps = _analysis_fields(question, analyzed)
    quote = question.get("source_quote", "")
    location = locate_quote(quote, passage_text, sentence_rows)
    question_id = f"{passage_id}_q{question['number']}"
    conn.execute(
        "INSERT INTO exam_questions "
        "(id, passage_id, year, exam_type, text_number, number, question_type, content, "
        "options_json, correct_answer, analysis_json, steps_json, source_sentence_id, "
        "answer_source, answer_source_note, review_status, source_quote, location_status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)",
        (question_id, passage_id, payload.year, payload.exam_type, payload.text_number,
         question["number"], qtype, question["content"],
         json.dumps(question["options"], ensure_ascii=False), question["correct_answer"],
         json.dumps(analysis, ensure_ascii=False), json.dumps(steps, ensure_ascii=False),
         location["source_sentence_id"], answer_source, source_note, quote,
         location["location_status"]),
    )
    return question_id


def _manual_duplicate(conn, payload, passage_text):
    # Separate manual questions can share a passage, but repeated submissions of
    # the same question are rejected instead of creating indistinguishable copies.
    return conn.execute(
        "SELECT q.id FROM exam_questions q JOIN exam_passages p ON p.id=q.passage_id "
        "WHERE p.year=? AND p.exam_type=? AND p.text_number=? AND p.text=? AND q.content=?",
        (payload.year, payload.exam_type, payload.text_number, passage_text, payload.content.strip()),
    ).fetchone()


def _duplicate_error():
    return HTTPException(status_code=409, detail={
        "code": "duplicate_exam", "message": "该真题已导入，请先核对现有题库；本次未写入或覆盖。",
    })


@app.post("/api/exams/import", dependencies=[Depends(_team_cli_only)])
def import_exam(payload: ExamImportRequest, conn: DB):
    options = {key: payload.options.get(key, "").strip() for key in LETTERS}
    if set(payload.options) != set(LETTERS) or not all(options.values()):
        raise HTTPException(status_code=400, detail="A/B/C/D four options are required")
    passage_text = normalize_passage(payload.passage)
    if len(passage_text) < 50 or not payload.content.strip():
        raise HTTPException(status_code=422, detail="文章或题干不能为空，文章须至少 50 字符")
    if _manual_duplicate(conn, payload, passage_text):
        raise _duplicate_error()
    # No write transaction is held during network/LLM calls.
    analyzed = analyze_imported_question(
        passage_text, payload.content.strip(), options, payload.correct_answer,
    )
    question = {"number": 1, "content": payload.content.strip(), "options": options,
                "correct_answer": payload.correct_answer, "question_type": payload.question_type,
                "source_quote": (analyzed or {}).get("source_quote", "")}
    passage_id = f"custom_{uuid.uuid4().hex}"
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        if _manual_duplicate(conn, payload, passage_text):
            raise _duplicate_error()
        conn.execute(
            "INSERT INTO exam_passages (id, year, exam_type, text_number, text) VALUES (?, ?, ?, ?, ?)",
            (passage_id, payload.year, payload.exam_type, payload.text_number, passage_text),
        )
        rows = _insert_sentences(conn, passage_id, payload, passage_text, "自定义导入")
        question_id = _insert_question(
            conn, passage_id, payload, question, analyzed, rows, passage_text,
            "manual", "用户手工录入答案，尚未人工复核来源",
        )
    return {"ok": True, "question_id": question_id, "passage_id": passage_id,
            "analysis_source": "deepseek" if analyzed else "fallback",
            "answer_source": "manual", "review_status": "pending",
            "question": _full_question(conn, question_id)}


def _download_pdf_text(url: str) -> str:
    if not url.lower().startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="PDF URL must use http(s)")
    response = None
    for trust_env in (False, True):
        try:
            with httpx.Client(
                follow_redirects=True, timeout=60, trust_env=trust_env
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                break
        except Exception:
            response = None
    if response is None:
        raise HTTPException(status_code=400, detail="PDF download failed")
    if len(response.content) > 30 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF is larger than 30MB")
    try:
        reader = PdfReader(io.BytesIO(response.content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"PDF parse failed: {exc}") from exc


def _slice_text(raw: str, text_number: int) -> str:
    pattern = re.compile(
        rf"(?is)\bText\s*{text_number}\b(.*?)(?=\bText\s*{text_number + 1}\b|\bSection\s*III\b|\bPart\s*B\b|$)"
    )
    match = pattern.search(raw)
    return match.group(1) if match else raw


def _auto_duplicate(conn, payload):
    # Seed examples are placeholders and must not block a first real import.
    return conn.execute(
        "SELECT id FROM exam_passages WHERE year=? AND exam_type=? AND text_number=? "
        "AND (id LIKE 'auto_%' OR id LIKE 'custom_%') LIMIT 1",
        (payload.year, payload.exam_type, payload.text_number),
    ).fetchone()


@app.post("/api/exams/auto-import", dependencies=[Depends(_team_cli_only)])
def auto_import_exam(payload: AutoImportRequest, conn: DB):
    try:
        numbers = expected_numbers(payload.text_number)
        parse_answer_key(payload.answer_key, numbers)
    except ImportValidationError as exc:
        raise _validation_error(exc) from exc
    if _auto_duplicate(conn, payload):
        raise _duplicate_error()
    if not llm_status()["llm_configured"]:
        raise HTTPException(status_code=400, detail="LLM_API_KEY is required for automatic PDF import")
    if payload.text and payload.text.strip():
        raw = payload.text
    elif payload.url:
        raw = _download_pdf_text(payload.url)
    else:
        raise HTTPException(status_code=400, detail="url or text is required")
    sliced = _slice_text(raw, payload.text_number)
    if not sliced.strip():
        raise HTTPException(status_code=422, detail="未提取到文本；扫描版 PDF 需要先做 OCR")
    if len(sliced) > 50000:
        raise HTTPException(status_code=422, detail="当前 Text 超过 50000 字符，请提供该篇文本，不能静默截断")
    extraction = extract_exam_text(
        sliced, payload.year, payload.exam_type, payload.text_number, payload.answer_key,
    )
    if extraction is None:
        raise HTTPException(status_code=422, detail="failed to extract reading text")
    try:
        validated = validate_extraction(extraction, payload.text_number, payload.answer_key)
    except ImportValidationError as exc:
        raise _validation_error(exc) from exc
    passage_text = validated["passage"]
    questions = validated["questions"]
    answer_source = validated["answer_source"]
    # Model analysis is prepared entirely before starting the atomic DB write.
    batch = analyze_imported_questions_batch(passage_text, questions)
    passage_id = f"auto_{uuid.uuid4().hex}"
    question_ids = []
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        # Recheck while holding the write lock: handles concurrent duplicate requests.
        if _auto_duplicate(conn, payload):
            raise _duplicate_error()
        conn.execute(
            "INSERT INTO exam_passages (id, year, exam_type, text_number, text) VALUES (?, ?, ?, ?, ?)",
            (passage_id, payload.year, payload.exam_type, payload.text_number, passage_text),
        )
        rows = _insert_sentences(conn, passage_id, payload, passage_text, "自动导入")
        note = payload.answer_source_note.strip() or (
            "用户提供答案序列，尚未核对权威来源" if answer_source == "provided"
            else "模型根据文章推断，尚未人工复核"
        )
        for question in questions:
            question_ids.append(_insert_question(
                conn, passage_id, payload, question, (batch or {}).get(question["number"]),
                rows, passage_text, answer_source, note,
            ))
    items = [_full_question(conn, qid) for qid in question_ids]
    warnings = ["导入题目尚未人工复核，答案来源不代表答案已核实。"]
    if "\n\n" not in passage_text:
        warnings.append("提取文本无明确空行段落；目前作为一段保存，不代表原卷只有一段。")
    if any(item["locationStatus"] != "exact_quote" for item in items):
        warnings.append("部分题目无唯一单句证据，保留引文并等待人工定位。")
    return {"ok": True, "passage_id": passage_id, "question_ids": question_ids,
            "analysis_source": "deepseek" if batch else "fallback",
            "answer_source": answer_source, "review_status": "pending",
            "warnings": warnings, "questions": items}


@app.get("/api/vocab/search")
def vocab_search(
    conn: DB,
    q: str = Query(default="", max_length=80),
    limit: int = Query(default=20, ge=1, le=100),
):
    if not q.strip():
        return {"items": []}
    return {"items": search_vocab(conn, q.strip(), limit)}


@app.get("/api/vocab")
def vocab_browse(
    conn: DB,
    q: str = Query(default="", max_length=80),
    level: str = Query(default="", max_length=16),
    sort: str = Query(default="freq", pattern="^(freq|alpha)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_vocab(conn, q.strip(), level.strip(), sort, offset, limit)


@app.post("/api/tools/check-vocab")
def tool_check_vocab(payload: VocabCheckRequest, conn: DB):
    if payload.words:
        entries, trace = check_syllabus_vocab(conn, payload.words)
    elif payload.text:
        entries, trace = check_syllabus_vocab(conn, payload.text)
    else:
        raise HTTPException(status_code=400, detail="text or words is required")
    return {"items": entries, "tool_trace": trace}


@app.get("/api/tools/search-exams")
def tool_search_exams(
    conn: DB,
    q: str = Query(default="", max_length=300),
    grammar: str = Query(default="", max_length=200),
    limit: int = Query(default=5, ge=1, le=20),
):
    citations, trace = search_past_exams(conn, query=q, grammar=grammar, limit=limit)
    return {"items": citations, "tool_trace": trace}


@app.get("/api/agent/runs", dependencies=[Depends(_team_cli_only)])
def agent_runs(
    conn: DB,
    limit: int = Query(default=10, ge=1, le=50),
):
    rows = conn.execute(
        "SELECT id, workflow, input_json, output_json, tool_trace_json, created_at "
        "FROM agent_runs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return {
        "items": [
            {
                "id": row["id"],
                "workflow": row["workflow"],
                "input": json.loads(row["input_json"]),
                "output": json.loads(row["output_json"]),
                "tool_trace": json.loads(row["tool_trace_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    }
