"""P0 goal/session and P1 SM-2/quiz regression tests, in-memory only."""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db import SCHEMA, migrate_schema
from learner import get_goal, save_goal, save_reading_session
from tools import review_word
from vocab_quiz import build_quiz


class P0P1Tests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.addCleanup(self.conn.close)

    def add_word(self, spelling="novel", meaning="n. 小说", context="The novel is new."):
        self.conn.execute(
            "INSERT INTO user_vocab_book "
            "(spelling, meaning, context, source, is_outline, next_review) "
            "VALUES (?, ?, ?, 'test', 1, datetime('now'))",
            (spelling, meaning, context),
        )
        self.conn.commit()

    def test_goal_and_reading_session_persist(self):
        self.assertIsNone(get_goal(self.conn))
        goal = save_goal(
            self.conn,
            target_score=75,
            exam_date="2026-12-20",
            daily_minutes=45,
            current_level="六级",
        )
        self.assertEqual(goal["target_score"], 75)
        self.assertEqual(goal["daily_minutes"], 45)
        session = save_reading_session(
            self.conn,
            passage_id="p1",
            started_at="2026-10-29T10:00:00",
            duration_seconds=600,
            answered=5,
            correct=3,
        )
        self.assertEqual(session["answered"], 5)
        self.assertEqual(session["accuracy"], 0.6)

    def test_sm2_quality_updates_interval_and_writes_event(self):
        self.add_word()
        first = review_word(self.conn, "novel", quality=5)
        self.assertEqual(first["reviewCount"], 1)
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM vocab_review_events").fetchone()[0],
            1,
        )
        second = review_word(self.conn, "novel", quality=5)
        self.assertGreater(second["reviewCount"], first["reviewCount"])
        event = self.conn.execute(
            "SELECT quality, interval_days FROM vocab_review_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(event["quality"], 5)
        self.assertGreaterEqual(event["interval_days"], 1)

    def test_quiz_modes_are_generated_from_real_words(self):
        self.add_word("novel", "n. 小说", "The novel is new.")
        self.add_word("hollow", "adj. 空洞的", "The hollow lives.")
        for mode in ("choice", "spelling", "listening", "context"):
            items = build_quiz(self.conn, limit=2, mode=mode)
            self.assertTrue(items)
            self.assertEqual(items[0]["mode"], mode)
            self.assertTrue(items[0]["answer"])


if __name__ == "__main__":
    unittest.main()
