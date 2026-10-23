import json
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import connect, init_db
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
    return {"status": "ok", "database": "connected", **meta}


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
    return run_chat_workflow(conn, payload.message)


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
