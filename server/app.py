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
from llm import (
    analyze_imported_question,
    analyze_imported_questions_batch,
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
    record_option_attempt,
    remove_word,
    review_word,
    search_past_exams,
    search_vocab,
)
from workflows import run_chat_workflow, run_options_workflow, run_sentence_workflow


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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    context_id: str = Field(default="2024_en1_t1", max_length=80)


class SentenceRequest(BaseModel):
    sentence_id: str = Field(default="s4", max_length=40)


class OptionsRequest(BaseModel):
    question_id: str = Field(default="2024_en1_t1-q1", max_length=80)
    user_answer: str | None = Field(default=None, max_length=4)


class WordCreateRequest(BaseModel):
    spelling: str = Field(min_length=1, max_length=80)
    meaning: str = Field(min_length=1, max_length=500)
    source: str = Field(default="", max_length=200)
    context: str = Field(default="", max_length=1000)


class ReviewRequest(BaseModel):
    spelling: str = Field(min_length=1, max_length=80)
    remembered: bool


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
    text_number: int = Field(default=1, ge=1, le=10)
    answer_key: str = Field(default="", max_length=200)


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


@app.get("/api/questions")
def questions(conn: DB):
    return {"items": list_questions(conn)}


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
    updated = review_word(conn, payload.spelling, payload.remembered)
    if not updated:
        raise HTTPException(status_code=404, detail="word not found")
    return {"ok": True, "word": updated}


@app.post("/api/records")
def create_record(payload: RecordRequest, conn: DB):
    question = get_question(conn, payload.question_id)
    is_correct = payload.user_answer == payload.correct_answer
    if question:
        record, _ = record_option_attempt(conn, question, payload.user_answer)
        return {"ok": True, "record": record}
    cursor = conn.execute(
        """
        INSERT INTO practice_records
            (question_id, question_type, user_answer, correct_answer, is_correct)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            payload.question_id,
            payload.question_type,
            payload.user_answer,
            payload.correct_answer,
            1 if is_correct else 0,
        ),
    )
    conn.commit()
    return {
        "ok": True,
        "record": {
            "id": f"r{cursor.lastrowid}",
            "questionId": payload.question_id,
            "questionType": payload.question_type,
            "userAnswer": payload.user_answer,
            "correctAnswer": payload.correct_answer,
            "isCorrect": is_correct,
            "time": datetime.now().isoformat(timespec="seconds"),
        },
    }


@app.get("/api/report")
def report(conn: DB):
    return get_report(conn)


def _full_question(conn: sqlite3.Connection, question_id: str):
    question = get_question(conn, question_id)
    if not question:
        return None
    source = (
        get_sentence(conn, question["source_sentence_id"])
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
        "location": source["source"] if source else "自定义导入",
        "sourceSentence": source["text"] if source else "",
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
        "SELECT id FROM exam_questions ORDER BY year DESC, passage_id, number"
    ).fetchall()
    items = [
        item
        for item in (_full_question(conn, row["id"]) for row in rows)
        if item is not None
    ]
    return {"items": items}


@app.post("/api/exams/import")
def import_exam(payload: ExamImportRequest, conn: DB):
    options = {
        key: str(payload.options.get(key, "")).strip()
        for key in ("A", "B", "C", "D")
    }
    if not all(options.values()):
        raise HTTPException(
            status_code=400, detail="A/B/C/D four options are required"
        )
    if payload.correct_answer not in options:
        raise HTTPException(status_code=400, detail="invalid correct answer")

    passage_id = f"custom_{uuid.uuid4().hex[:8]}"
    conn.execute(
        "INSERT INTO exam_passages (id, year, exam_type, text_number, text) VALUES (?, ?, ?, ?, ?)",
        (
            passage_id,
            payload.year,
            payload.exam_type,
            payload.text_number,
            payload.passage.strip(),
        ),
    )

    chunks = [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", payload.passage.strip())
        if item.strip()
    ]
    sentences = []
    for index, text in enumerate(chunks, start=1):
        sentence_id = f"{passage_id}_s{index}"
        source_label = (
            f"自定义导入 · {payload.year} {payload.exam_type} "
            f"Text {payload.text_number} · 第1段第{index}句"
        )
        conn.execute(
            """
            INSERT INTO exam_sentences
                (id, passage_id, year, exam_type, text_number, paragraph,
                 sentence_index, text, grammar_tags, source_label)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, '[]', ?)
            """,
            (
                sentence_id,
                passage_id,
                payload.year,
                payload.exam_type,
                payload.text_number,
                index,
                text,
                source_label,
            ),
        )
        sentences.append(
            {"id": sentence_id, "text": text, "source": source_label}
        )

    source = max(sentences, key=lambda item: len(item["text"])) if sentences else None
    analysis_result = analyze_imported_question(
        payload.passage, payload.content, options, payload.correct_answer
    )
    if analysis_result:
        question_type = analysis_result["question_type"]
        analysis = analysis_result["analysis"]
        steps = analysis_result["steps"]
        analysis_source = "deepseek"
    else:
        question_type = (
            payload.question_type
            if payload.question_type
            in {"细节题", "主旨题", "推理题", "词义题", "态度题"}
            else "细节题"
        )
        analysis = {
            key: {
                "trapType": "正确" if key == payload.correct_answer else "待分析",
                "explanation": (
                    "与原文信息一致，为正确选项。"
                    if key == payload.correct_answer
                    else "导入题目尚未生成该选项分析。"
                ),
            }
            for key in ("A", "B", "C", "D")
        }
        steps = [
            "识别题型与题干关键词。",
            "回到原文定位对应句。",
            "逐项比对，标注陷阱类型。",
            "排除干扰项，确认正确答案。",
        ]
        analysis_source = "fallback"

    question_id = f"{passage_id}_q1"
    conn.execute(
        """
        INSERT INTO exam_questions
            (id, passage_id, year, exam_type, text_number, number,
             question_type, content, options_json, correct_answer,
             analysis_json, steps_json, source_sentence_id)
        VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question_id,
            passage_id,
            payload.year,
            payload.exam_type,
            payload.text_number,
            question_type,
            payload.content.strip(),
            json.dumps(options, ensure_ascii=False),
            payload.correct_answer,
            json.dumps(analysis, ensure_ascii=False),
            json.dumps(steps, ensure_ascii=False),
            source["id"] if source else None,
        ),
    )
    conn.commit()

    return {
        "ok": True,
        "question_id": question_id,
        "passage_id": passage_id,
        "analysis_source": analysis_source,
        "question": _full_question(conn, question_id),
    }


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


