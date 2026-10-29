#!/usr/bin/env python3
"""Load the portable imported-exam snapshot into the local SQLite database.

Run after installing dependencies (or after the backend has created app.db):

    python scripts/load_demo.py
    python scripts/load_demo.py --reset   # remove prior imported passages first

The snapshot contains only imported passages, sentences, questions and cached
sentence breakdowns. Base vocabulary, 2 sample passages and demo learning
state are created by seed.py. A snapshot restores content only: every restored
passage is draft and every restored question is pending review, so restored
content must be reviewed and published again before users can see it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db import DB_PATH, connect, init_db  # noqa: E402

SNAPSHOT = BASE_DIR / "data" / "demo_snapshot.json"
IMPORTED_PASSAGE_WHERE = "id LIKE 'auto_%' OR id LIKE 'bank_%' OR id LIKE 'custom_%'"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete existing imported passages before loading",
    )
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    args = parser.parse_args()

    if not args.snapshot.exists():
        raise SystemExit(f"snapshot not found: {args.snapshot}")
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if snapshot.get("format") != "kaoyan-demo-snapshot":
        raise SystemExit("unexpected snapshot format")

    init_db()
    conn = connect()
    try:
        if args.reset:
            conn.execute(
                "DELETE FROM sentence_breakdowns WHERE sentence_id IN "
                "(SELECT id FROM exam_sentences WHERE passage_id LIKE 'auto_%' "
                "OR passage_id LIKE 'bank_%' OR passage_id LIKE 'custom_%')"
            )
            conn.execute(
                "DELETE FROM exam_questions WHERE passage_id LIKE 'auto_%' "
                "OR passage_id LIKE 'bank_%' OR passage_id LIKE 'custom_%'"
            )
            conn.execute(
                "DELETE FROM exam_sentences WHERE passage_id LIKE 'auto_%' "
                "OR passage_id LIKE 'bank_%' OR passage_id LIKE 'custom_%'"
            )
            conn.execute(f"DELETE FROM exam_passages WHERE {IMPORTED_PASSAGE_WHERE}")

        for row in snapshot["passages"]:
            conn.execute(
                "INSERT OR REPLACE INTO exam_passages "
                "(id, year, exam_type, text_number, text, publication_status, revision, "
                "reviewed_by, reviewed_at, published_at, source_note) "
                "VALUES (?, ?, ?, ?, ?, 'draft', ?, '', '', '', ?)",
                (
                    row["id"],
                    row["year"],
                    row["exam_type"],
                    row["text_number"],
                    row["text"],
                    row.get("revision", 1),
                    row.get("source_note", ""),
                ),
            )
        for row in snapshot["sentences"]:
            conn.execute(
                "INSERT OR REPLACE INTO exam_sentences "
                "(id, passage_id, year, exam_type, text_number, paragraph, "
                "sentence_index, text, grammar_tags, source_label, char_start, char_end) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row["id"],
                    row["passage_id"],
                    row["year"],
                    row["exam_type"],
                    row["text_number"],
                    row["paragraph"],
                    row["sentence_index"],
                    row["text"],
                    row["grammar_tags"],
                    row["source_label"],
                    row.get("char_start"),
                    row.get("char_end"),
                ),
            )
        for row in snapshot["questions"]:
            conn.execute(
                "INSERT OR REPLACE INTO exam_questions "
                "(id, passage_id, year, exam_type, text_number, number, "
                "question_type, content, options_json, correct_answer, "
                "analysis_json, steps_json, source_sentence_id, answer_source, "
                "answer_source_note, review_status, source_quote, location_status, evidence_note) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)",
                (
                    row["id"],
                    row["passage_id"],
                    row["year"],
                    row["exam_type"],
                    row["text_number"],
                    row["number"],
                    row["question_type"],
                    row["content"],
                    row["options_json"],
                    row["correct_answer"],
                    row["analysis_json"],
                    row["steps_json"],
                    row["source_sentence_id"],
                    row.get("answer_source", "unknown"),
                    row.get("answer_source_note", ""),
                    row.get("source_quote", ""),
                    row.get("location_status", "unverified"),
                    row.get("evidence_note", ""),
                ),
            )
        for row in snapshot.get("breakdowns", []):
            conn.execute(
                "INSERT OR REPLACE INTO sentence_breakdowns "
                "(sentence_id, data_json, llm_used, created_at) VALUES (?, ?, ?, ?)",
                (row["sentence_id"], row["data_json"], row["llm_used"], row["created_at"]),
            )
        conn.commit()

        counts = {
            "passages": conn.execute(
                f"SELECT COUNT(*) FROM exam_passages WHERE {IMPORTED_PASSAGE_WHERE}"
            ).fetchone()[0],
            "sentences": conn.execute(
                "SELECT COUNT(*) FROM exam_sentences WHERE passage_id LIKE 'auto_%' "
                "OR passage_id LIKE 'bank_%' OR passage_id LIKE 'custom_%'"
            ).fetchone()[0],
            "questions": conn.execute(
                "SELECT COUNT(*) FROM exam_questions WHERE passage_id LIKE 'auto_%' "
                "OR passage_id LIKE 'bank_%' OR passage_id LIKE 'custom_%'"
            ).fetchone()[0],
            "breakdowns": conn.execute(
                "SELECT COUNT(*) FROM sentence_breakdowns"
            ).fetchone()[0],
        }
        print(f"loaded {args.snapshot} -> {DB_PATH}")
        print(counts)
        print("restored content is draft/pending and must be reviewed and published again")
        if counts != snapshot["counts"]:
            print("warning: loaded counts differ from snapshot counts")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
