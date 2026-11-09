import json
import os
import re
import sqlite3
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from db import connect, init_db
from exam_import import LETTERS
from llm import (
    analyze_sentence_breakdown,
    status as llm_status,
)
from plan import (
    generate_plan,
    get_insights,
    get_or_create_settings,
    get_plan,
    mark_item_done,
    update_settings,
)
from tools import (
    add_to_vocab_book,
    check_syllabus_vocab,
    get_meta,
    get_question,
    get_rare_words,
    get_report,
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


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
    ).strip()
    return [item.strip() for item in raw.split(",") if item.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", "")
    # Keep the retired import routes' 410 contract unchanged.
    if exc.status_code == 410:
        return JSONResponse(
            status_code=410,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    detail = exc.detail
    if isinstance(detail, dict):
        detail = {**detail, "request_id": request_id}
    else:
        detail = {"message": detail, "request_id": request_id}
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=exc.headers,
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


class SentenceRequest(BaseModel):
    sentence_id: str = Field(min_length=1, max_length=80)


class OptionsRequest(BaseModel):
    question_id: str = Field(min_length=1, max_length=80)
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


class PlanSettingsRequest(BaseModel):
    exam_date: str = Field(default="", max_length=10)
    daily_minutes: int = Field(default=60, ge=10, le=480)
    target_score: int = Field(default=70, ge=0, le=100)


class PlanItemDoneRequest(BaseModel):
    done: bool = True



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
    if not question:
        raise HTTPException(status_code=404, detail="published question not found")
    if payload.user_answer not in LETTERS:
        raise HTTPException(status_code=422, detail="answer must be A/B/C/D")
    record, _ = record_option_attempt(conn, question, payload.user_answer)
    return {"ok": True, "record": record}



@app.get("/api/report")
def report(conn: DB):
    return get_report(conn)


@app.get("/api/insights")
def insights(conn: DB):
    return get_insights(conn)


@app.get("/api/plan")
def plan(
    conn: DB,
    week_offset: int = Query(default=0, ge=-8, le=8),
):
    return get_plan(conn, week_offset)


@app.post("/api/plan/generate")
def plan_generate(
    conn: DB,
    force: bool = Query(default=False),
):
    return generate_plan(conn, force=force)


@app.post("/api/plan/items/{item_id}/done")
def plan_item_done(item_id: int, payload: PlanItemDoneRequest, conn: DB):
    result = mark_item_done(conn, item_id, payload.done)
    if result is None:
        raise HTTPException(status_code=404, detail="plan item not found")
    return result


@app.get("/api/plan/settings")
def plan_settings(conn: DB):
    return get_or_create_settings(conn)


@app.put("/api/plan/settings")
def plan_settings_update(payload: PlanSettingsRequest, conn: DB):
    try:
        return update_settings(
            conn,
            payload.exam_date,
            payload.daily_minutes,
            payload.target_score,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


def _assemble_full_question(
    question_row: sqlite3.Row,
    sentence_rows: dict[str, sqlite3.Row],
    passage_text: str,
) -> dict[str, Any]:
    """Assemble one /api/questions/full item from prefetched rows.

    Field contract matches the previous per-question implementation exactly,
    including the exact_quote-only display rule for the source sentence.
    """
    source = sentence_rows.get(question_row["source_sentence_id"])
    exact = question_row["location_status"] == "exact_quote"
    return {
        "id": question_row["id"],
        "number": question_row["number"],
        "questionType": question_row["question_type"],
        "content": question_row["content"],
        "options": json.loads(question_row["options_json"]),
        "correctAnswer": question_row["correct_answer"],
        "analysis": {
            key: {
                "trapType": value.get("trapType") or value.get("trap_type", ""),
                "explanation": value.get("explanation", ""),
            }
            for key, value in json.loads(question_row["analysis_json"]).items()
        },
        "steps": json.loads(question_row["steps_json"]),
        "location": source["source_label"] if source and exact else "待人工定位",
        "sourceSentence": source["text"] if source and exact else "",
        "sourceSentenceId": question_row["source_sentence_id"] if exact else None,
        "answerSource": question_row["answer_source"],
        "answerSourceNote": question_row["answer_source_note"],
        "reviewStatus": question_row["review_status"],
        "locationStatus": question_row["location_status"],
        "sourceQuote": question_row["source_quote"],
        "sourceHighlights": [],
        "passage": passage_text,
        "passageId": question_row["passage_id"],
        "year": question_row["year"],
        "examType": question_row["exam_type"],
        "textNumber": question_row["text_number"],
    }


@app.get("/api/questions/full")
def questions_full(
    conn: DB,
    year: int | None = Query(default=None, ge=2000, le=2100),
    exam_type: str = Query(default="", max_length=16),
    text_number: int | None = Query(default=None, ge=1, le=4),
    include_passage: bool = Query(default=True),
):
    """List published questions in three fixed queries (no per-question N+1).

    Optional filters mirror the reading-train cascade (year / exam_type /
    text_number). include_passage=false omits passage bodies from each item so
    a full-catalog listing stays lightweight; the passage text is then fetched
    per passage on demand instead of being repeated once per question.
    """
    clauses = ["p.publication_status='published'"]
    params: list[Any] = []
    if year is not None:
        clauses.append("q.year=?")
        params.append(year)
    if exam_type.strip():
        clauses.append("q.exam_type=?")
        params.append(exam_type.strip())
    if text_number is not None:
        clauses.append("q.text_number=?")
        params.append(text_number)
    question_rows = conn.execute(
        "SELECT q.* FROM exam_questions q JOIN exam_passages p ON p.id=q.passage_id "
        f"WHERE {' AND '.join(clauses)} "
        "ORDER BY q.year DESC, q.passage_id, q.number",
        params,
    ).fetchall()

    sentence_ids = sorted({r["source_sentence_id"] for r in question_rows if r["source_sentence_id"]})
    sentence_rows: dict[str, sqlite3.Row] = {}
    if sentence_ids:
        placeholders = ",".join("?" for _ in sentence_ids)
        for row in conn.execute(
            f"SELECT s.* FROM exam_sentences s WHERE s.id IN ({placeholders})",
            sentence_ids,
        ):
            sentence_rows[row["id"]] = row

    passage_texts: dict[str, str] = {}
    if include_passage:
        passage_ids = sorted({r["passage_id"] for r in question_rows})
        if passage_ids:
            placeholders = ",".join("?" for _ in passage_ids)
            for row in conn.execute(
                f"SELECT id, text FROM exam_passages WHERE id IN ({placeholders})",
                passage_ids,
            ):
                passage_texts[row["id"]] = row["text"]

    return {
        "items": [
            _assemble_full_question(row, sentence_rows, passage_texts.get(row["passage_id"], ""))
            for row in question_rows
        ]
    }


# The team CLI (scripts/question_bank.py) is the only ingestion path. These
# retired student-facing routes keep their 410 contract so old clients and
# documentation links keep receiving an explicit migration notice.
@app.post("/api/exams/import", dependencies=[Depends(_team_cli_only)])
def import_exam_retired():
    raise HTTPException(status_code=410, detail="题库管理已迁移到团队离线命令行 scripts/question_bank.py，学生接口不接受导入或管理操作")


@app.post("/api/exams/auto-import", dependencies=[Depends(_team_cli_only)])
def auto_import_exam_retired():
    raise HTTPException(status_code=410, detail="题库管理已迁移到团队离线命令行 scripts/question_bank.py，学生接口不接受导入或管理操作")


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
def agent_runs_retired():
    # agent_runs rows are inspectable offline via SQLite / team tooling.
    raise HTTPException(status_code=410, detail="题库管理已迁移到团队离线命令行 scripts/question_bank.py，学生接口不接受导入或管理操作")
