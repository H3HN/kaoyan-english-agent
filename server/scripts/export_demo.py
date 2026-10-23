#!/usr/bin/env python3
"""Export imported exam content from the local SQLite DB to a portable JSON snapshot.

Only imported passages (id starts with ``auto_``) and their sentences/questions
are exported. The base vocabulary and sample passages are recreated by seed.py,
so they are intentionally not duplicated in the snapshot.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
OUT_PATH = DATA_DIR / "demo_snapshot.json"


def fetch_rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    cursor = conn.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]


def main() -> int:
    if not DB_PATH.exists():
        raise SystemExit(f"database not found: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    passages = fetch_rows(
        conn,
        "SELECT id, year, exam_type, text_number, text FROM exam_passages "
        "WHERE id LIKE 'auto_%' ORDER BY year DESC, text_number",
    )
    ids = [item["id"] for item in passages]
    if not ids:
        raise SystemExit("no imported passages found (id LIKE 'auto_%')")
    placeholders = ",".join("?" for _ in ids)
    sentences = fetch_rows(
        conn,
        f"SELECT id, passage_id, year, exam_type, text_number, paragraph, "
        f"sentence_index, text, grammar_tags, source_label "
        f"FROM exam_sentences WHERE passage_id IN ({placeholders}) "
        f"ORDER BY passage_id, sentence_index",
        tuple(ids),
    )
    questions = fetch_rows(
        conn,
        f"SELECT id, passage_id, year, exam_type, text_number, number, "
        f"question_type, content, options_json, correct_answer, analysis_json, "
        f"steps_json, source_sentence_id FROM exam_questions "
        f"WHERE passage_id IN ({placeholders}) ORDER BY passage_id, number",
        tuple(ids),
    )
    sentence_ids = [item["id"] for item in sentences]
    breakdowns: list[dict] = []
    if sentence_ids:
        s_placeholders = ",".join("?" for _ in sentence_ids)
        breakdowns = fetch_rows(
            conn,
            f"SELECT sentence_id, data_json, llm_used, created_at "
            f"FROM sentence_breakdowns WHERE sentence_id IN ({s_placeholders}) "
            f"ORDER BY sentence_id",
            tuple(sentence_ids),
        )
    snapshot = {
        "format": "kaoyan-demo-snapshot",
        "version": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "note": (
            "Imported exam content for course testing only. "
            "Source PDFs are not included. Do not redistribute outside the course."
        ),
        "counts": {
            "passages": len(passages),
            "sentences": len(sentences),
            "questions": len(questions),
            "breakdowns": len(breakdowns),
        },
        "passages": passages,
        "sentences": sentences,
        "questions": questions,
        "breakdowns": breakdowns,
    }
    OUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"wrote {OUT_PATH} "
        f"({len(passages)} passages, {len(sentences)} sentences, "
        f"{len(questions)} questions, {len(breakdowns)} breakdowns)"
    )
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