def _best_sentence(text: str, sentences: list[dict[str, Any]]) -> dict[str, Any] | None:
    tokens = set(re.findall(r"[a-z]{4,}", text.lower()))
    if not sentences:
        return None
    return max(
        sentences,
        key=lambda item: len(
            tokens & set(re.findall(r"[a-z]{4,}", item["text"].lower()))
        ),
    )


@app.post("/api/exams/auto-import")
def auto_import_exam(payload: AutoImportRequest, conn: DB):
    if not llm_status()["llm_configured"]:
        raise HTTPException(
            status_code=400,
            detail="LLM_API_KEY is required for automatic PDF import",
        )
    if payload.text:
        raw = payload.text
    elif payload.url:
        raw = _download_pdf_text(payload.url)
    else:
        raise HTTPException(status_code=400, detail="url or text is required")

    sliced = _slice_text(raw, payload.text_number)
    extraction = extract_exam_text(
        sliced,
        payload.year,
        payload.exam_type,
        payload.text_number,
        payload.answer_key,
    )
    if not extraction:
        raise HTTPException(status_code=422, detail="failed to extract reading text")

    passage_text = extraction["passage"]
    questions = extraction["questions"]
    key_letters = re.findall(r"[ABCD]", payload.answer_key.upper())
    answer_source = extraction.get("answer_source", "inferred")
    if len(key_letters) >= len(questions):
        for index, question in enumerate(questions):
            question["correct_answer"] = key_letters[index]
        answer_source = "provided"

    passage_id = f"auto_{uuid.uuid4().hex[:8]}"
    conn.execute(
        "INSERT INTO exam_passages (id, year, exam_type, text_number, text) VALUES (?, ?, ?, ?, ?)",
        (
            passage_id,
            payload.year,
            payload.exam_type,
            payload.text_number,
            passage_text,
        ),
    )
    chunks = [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", passage_text)
        if item.strip()
    ]
    sentence_rows = []
    for index, text_value in enumerate(chunks, start=1):
        sentence_id = f"{passage_id}_s{index}"
        source_label = (
            f"自动导入 · {payload.year} {payload.exam_type} "
            f"Text {payload.text_number} · 第1段第{index}句"
        )
        conn.execute(
            """
            INSERT INTO exam_sentences
                (id, passage_id, year, exam_type, text_number, paragraph,
                 sentence_index, text, grammar_tags, source_label)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, '[]', ?)
            """,
            (
                sentence_id,
                passage_id,
                payload.year,
                payload.exam_type,
                payload.text_number,
                index,
                text_value,
                source_label,
            ),
        )
        sentence_rows.append(
            {"id": sentence_id, "text": text_value, "source": source_label}
        )

    batch = analyze_imported_questions_batch(passage_text, questions)
    analysis_source = "deepseek" if batch else "fallback"
    question_ids = []
    for index, question in enumerate(questions):
        source_number = question["number"]
        number = 21 + (payload.text_number - 1) * 5 + index
        source = _best_sentence(
            question.get("source_quote")
            or f"{question['content']} {question['options'][question['correct_answer']]}",
            sentence_rows,
        )
        analyzed = (batch or {}).get(source_number)
        if analyzed:
            analysis = analyzed["analysis"]
            question_type = analyzed["question_type"]
            steps = analyzed["steps"] or [
                "识别题型与题干关键词。",
                "回到原文定位对应句。",
                "逐项比对，标注陷阱类型。",
                "排除干扰项，确认正确答案。",
            ]
        else:
            analysis = {
                key: {
                    "trapType": "正确" if key == question["correct_answer"] else "待分析",
                    "explanation": (
                        "与原文信息一致，为正确选项。"
                        if key == question["correct_answer"]
                        else "自动导入尚未生成该选项分析。"
                    ),
                }
                for key in ("A", "B", "C", "D")
            }
            question_type = question["question_type"]
            steps = [
                "识别题型与题干关键词。",
                "回到原文定位对应句。",
                "逐项比对，标注陷阱类型。",
                "排除干扰项，确认正确答案。",
            ]
        for key in ("A", "B", "C", "D"):
            if key != question["correct_answer"] and analysis[key].get("trapType") == "正确":
                analysis[key] = {
                    "trapType": "待分析",
                    "explanation": "自动分析结果与答案序列冲突，请复核。",
                }
        analysis[question["correct_answer"]] = {
            "trapType": "正确",
            "explanation": analysis[question["correct_answer"]].get(
                "explanation", "与原文信息一致，为正确选项。"
            ),
        }
        question_id = f"{passage_id}_q{number}"
        conn.execute(
            """
            INSERT INTO exam_questions
                (id, passage_id, year, exam_type, text_number, number,
                 question_type, content, options_json, correct_answer,
                 analysis_json, steps_json, source_sentence_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                passage_id,
                payload.year,
                payload.exam_type,
                payload.text_number,
                number,
                question_type,
                question["content"],
                json.dumps(question["options"], ensure_ascii=False),
                question["correct_answer"],
                json.dumps(analysis, ensure_ascii=False),
                json.dumps(steps, ensure_ascii=False),
                source["id"] if source else None,
            ),
        )
        question_ids.append(question_id)
    conn.commit()

    return {
        "ok": True,
        "passage_id": passage_id,
        "question_ids": question_ids,
        "analysis_source": analysis_source,
        "answer_source": answer_source,
        "questions": [
            item
            for item in (_full_question(conn, qid) for qid in question_ids)
            if item is not None
        ],
    }


@app.get("/api/vocab/search")
def vocab_search(
    conn: DB,
    q: str = Query(default="", max_length=80),
    limit: int = Query(default=20, ge=1, le=100),
):
    if not q.strip():
        return {"items": []}
    return {"items": search_vocab(conn, q.strip(), limit)}


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


@app.get("/api/agent/runs")
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
