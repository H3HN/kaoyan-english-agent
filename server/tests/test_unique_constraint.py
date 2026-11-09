"""Task A: one exam passage per (year, exam_type, text_number) slot.

The fixture starts from a schema without the table-level UNIQUE constraint,
mimicking an existing local database, then runs the production migration.
"""
import sqlite3
import unittest

from db import SCHEMA, migrate_schema


def legacy_schema() -> str:
    marker = "    source_note TEXT NOT NULL DEFAULT '',\n    UNIQUE(year, exam_type, text_number)\n);"
    replacement = "    source_note TEXT NOT NULL DEFAULT ''\n);"
    schema = SCHEMA.replace(marker, replacement)
    if schema == SCHEMA:
        raise AssertionError("could not build legacy schema without the slot UNIQUE")
    return schema


def connect_legacy():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(legacy_schema())
    conn.commit()
    return conn


def add_passage(conn, passage_id, published=False):
    conn.execute(
        "INSERT INTO exam_passages (id, year, exam_type, text_number, text,"
        " publication_status, revision, source_note)"
        " VALUES (?, 2023, '英语一', 1, 'Synthetic passage text.', ?, 1, '')",
        (passage_id, "published" if published else "draft"),
    )
    conn.execute(
        "INSERT INTO exam_sentences (id, passage_id, year, exam_type, text_number,"
        " paragraph, sentence_index, text, grammar_tags, source_label)"
        " VALUES (?, ?, 2023, '英语一', 1, 1, 1, 'Synthetic sentence.', '[]', '测试')",
        (f"{passage_id}_s1", passage_id),
    )
    conn.execute(
        "INSERT INTO exam_questions (id, passage_id, year, exam_type, text_number,"
        " number, question_type, content, options_json, correct_answer,"
        " analysis_json, steps_json, source_sentence_id)"
        " VALUES (?, ?, 2023, '英语一', 1, 21, '细节题', 'Synthetic question?',"
        " '{}', 'A', '{}', '[]', ?)",
        (f"{passage_id}_q21", passage_id, f"{passage_id}_s1"),
    )


def duplicate_groups(conn):
    return conn.execute(
        "SELECT year, exam_type, text_number, COUNT(*) c FROM exam_passages"
        " GROUP BY year, exam_type, text_number HAVING c > 1"
    ).fetchall()


class UniquePassageSlotTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect_legacy()
        self.addCleanup(self.conn.close)

    def test_migration_removes_legacy_draft_and_is_idempotent(self):
        add_passage(self.conn, "auto_2023", published=True)
        add_passage(self.conn, "2023_en1_t1", published=False)
        self.conn.execute(
            "INSERT INTO sentence_breakdowns (sentence_id, data_json, llm_used)"
            " VALUES ('2023_en1_t1_s1', '{}', 0)"
        )
        self.conn.execute(
            "INSERT INTO bank_events (passage_id, revision, action, actor,"
            " created_at, snapshot_json) VALUES ('2023_en1_t1', 1, 'import',"
            " 'tester', '2026-01-01', '{}')"
        )
        self.conn.commit()

        migrate_schema(self.conn)
        self.conn.commit()

        self.assertEqual(duplicate_groups(self.conn), [])
        ids = [
            row["id"]
            for row in self.conn.execute("SELECT id FROM exam_passages ORDER BY id")
        ]
        self.assertEqual(ids, ["auto_2023"])
        self.assertEqual(
            self.conn.execute(
                "SELECT COUNT(*) FROM exam_sentences WHERE passage_id='2023_en1_t1'"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            self.conn.execute(
                "SELECT COUNT(*) FROM bank_events WHERE passage_id='2023_en1_t1'"
            ).fetchone()[0],
            0,
        )
        index = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
            " AND name='ux_exam_passages_slot'"
        ).fetchone()
        self.assertIsNotNone(index)

        # Running the same migration twice must be a no-op.
        migrate_schema(self.conn)
        self.conn.commit()
        self.assertEqual(duplicate_groups(self.conn), [])

    def test_duplicate_insert_is_rejected_after_migration(self):
        migrate_schema(self.conn)
        self.conn.commit()
        add_passage(self.conn, "auto_2023", published=True)
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO exam_passages (id, year, exam_type, text_number, text)"
                " VALUES ('duplicate', 2023, '英语一', 1, 'x')"
            )

    def test_draft_with_practice_records_blocks_cleanup(self):
        add_passage(self.conn, "auto_2023", published=True)
        add_passage(self.conn, "draft_with_history", published=False)
        self.conn.execute(
            "INSERT INTO practice_records (question_id, question_type, user_answer,"
            " correct_answer, is_correct, trap_type)"
            " VALUES ('draft_with_history_q21', '细节题', 'B', 'A', 0, '偷换概念')"
        )
        self.conn.commit()
        with self.assertRaises(RuntimeError):
            migrate_schema(self.conn)

    def test_fresh_schema_enforces_unique_slot(self):
        fresh = sqlite3.connect(":memory:")
        fresh.executescript(SCHEMA)
        fresh.execute(
            "INSERT INTO exam_passages (id, year, exam_type, text_number, text)"
            " VALUES ('a', 2024, '英语一', 1, 'x')"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            fresh.execute(
                "INSERT INTO exam_passages (id, year, exam_type, text_number, text)"
                " VALUES ('b', 2024, '英语一', 1, 'y')"
            )
        fresh.close()


if __name__ == "__main__":
    unittest.main()
