"""Embedded extensive-reading library and draft/publish pipeline."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from typing import Any


def _row_to_source(row: sqlite3.Row, include_text: bool = False) -> dict[str, Any]:
    text = row["text"]
    data = {
        "id": row["id"],
        "title": row["title"],
        "source_url": row["source_url"],
        "license": row["license"],
        "status": row["status"],
        "created_at": row["created_at"],
        "published_at": row["published_at"],
        "word_count": len(re.findall(r"[A-Za-z][A-Za-z'’\-]*", text)),
        "preview": text[:180],
    }
    if include_text:
        data["text"] = text
    return data


def list_sources(conn: sqlite3.Connection, status: str | None = None) -> list[dict[str, Any]]:
    if status in ("draft", "published"):
        rows = conn.execute(
            "SELECT * FROM reader_sources WHERE status = ? ORDER BY id DESC",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM reader_sources ORDER BY id DESC").fetchall()
    return [_row_to_source(row) for row in rows]


def get_source(conn: sqlite3.Connection, source_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM reader_sources WHERE id = ?", (source_id,)).fetchone()
    return _row_to_source(row, include_text=True) if row else None


def import_source(
    conn: sqlite3.Connection,
    *,
    title: str,
    text: str,
    source_url: str = "",
    license: str = "",
) -> dict[str, Any]:
    text = text.strip()
    if len(text) < 200:
        raise ValueError("文章至少需要 200 个字符")
    cursor = conn.execute(
        "INSERT INTO reader_sources (title, text, source_url, license, status) "
        "VALUES (?, ?, ?, ?, 'draft')",
        (title.strip() or "未命名文章", text, source_url.strip(), license.strip()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM reader_sources WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_source(row, include_text=True) or {}


def publish_source(conn: sqlite3.Connection, source_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM reader_sources WHERE id = ?", (source_id,)).fetchone()
    if not row:
        return None
    conn.execute(
        "UPDATE reader_sources SET status = 'published', published_at = ? WHERE id = ?",
        (datetime.now().isoformat(timespec="seconds"), source_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM reader_sources WHERE id = ?", (source_id,)).fetchone()
    return _row_to_source(updated, include_text=True) if updated else None
