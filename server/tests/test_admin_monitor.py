"""Admin monitor tests: agent runs, practice analytics, breakdown and wordbook."""
import os
import sqlite3
import unittest
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient

import app as api
from db import SCHEMA, migrate_schema

TOKEN = "test-admin-token"
HEADERS = {"X-Admin-Token": TOKEN}


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    migrate_schema(conn)
    conn.commit()
    return conn


def seed_monitor(conn: sqlite3.Connection) -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)
    conn.executemany(
        "INSERT INTO agent_runs (workflow, input_json, output_json, tool_trace_json,"
        " created_at) VALUES (?, '{}', '{}', '[]', ?)",
        [
            ("chat", f"{today.isoformat()}T09:00:00"),
            ("sentence", f"{today.isoformat()}T10:00:00"),
            ("sentence", f"{yesterday.isoformat()}T10:00:00"),
        ],
    )
    conn.executemany(
        "INSERT INTO practice_records (question_id, question_type, user_answer,"
        " correct_answer, is_correct, trap_type, created_at)"
        " VALUES (?, ?, 'B', 'A', ?, ?, ?)",
        [
            ("q1", "细节题", 1, None, f"{today.isoformat()}T08:00:00"),
            ("q2", "细节题", 0, "偷换概念", f"{today.isoformat()}T08:30:00"),
            ("q3", "推理题", 1, None, f"{yesterday.isoformat()}T08:00:00"),
        ],
    )
    conn.execute(
        "INSERT INTO exam_passages (id, year, exam_type, text_number, text,"
        " publication_status) VALUES ('p1', 2018, '英语一', 1, 'text', 'published')"
    )
    conn.execute(
        "INSERT INTO exam_sentences (id, passage_id, year, exam_type, text_number,"
        " paragraph, sentence_index, text, source_label)"
        " VALUES ('s1', 'p1', 2018, '英语一', 1, 1, 1, 'A sentence.', 'label')"
    )
    conn.execute(
        "INSERT INTO sentence_breakdowns (sentence_id, data_json, llm_used)"
        " VALUES ('s1', '{}', 0)"
    )
    conn.execute(
        "INSERT INTO user_vocab_book (spelling, meaning, next_review)"
        " VALUES ('abandon', '放弃', ?)",
        (f"{yesterday.isoformat()}T00:00:00",),
    )
    conn.commit()


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.previous_token = os.environ.get("ADMIN_TOKEN")
        os.environ["ADMIN_TOKEN"] = TOKEN
        self.addCleanup(self._restore_token)
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        seed_monitor(self.conn)

        def override():
            yield self.conn

        api.app.dependency_overrides[api.get_db] = override
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    def _restore_token(self):
        if self.previous_token is None:
            os.environ.pop("ADMIN_TOKEN", None)
        else:
            os.environ["ADMIN_TOKEN"] = self.previous_token

    def test_requires_admin_token(self):
        self.assertEqual(self.client.get("/api/admin/monitor").status_code, 401)

    def test_monitor_aggregates_runs(self):
        payload = self.client.get("/api/admin/monitor", headers=HEADERS).json()
        self.assertEqual(payload["days"], 7)
        self.assertEqual(payload["runs"]["total"], 3)
        self.assertEqual(
            payload["runs"]["by_workflow"][0], {"workflow": "sentence", "count": 2}
        )
        self.assertEqual(len(payload["runs"]["daily"]), 7)
        self.assertEqual(payload["runs"]["daily"][-1]["count"], 2)
        self.assertEqual(payload["runs"]["daily"][-2]["count"], 1)

    def test_monitor_aggregates_practice(self):
        payload = self.client.get("/api/admin/monitor", headers=HEADERS).json()
        practice = payload["practice"]
        self.assertEqual(practice["total"], 3)
        self.assertEqual(practice["correct"], 2)
        self.assertEqual(practice["accuracy"], 0.67)
        detail = next(
            item for item in practice["by_type"] if item["type"] == "细节题"
        )
        self.assertEqual(detail["total"], 2)
        self.assertEqual(detail["correct"], 1)
        self.assertEqual(detail["accuracy"], 0.5)
        self.assertEqual(len(practice["daily"]), 7)
        self.assertEqual(practice["daily"][-1]["count"], 2)

    def test_monitor_breakdowns_and_wordbook(self):
        payload = self.client.get("/api/admin/monitor", headers=HEADERS).json()
        self.assertEqual(payload["breakdowns"]["total"], 1)
        self.assertEqual(payload["breakdowns"]["llm_used"], 0)
        self.assertEqual(payload["breakdowns"]["llm_ratio"], 0)
        self.assertEqual(payload["wordbook"]["total"], 1)
        self.assertEqual(payload["wordbook"]["due"], 1)

    def test_monitor_empty_database_returns_zeroes(self):
        empty = make_conn()
        self.addCleanup(empty.close)

        def override():
            yield empty

        api.app.dependency_overrides[api.get_db] = override
        payload = self.client.get("/api/admin/monitor", headers=HEADERS).json()
        self.assertEqual(payload["runs"]["total"], 0)
        self.assertEqual(payload["practice"]["accuracy"], 0)
        self.assertEqual(payload["breakdowns"]["llm_ratio"], 0)
        self.assertEqual(len(payload["practice"]["daily"]), 7)


if __name__ == "__main__":
    unittest.main()