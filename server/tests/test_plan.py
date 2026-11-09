"""Tests for deterministic study plans and proactive insights.

The planner is rule-based: these tests pin the scheduling rules, idempotency
and the /api/plan + /api/insights contracts without network or app.db access.
"""
import sqlite3
import unittest
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient

import app as api
from db import SCHEMA, migrate_schema
from plan import (
    generate_plan,
    get_insights,
    get_or_create_settings,
    get_plan,
    mark_item_done,
    update_settings,
)


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    migrate_schema(conn)
    conn.commit()
    return conn


def add_practice(conn, question_id, qtype, correct, created_at, trap=None):
    conn.execute(
        "INSERT INTO practice_records (question_id, question_type, user_answer,"
        " correct_answer, is_correct, trap_type, created_at)"
        " VALUES (?, ?, 'B', 'A', ?, ?, ?)",
        (question_id, qtype, 1 if correct else 0, trap, created_at),
    )


def add_due_word(conn, spelling, next_review):
    conn.execute(
        "INSERT INTO user_vocab_book (spelling, meaning, next_review)"
        " VALUES (?, '测试释义', ?)",
        (spelling, next_review),
    )


def add_published_question(conn, passage_id, question_id, year=2025, text_number=1):
    conn.execute(
        "INSERT OR IGNORE INTO exam_passages (id, year, exam_type, text_number,"
        " text, publication_status) VALUES (?, ?, '英语一', ?, 'synthetic text',"
        " 'published')",
        (passage_id, year, text_number),
    )
    conn.execute(
        "INSERT OR IGNORE INTO exam_questions (id, passage_id, year, exam_type,"
        " text_number, number, question_type, content, options_json,"
        " correct_answer, analysis_json, steps_json)"
        " VALUES (?, ?, ?, '英语一', ?, 21, '细节题', 'synthetic question',"
        " '{}', 'A', '{}', '[]')",
        (question_id, passage_id, year, text_number),
    )


class PlanSchedulingTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        today = date.today()
        stamp = f"{today.isoformat()}T09:00:00"
        add_practice(self.conn, "q-detail-1", "细节题", False, stamp, "偷换概念")
        add_practice(self.conn, "q-detail-2", "细节题", False, stamp, "偷换概念")
        add_practice(self.conn, "q-reason-1", "推理题", True, stamp)
        add_due_word(self.conn, "abandon", f"{(today - timedelta(days=1)).isoformat()}T00:00:00")
        add_published_question(self.conn, "p-2025-t1", "q-2025-21", 2025, 1)
        add_published_question(self.conn, "p-2024-t2", "q-2024-22", 2024, 2)
        self.conn.commit()
        self.today = today

    def test_generate_builds_a_week_from_current_state(self):
        result = generate_plan(self.conn)
        self.assertEqual(result["created_dates"], 7)
        self.assertEqual(len(result["days"]), 7)
        self.assertTrue(result["days"][0]["is_today"])
        task_types = {item["task_type"] for item in result["items"]}
        self.assertEqual(
            task_types,
            {"vocab_review", "weak_type_practice", "exam_practice"},
        )
        weak_items = [
            item for item in result["items"] if item["task_type"] == "weak_type_practice"
        ]
        self.assertTrue(all("细节题" in item["title"] for item in weak_items))
        self.assertGreater(result["summary"]["total"], 0)
        self.assertEqual(result["summary"]["done"], 0)

    def test_generate_is_idempotent(self):
        first = generate_plan(self.conn)
        second = generate_plan(self.conn)
        self.assertEqual(second["created_dates"], 0)
        self.assertEqual(second["summary"]["total"], first["summary"]["total"])

    def test_force_regenerates_pending_and_keeps_done(self):
        first = generate_plan(self.conn)
        created_before = first["summary"]["total"]
        first_item = first["items"][0]
        mark_item_done(self.conn, first_item["id"], True)
        result = generate_plan(self.conn, force=True)
        self.assertGreaterEqual(result["created_dates"], 1)
        done_items = [item for item in result["items"] if item["status"] == "done"]
        self.assertIn(first_item["id"], {item["id"] for item in done_items})
        self.assertGreater(result["summary"]["total"], created_before)

    def test_mark_item_done_updates_summary(self):
        plan = generate_plan(self.conn)
        target = plan["items"][0]
        updated = mark_item_done(self.conn, target["id"], True)
        self.assertEqual(updated["status"], "done")
        refreshed = get_plan(self.conn)
        self.assertEqual(refreshed["summary"]["done"], 1)
        undone = mark_item_done(self.conn, target["id"], False)
        self.assertEqual(undone["status"], "pending")

    def test_mark_missing_item_returns_none(self):
        self.assertIsNone(mark_item_done(self.conn, 999999, True))

    def test_week_offset_moves_window(self):
        current = get_plan(self.conn, 0)
        next_week = get_plan(self.conn, 1)
        self.assertEqual(
            next_week["days"][0]["date"],
            (self.today + timedelta(days=7)).isoformat(),
        )
        self.assertNotEqual(current["days"][0]["date"], next_week["days"][0]["date"])

    def test_fallback_task_when_nothing_else_to_do(self):
        empty = make_conn()
        self.addCleanup(empty.close)
        result = generate_plan(empty)
        task_types = {item["task_type"] for item in result["items"]}
        self.assertEqual(task_types, {"sentence_practice"})


class PlanInsightsTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        today = date.today()
        add_practice(
            self.conn, "q-detail-1", "细节题", False,
            f"{today.isoformat()}T09:00:00", "偷换概念",
        )
        add_due_word(self.conn, "abandon", f"{(today - timedelta(days=1)).isoformat()}T00:00:00")
        self.conn.commit()
        self.today = today

    def test_insights_reflect_today_state(self):
        generate_plan(self.conn)
        insights = get_insights(self.conn)
        self.assertEqual(insights["due_word_count"], 1)
        self.assertEqual(insights["weakest_type"]["type"], "细节题")
        self.assertEqual(insights["streak_days"], 1)
        self.assertEqual(insights["idle_days"], 0)
        self.assertTrue(insights["plan_ready"])
        self.assertGreater(len(insights["today_tasks"]), 0)
        self.assertIsInstance(insights["suggestions"], list)

    def test_exam_countdown_from_settings(self):
        future = (self.today + timedelta(days=30)).isoformat()
        update_settings(self.conn, exam_date=future, daily_minutes=90, target_score=80)
        insights = get_insights(self.conn)
        self.assertEqual(insights["exam_countdown"], 30)
        self.assertTrue(any("30" in text for text in insights["suggestions"]))

    def test_idle_suggestion_after_gap(self):
        idle_conn = make_conn()
        self.addCleanup(idle_conn.close)
        old = (self.today - timedelta(days=5)).isoformat()
        add_practice(idle_conn, "q-old", "细节题", True, f"{old}T09:00:00")
        insights = get_insights(idle_conn)
        self.assertEqual(insights["idle_days"], 5)
        self.assertEqual(insights["streak_days"], 0)
        self.assertTrue(any("没有练习" in text for text in insights["suggestions"]))


class PlanSettingsTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)

    def test_defaults_are_created_on_demand(self):
        settings = get_or_create_settings(self.conn)
        self.assertEqual(settings, {"exam_date": "", "daily_minutes": 60, "target_score": 70})
        self.assertEqual(get_or_create_settings(self.conn), settings)

    def test_update_and_invalid_date(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        updated = update_settings(self.conn, tomorrow, 120, 85)
        self.assertEqual(updated["exam_date"], tomorrow)
        self.assertEqual(updated["daily_minutes"], 120)
        self.assertEqual(updated["target_score"], 85)
        with self.assertRaises(ValueError):
            update_settings(self.conn, "2026/12/31")


class PlanApiTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        today = date.today()
        add_practice(
            self.conn, "q-detail-1", "细节题", False,
            f"{today.isoformat()}T09:00:00", "偷换概念",
        )
        self.conn.commit()

        def override():
            yield self.conn

        api.app.dependency_overrides[api.get_db] = override
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    def test_plan_endpoints_roundtrip(self):
        generated = self.client.post("/api/plan/generate").json()
        self.assertGreater(generated["summary"]["total"], 0)
        plan = self.client.get("/api/plan").json()
        self.assertEqual(plan["summary"]["total"], generated["summary"]["total"])
        item_id = plan["items"][0]["id"]
        done = self.client.post(
            f"/api/plan/items/{item_id}/done", json={"done": True}
        ).json()
        self.assertEqual(done["status"], "done")
        missing = self.client.post("/api/plan/items/999999/done", json={"done": True})
        self.assertEqual(missing.status_code, 404)

    def test_insights_and_settings_endpoints(self):
        insights = self.client.get("/api/insights").json()
        self.assertIn("greeting", insights)
        self.assertEqual(insights["weakest_type"]["type"], "细节题")
        settings = self.client.get("/api/plan/settings").json()
        self.assertEqual(settings["daily_minutes"], 60)
        updated = self.client.put(
            "/api/plan/settings",
            json={"exam_date": "", "daily_minutes": 90, "target_score": 75},
        ).json()
        self.assertEqual(updated["daily_minutes"], 90)
        invalid = self.client.put(
            "/api/plan/settings",
            json={"exam_date": "2026/12/31", "daily_minutes": 90, "target_score": 75},
        )
        self.assertEqual(invalid.status_code, 422)


if __name__ == "__main__":
    unittest.main()