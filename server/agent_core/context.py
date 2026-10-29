import sqlite3
from typing import Any

from tools import get_sentence

def _ctx(ctx: dict[str, Any] | None) -> dict[str, Any]:
    ctx = ctx or {}
    return {
        "current_route": str(ctx.get("current_route") or "/dashboard"),
        "active_passage_id": ctx.get("active_passage_id"),
        "active_question_id": ctx.get("active_question_id"),
        "active_sentence_id": ctx.get("active_sentence_id"),
        "selected_raw_text": ctx.get("selected_raw_text"),
        "recent_event": ctx.get("recent_event"),
        "active_sentence_data": ctx.get("active_sentence_data"),
        "active_content_type": ctx.get("active_content_type"),
        "active_content_title": ctx.get("active_content_title"),
        "active_content_text": ctx.get("active_content_text"),
        "trigger_mode": str(ctx.get("trigger_mode") or "USER_CHAT"),
    }


def _question_payload(conn: sqlite3.Connection, question_id: str | None) -> dict[str, Any] | None:
    if not question_id:
        return None
    question = get_question(conn, question_id)
    if not question:
        return None
    source = (
        get_sentence(conn, question["source_sentence_id"])
        if question.get("source_sentence_id")
        else None
    )
    return {
        "question": question,
        "source": source,
        "correct_analysis": question["analysis"].get(question["correct_answer"], {}),
    }
