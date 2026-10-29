"""Long-sentence library entities and word-context links.

`sentence_breakdowns` remains the cache for exam sentences. This module owns
the user-facing library overlay so a saved ad-hoc analysis can be reopened
without polluting the question bank.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any

from tools import add_to_vocab_book, word_to_dict


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("sentence_data") or payload.get("data") or {}
    if not isinstance(data, dict):
        data = {}
    sentence_en = str(payload.get("sentence_en") or data.get("sentence_en") or "").strip()
    if not sentence_en:
        raise ValueError("sentence_en is required")
    return {
        "sentence_en": sentence_en,
        "source_label": str(payload.get("source_label") or data.get("source_label") or "自定义精析"),
        "source_type": str(payload.get("source_type") or "USER_SAVED"),
        "exam_sentence_id": payload.get("exam_sentence_id") or None,
        "data": data,
    }


def save_analysis(conn: sqlite3.Connection, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_payload(payload)
    sentence_en = normalized["sentence_en"]
    exam_sentence_id = normalized["exam_sentence_id"]
    source_label = normalized["source_label"]
    source_type = normalized["source_type"]
    if source_type not in ("USER_SAVED", "EXAM_FEATURED"):
        source_type = "USER_SAVED"

    existing = None
    if exam_sentence_id:
        existing = conn.execute(
            "SELECT * FROM sentence_analyses WHERE exam_sentence_id = ?",
            (exam_sentence_id,),
        ).fetchone()
    if not existing:
        existing = conn.execute(
            "SELECT * FROM sentence_analyses WHERE sentence_en = ? AND source_label = ?",
            (sentence_en, source_label),
        ).fetchone()
    if existing:
        analysis_id = existing["id"]
        conn.execute(
            "UPDATE sentence_analyses SET data_json = ?, source_type = ?, updated_at = ? WHERE id = ?",
            (
                json.dumps(normalized["data"], ensure_ascii=False),
                source_type,
                _now(),
                analysis_id,
            ),
        )
    else:
        prefix = "exam" if exam_sentence_id else "usr"
        analysis_id = f"{prefix}_{uuid.uuid4().hex[:12]}"
        conn.execute(
            """
            INSERT INTO sentence_analyses
                (id, exam_sentence_id, sentence_en, source_type, source_label,
                 data_json, is_favorite, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                analysis_id,
                exam_sentence_id,
                sentence_en,
                source_type,
                source_label,
                json.dumps(normalized["data"], ensure_ascii=False),
                _now(),
                _now(),
            ),
        )
    conn.commit()
    return {
        "analysis_id": analysis_id,
        "source_type": source_type,
        "source_label": source_label,
        "saved": True,
    }


def get_analysis(conn: sqlite3.Connection, analysis_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM sentence_analyses WHERE id = ?", (analysis_id,)
    ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "exam_sentence_id": row["exam_sentence_id"],
        "sentence_en": row["sentence_en"],
        "source_type": row["source_type"],
        "source_label": row["source_label"],
        "data": json.loads(row["data_json"]),
        "saved": True,
        "updated_at": row["updated_at"],
    }


def _featured(conn: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT s.id, s.text, s.source_label, s.grammar_tags
        FROM exam_sentences AS s
        JOIN exam_passages AS p ON p.id = s.passage_id
        WHERE p.publication_status = 'published'
        ORDER BY length(s.text) DESC, s.year DESC, s.sentence_index
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    items = []
    for row in rows:
        tags = json.loads(row["grammar_tags"] or "[]")
        items.append(
            {
                "id": row["id"],
                "sentence_en": row["text"],
                "preview": row["text"][:60],
                "source_label": row["source_label"],
                "grammar_tags": tags[:3],
                "source_type": "EXAM_FEATURED",
            }
        )
    return items


def _saved(conn: sqlite3.Connection, limit: int = 40) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, sentence_en, source_label, data_json, updated_at
        FROM sentence_analyses
        WHERE source_type = 'USER_SAVED'
        ORDER BY is_favorite DESC, updated_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    items = []
    for row in rows:
        data = json.loads(row["data_json"])
        items.append(
            {
                "id": row["id"],
                "sentence_en": row["sentence_en"],
                "preview": row["sentence_en"][:60],
                "source_label": row["source_label"],
                "grammar_tags": [item.get("name", "") for item in data.get("step5_vocab_and_grammar", {}).get("grammar", [])][:3],
                "source_type": "USER_SAVED",
                "updated_at": row["updated_at"],
            }
        )
    return items


def list_library(conn: sqlite3.Connection) -> dict[str, Any]:
    return {"featured": _featured(conn), "saved": _saved(conn)}


def add_word_from_sentence(
    conn: sqlite3.Connection,
    *,
    word: str,
    sentence_en: str,
    sentence_data: dict[str, Any],
    analysis_id: str | None = None,
    source_label: str = "自定义精析",
) -> dict[str, Any]:
    if analysis_id:
        saved = get_analysis(conn, analysis_id)
        if not saved:
            analysis_id = None
    if not analysis_id:
        saved = save_analysis(
            conn,
            {
                "sentence_en": sentence_en,
                "source_label": source_label,
                "sentence_data": sentence_data,
            },
        )
        analysis_id = saved["analysis_id"]
    word_row, trace = add_to_vocab_book(
        conn,
        word,
        context=sentence_en[:500],
        source=source_label,
    )
    if word_row:
        conn.execute(
            """
            UPDATE user_vocab_book
            SET context_sentence_id = ?, context_sentence_en = ?,
                context = CASE WHEN context = '' THEN ? ELSE context END
            WHERE spelling = ?
            """,
            (analysis_id, sentence_en[:1000], sentence_en[:500], word_row["spelling"].lower()),
        )
        conn.commit()
        fresh = conn.execute(
            "SELECT * FROM user_vocab_book WHERE spelling = ?",
            (word_row["spelling"].lower(),),
        ).fetchone()
        word_row = word_to_dict(fresh)
    return {
        "ok": bool(word_row),
        "word": word_row,
        "analysis_id": analysis_id,
        "sentence_saved": True,
        "tool_trace": trace,
    }


def save_current_sentence_to_library(
    conn: sqlite3.Connection, payload: dict[str, Any]
) -> dict[str, Any]:
    """Agent-facing alias used by the natural-language save command."""
    return save_analysis(conn, payload)
