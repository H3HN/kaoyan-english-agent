"""Deterministic vocabulary quiz generation from the learner's own wordbook."""
from __future__ import annotations

import random
import sqlite3
from typing import Any

MODES = ("choice", "spelling", "listening", "context")


def build_quiz(
    conn: sqlite3.Connection, *, limit: int = 8, mode: str = "choice"
) -> list[dict[str, Any]]:
    if mode not in MODES:
        mode = "choice"
    rows = conn.execute(
        """
        SELECT spelling, meaning, context, source
        FROM user_vocab_book
        ORDER BY CASE WHEN next_review <= datetime('now') THEN 0 ELSE 1 END,
                 next_review ASC, id DESC
        LIMIT ?
        """,
        (max(1, min(limit, 20)),),
    ).fetchall()
    if not rows:
        return []
    distractor_pool = [
        row["basic_meaning"]
        for row in conn.execute(
            "SELECT basic_meaning FROM syllabus_vocabulary WHERE basic_meaning != '' "
            "ORDER BY exam_frequency DESC LIMIT 80"
        ).fetchall()
    ]
    rng = random.Random(42)
    items: list[dict[str, Any]] = []
    for row in rows:
        spelling = row["spelling"]
        correct = row["meaning"]
        options = []
        if mode in ("choice", "listening"):
            distractors = [text for text in distractor_pool if text and text != correct]
            rng.shuffle(distractors)
            options = [correct, *distractors[:3]]
            rng.shuffle(options)
        items.append(
            {
                "mode": mode,
                "word": spelling,
                "meaning": correct,
                "context": row["context"] or "",
                "source": row["source"] or "",
                "options": options,
                "answer": correct if mode in ("choice", "listening") else spelling,
                "prompt": correct if mode in ("spelling", "context") else spelling,
            }
        )
    return items
