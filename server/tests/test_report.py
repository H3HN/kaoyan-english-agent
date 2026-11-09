"""Task B: report aggregation stays on the backend and gains chart/recent fields."""
import sqlite3
import unittest
from datetime import datetime, timedelta

from db import SCHEMA, migrate_schema
from tools import get_report


def make_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    migrate_schema(conn)
    conn.commit()
    return conn


def add_record(conn, question_id, qtype, correct, created_at, trap=None):
    conn.execute(
        "INSERT INTO practice_records (question_id, question_type, user_answer,"
        " correct_answer, is_correct, trap_type, created_at)"
        " VALUES (?, ?, 'B', 'A', ?, ?, ?)",
        (question_id, qtype, 1 if correct else 0, trap, created_at),
    )


class ReportAggregationTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        old = today - timedelta(days=3)
        add_record(self.conn, "q1", "细节题", True, f"{today.isoformat()}T09:00:00")
        add_record(self.conn, "q2", "细节题", False, f"{today.isoformat()}T10:00:00", "偷换概念")
        add_record(self.conn, "q3", "推理题", False, f"{yesterday.isoformat()}T10:00:00", "过度推理")
        add_record(self.conn, "q4", "主旨题", True, f"{old.isoformat()}T10:00:00")
        self.conn.commit()
        self.today = today
        self.yesterday = yesterday
        self.old = old

    def test_daily_counts_cover_seven_days_with_zero_fill(self):
        report = get_report(self.conn)
        self.assertEqual(len(report["daily_counts"]), 7)
        self.assertEqual(
            [item["date"] for item in report["daily_counts"]],
            [
                (self.today - timedelta(days=offset)).isoformat()
                for offset in range(6, -1, -1)
            ],
        )
        counts = {item["date"]: item["count"] for item in report["daily_counts"]}
        self.assertEqual(counts[self.today.isoformat()], 2)
        self.assertEqual(counts[self.yesterday.isoformat()], 1)
        self.assertEqual(counts[self.old.isoformat()], 1)
        self.assertEqual(sum(counts.values()), 4)

    def test_recent_records_shape_and_order(self):
        report = get_report(self.conn)
        recent = report["recent_records"]
        self.assertEqual(len(recent), 4)
        self.assertEqual(
            set(recent[0]),
            {
                "question_id",
                "question_type",
                "user_answer",
                "correct_answer",
                "is_correct",
                "created_at",
            },
        )
        self.assertEqual(recent[0]["question_id"], "q2")
        self.assertFalse(recent[0]["is_correct"])
        self.assertEqual(recent[0]["correct_answer"], "A")
        self.assertEqual(recent[0]["created_at"][:10], self.today.isoformat())
        self.assertTrue(recent[-1]["is_correct"])

    def test_existing_fields_are_unchanged(self):
        report = get_report(self.conn)
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["correct"], 2)
        self.assertEqual(report["accuracy"], 0.5)
        self.assertEqual(report["by_type"]["细节题"]["total"], 2)
        self.assertEqual(report["by_type"]["细节题"]["accuracy"], 0.5)
        self.assertIn("过度推理", report["trap_distribution"])
        self.assertIsInstance(report["suggestions"], list)


if __name__ == "__main__":
    unittest.main()
