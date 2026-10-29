"""Listening dictation canvas tool."""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from ..canvas import _canvas_action


def _split_sentences(text: str) -> list[str]:
    items = [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", text.strip())
        if len(item.strip()) >= 18
    ]
    return items[:8]


def _listening_insight(conn: sqlite3.Connection, text: str, ctx: dict[str, Any]) -> dict[str, Any]:
    source_text = text.strip()
    source_label = "自定义听力 · 听写练习"
    row = None
    if not source_text and ctx.get("active_passage_id"):
        row = conn.execute(
            "SELECT text, year, exam_type, text_number FROM exam_passages WHERE id = ?",
            (ctx["active_passage_id"],),
        ).fetchone()
    if row:
        source_text = row["text"]
        source_label = f"{row['year']} {row['exam_type']} Text {row['text_number']} · 听力听写"
    sentences = _split_sentences(source_text)
    data = {
        "source_label": source_label,
        "sentences": [
            {"index": index + 1, "text": sentence}
            for index, sentence in enumerate(sentences)
        ],
    }
    return {
        "intro": "听力听写已铺到左侧。先听一遍抓主干，再逐句听写；提交后对照原文，不要求一次全对。",
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            _canvas_action("listening", data, source_label)
        ],
        "widgets": [],
        "llm_used": False,
    }
