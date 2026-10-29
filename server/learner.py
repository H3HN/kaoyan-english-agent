"""Learner goal and reading-session persistence."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any


def get_goal(conn: sqlite3.Connection) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM learner_goal WHERE id = 1").fetchone()
    if not row:
        return None
    return {
        "target_score": row["target_score"],
        "exam_date": row["exam_date"],
        "daily_minutes": row["daily_minutes"],
        "current_level": row["current_level"],
        "updated_at": row["updated_at"],
    }


def save_goal(
    conn: sqlite3.Connection,
    *,
    target_score: int,
    exam_date: str,
    daily_minutes: int,
    current_level: str,
) -> dict[str, Any]:
    conn.execute(
        """
        INSERT INTO learner_goal
            (id, target_score, exam_date, daily_minutes, current_level, updated_at)
        VALUES (1, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            target_score = excluded.target_score,
            exam_date = excluded.exam_date,
            daily_minutes = excluded.daily_minutes,
            current_level = excluded.current_level,
            updated_at = datetime('now')
        """,
        (target_score, exam_date, daily_minutes, current_level),
    )
    conn.commit()
    return get_goal(conn) or {}


def save_reading_session(
    conn: sqlite3.Connection,
    *,
    passage_id: str,
    started_at: str,
    duration_seconds: int,
    answered: int,
    correct: int,
) -> dict[str, Any]:
    total = max(0, answered)
    accuracy = round(correct / total, 3) if total else 0.0
    cursor = conn.execute(
        """
        INSERT INTO reading_sessions
            (passage_id, started_at, duration_seconds, answered, correct, accuracy)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            passage_id,
            started_at,
            max(0, int(duration_seconds)),
            total,
            max(0, int(correct)),
            accuracy,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM reading_sessions WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return {
        "id": row["id"],
        "passage_id": row["passage_id"],
        "started_at": row["started_at"],
        "duration_seconds": row["duration_seconds"],
        "answered": row["answered"],
        "correct": row["correct"],
        "accuracy": row["accuracy"],
        "created_at": row["created_at"],
    }
