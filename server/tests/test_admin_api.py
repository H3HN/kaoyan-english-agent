"""B-end content console tests: admin token gate + workbench state machine."""
import os
import sqlite3
import unittest

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


def document(year=2025, exam_type="英语一", text_number=2, source_note="Synthetic fixture, not a real examination"):
    first_number = 20 + (text_number - 1) * 5 + 1
    questions = []
    for offset in range(5):
        number = first_number + offset
        questions.append(
            {
                "number": number,
                "question_type": "细节题",
                "content": f"What does the author say about feedback ({number})?",
                "options": {
                    "A": "It improves learning.",
                    "B": "It wastes time.",
                    "C": "It is optional.",
                    "D": "It is rare.",
                },
                "correct_answer": "A",
                "answer_source": "provided",
                "answer_source_note": "Synthetic fixture key",
                "source_quote": "Reliable feedback helps learners improve.",
                "analysis": {
                    key: {
                        "trapType": "正确" if key == "A" else "无关干扰",
                        "explanation": "Synthetic fixture explanation.",
                    }
                    for key in "ABCD"
                },
                "steps": ["定位反馈句", "比对选项", "排除无关项"],
            }
        )
    return {
        "format": "kaoyan-question-bank-v1",
        "passages": [
            {
                "year": year,
                "exam_type": exam_type,
                "text_number": text_number,
                "source_note": source_note,
                "paragraphs": [
                    "Reliable feedback helps learners improve. "
                    "Good feedback highlights the gap between effort and outcome."
                ],
                "questions": questions,
            }
        ],
    }


class AdminTestBase(unittest.TestCase):
    def setUp(self):
        self.previous_token = os.environ.get("ADMIN_TOKEN")
        os.environ["ADMIN_TOKEN"] = TOKEN
        self.addCleanup(self._restore_token)

        self.conn = make_conn()
        self.addCleanup(self.conn.close)

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

    def import_passage(self, **kwargs) -> str:
        response = self.client.post(
            "/api/admin/passages/import",
            json={"document": document(**kwargs), "actor": "测试管理员"},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertTrue(payload["ok"], payload)
        return payload["results"][0]["passage_id"]

    def transition(self, passage_id: str, action: str):
        return self.client.post(
            f"/api/admin/passages/{passage_id}/transition",
            json={"action": action, "actor": "测试管理员"},
            headers=HEADERS,
        )


class AdminAuthTests(AdminTestBase):
    def test_missing_token_is_rejected(self):
        self.assertEqual(self.client.get("/api/admin/stats").status_code, 401)

    def test_wrong_token_is_rejected(self):
        response = self.client.get(
            "/api/admin/stats", headers={"X-Admin-Token": "wrong-token"}
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_token_unlocks_console(self):
        response = self.client.get("/api/admin/stats", headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 0)


class WorkbenchTests(AdminTestBase):
    def test_import_creates_draft_and_updates_stats(self):
        passage_id = self.import_passage()
        stats = self.client.get("/api/admin/stats", headers=HEADERS).json()
        self.assertEqual(stats["draft"], 1)
        self.assertEqual(stats["published"], 0)
        self.assertEqual(stats["question_total"], 5)
        listing = self.client.get("/api/admin/passages", headers=HEADERS).json()
        self.assertEqual(listing["total"], 1)
        item = listing["items"][0]
        self.assertEqual(item["id"], passage_id)
        self.assertEqual(item["publication_status"], "draft")
        self.assertEqual(item["status_label"], "草稿")
        self.assertEqual(item["question_count"], 5)

    def test_review_then_publish(self):
        passage_id = self.import_passage()
        reviewed = self.transition(passage_id, "review")
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        self.assertEqual(reviewed.json()["publication_status"], "reviewed")

        published = self.transition(passage_id, "publish")
        self.assertEqual(published.status_code, 200, published.text)
        self.assertEqual(published.json()["publication_status"], "published")

        stats = self.client.get("/api/admin/stats", headers=HEADERS).json()
        self.assertEqual(stats["published"], 1)
        self.assertEqual(stats["draft"], 0)

    def test_publish_practice_straight_from_draft(self):
        passage_id = self.import_passage()
        response = self.transition(passage_id, "publish-practice")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["publication_status"], "published")

    def test_withdraw_returns_to_draft(self):
        passage_id = self.import_passage()
        self.transition(passage_id, "publish-practice")
        withdrawn = self.transition(passage_id, "withdraw")
        self.assertEqual(withdrawn.status_code, 200, withdrawn.text)
        self.assertEqual(withdrawn.json()["publication_status"], "draft")

    def test_unknown_action_is_rejected(self):
        passage_id = self.import_passage()
        response = self.transition(passage_id, "delete")
        self.assertEqual(response.status_code, 400)
        self.assertIn("未知状态操作", response.json()["detail"]["message"])

    def test_missing_passage_transition_is_rejected(self):
        response = self.transition("missing_passage", "review")
        self.assertEqual(response.status_code, 400)
        self.assertIn("不存在", response.json()["detail"]["message"])

    def test_events_are_recorded(self):
        passage_id = self.import_passage()
        self.transition(passage_id, "review")
        events = self.client.get(
            f"/api/admin/passages/{passage_id}/events", headers=HEADERS
        ).json()["items"]
        actions = [event["action"] for event in events]
        self.assertIn("imported", actions)
        self.assertIn("review", actions)
        self.assertTrue(all(event["actor"] == "测试管理员" for event in events))

    def test_detail_exposes_readiness(self):
        passage_id = self.import_passage()
        detail = self.client.get(
            f"/api/admin/passages/{passage_id}", headers=HEADERS
        ).json()
        self.assertEqual(detail["id"], passage_id)
        self.assertEqual(detail["entry"]["passage_id"], passage_id)
        self.assertIsInstance(detail["review_issues"], list)
        self.assertEqual(detail["review_issues"], [])

    def test_list_filters_and_pagination(self):
        self.import_passage(text_number=2)
        self.import_passage(text_number=3)
        published = self.import_passage(text_number=4)
        self.transition(published, "publish-practice")

        draft_list = self.client.get(
            "/api/admin/passages?status=draft", headers=HEADERS
        ).json()
        self.assertEqual(draft_list["total"], 2)
        published_list = self.client.get(
            "/api/admin/passages?status=published", headers=HEADERS
        ).json()
        self.assertEqual(published_list["total"], 1)

        first_page = self.client.get(
            "/api/admin/passages?page=1&page_size=1", headers=HEADERS
        ).json()
        self.assertEqual(len(first_page["items"]), 1)
        self.assertEqual(first_page["pages"], 3)

        keyword = self.client.get(
            "/api/admin/passages?q=2025", headers=HEADERS
        ).json()
        self.assertEqual(keyword["total"], 3)

    def test_student_surface_stays_published_only(self):
        passage_id = self.import_passage()
        before = self.client.get("/api/passages").json()["items"]
        self.assertEqual(before, [])

        self.transition(passage_id, "publish-practice")
        after = self.client.get("/api/passages").json()["items"]
        self.assertEqual(len(after), 1)
        self.assertEqual(after[0]["id"], passage_id)

    def test_import_validation_error_is_400(self):
        response = self.client.post(
            "/api/admin/passages/import",
            json={"document": {"format": "wrong-format", "passages": []}},
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("format", response.json()["detail"]["message"])


if __name__ == "__main__":
    unittest.main()