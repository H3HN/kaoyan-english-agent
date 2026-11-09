"""Knowledge-base admin tests: vocabulary CRUD, citations, trap rules."""
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


def seed_knowledge(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO syllabus_vocabulary "
        "(word, phonetic, basic_meaning, rare_meaning, exam_frequency, level, enabled) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("address", "/əˈdres/", "n. 地址；演讲", "v. 处理，应对", 18, "高频", 1),
            ("plant", "/plɑːnt/", "n. 植物", "n. 工厂", 12, "高频", 1),
            ("obsolete", "", "adj. 过时的", "", 2, "基础", 0),
        ],
    )
    conn.execute(
        "INSERT INTO exam_passages (id, year, exam_type, text_number, text,"
        " publication_status) VALUES ('p1', 2018, '英语一', 1,"
        " 'The report must address the concern raised by local teams.', 'published')"
    )
    conn.execute(
        "INSERT INTO exam_sentences (id, passage_id, year, exam_type, text_number,"
        " paragraph, sentence_index, text, source_label)"
        " VALUES ('s1', 'p1', 2018, '英语一', 1, 1, 1,"
        " 'The report must address the concern raised by local teams.',"
        " '2018 英语一 Text 1 · 第1段第1句')"
    )
    conn.execute(
        "INSERT INTO exam_questions (id, passage_id, year, exam_type, text_number,"
        " number, question_type, content, options_json, correct_answer,"
        " analysis_json, steps_json, source_sentence_id)"
        " VALUES ('q1', 'p1', 2018, '英语一', 1, 21, '细节题', 'q', '{}', 'A',"
        " '{}', '[]', 's1')"
    )
    conn.execute(
        "INSERT INTO trap_rules (name, definition, signals, example, tone)"
        " VALUES ('偷换概念', '把原文概念替换为相近但不同的说法', '选项与原文关键词近义不同',"
        " '原文说 early，选项说 first', 'red')"
    )
    conn.commit()


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.previous_token = os.environ.get("ADMIN_TOKEN")
        os.environ["ADMIN_TOKEN"] = TOKEN
        self.addCleanup(self._restore_token)
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        seed_knowledge(self.conn)

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
        self.assertEqual(self.client.get("/api/admin/vocab").status_code, 401)

    def test_vocab_list_filters_and_stats(self):
        payload = self.client.get("/api/admin/vocab", headers=HEADERS).json()
        self.assertEqual(payload["total"], 3)
        self.assertEqual(payload["stats"], {"total": 3, "enabled": 2, "disabled": 1})
        self.assertEqual(payload["items"][0]["word"], "address")

        by_level = self.client.get(
            "/api/admin/vocab?level=高频", headers=HEADERS
        ).json()
        self.assertEqual(by_level["total"], 2)
        by_enabled = self.client.get(
            "/api/admin/vocab?enabled=0", headers=HEADERS
        ).json()
        self.assertEqual(by_enabled["total"], 1)
        self.assertEqual(by_enabled["items"][0]["word"], "obsolete")
        by_keyword = self.client.get(
            "/api/admin/vocab?keyword=addr", headers=HEADERS
        ).json()
        self.assertEqual(by_keyword["total"], 1)

    def test_vocab_detail_includes_citations(self):
        detail = self.client.get("/api/admin/vocab/address", headers=HEADERS).json()
        self.assertEqual(detail["word"], "address")
        self.assertEqual(detail["phonetic"], "/əˈdres/")
        self.assertEqual(len(detail["citations"]), 1)
        citation = detail["citations"][0]
        self.assertEqual(citation["sentence_id"], "s1")
        self.assertEqual(citation["question_type"], "细节题")
        self.assertIn("address", citation["text"])

    def test_vocab_detail_missing_is_404(self):
        response = self.client.get("/api/admin/vocab/missing", headers=HEADERS)
        self.assertEqual(response.status_code, 404)

    def test_create_vocab_entry(self):
        response = self.client.post(
            "/api/admin/vocab",
            json={
                "word": "sound",
                "phonetic": "/saʊnd/",
                "basic_meaning": "n. 声音；v. 听起来",
                "rare_meaning": "adj. 健全的",
                "exam_frequency": 15,
                "level": "高频",
                "enabled": True,
            },
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["word"], "sound")
        listing = self.client.get("/api/admin/vocab", headers=HEADERS).json()
        self.assertEqual(listing["stats"]["total"], 4)

    def test_create_vocab_rejects_duplicate_and_blank(self):
        duplicate = self.client.post(
            "/api/admin/vocab",
            json={"word": "Address", "basic_meaning": "重复"},
            headers=HEADERS,
        )
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("已存在", duplicate.json()["detail"]["message"])

        blank = self.client.post(
            "/api/admin/vocab",
            json={"word": "newly", "basic_meaning": ""},
            headers=HEADERS,
        )
        self.assertEqual(blank.status_code, 400)
        self.assertIn("基本释义", blank.json()["detail"]["message"])

    def test_update_vocab_entry(self):
        response = self.client.put(
            "/api/admin/vocab/plant",
            json={
                "word": "ignored-spelling",
                "phonetic": "/plænt/",
                "basic_meaning": "n. 植物；工厂",
                "rare_meaning": "v. 栽种；安放",
                "exam_frequency": 13,
                "level": "核心",
                "enabled": True,
            },
            headers=HEADERS,
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["word"], "plant")
        self.assertEqual(data["basic_meaning"], "n. 植物；工厂")
        self.assertEqual(data["phonetic"], "/plænt/")
        self.assertEqual(data["exam_frequency"], 13)
        self.assertEqual(data["level"], "核心")

        missing = self.client.put(
            "/api/admin/vocab/missing",
            json={"word": "missing", "basic_meaning": "x"},
            headers=HEADERS,
        )
        self.assertEqual(missing.status_code, 400)

    def test_toggle_vocab_affects_student_surface(self):
        student_before = self.client.get("/api/vocab?q=plant").json()
        self.assertEqual(student_before["total"], 1)

        toggled = self.client.post(
            "/api/admin/vocab/plant/toggle", json={"enabled": False}, headers=HEADERS
        )
        self.assertEqual(toggled.status_code, 200, toggled.text)
        self.assertFalse(toggled.json()["enabled"])

        student_after = self.client.get("/api/vocab?q=plant").json()
        self.assertEqual(student_after["total"], 0)

        restored = self.client.post(
            "/api/admin/vocab/plant/toggle", json={"enabled": True}, headers=HEADERS
        )
        self.assertTrue(restored.json()["enabled"])
        self.assertEqual(
            self.client.get("/api/vocab?q=plant").json()["total"], 1
        )

    def test_trap_rules_list_create_update(self):
        listing = self.client.get("/api/admin/trap-rules", headers=HEADERS).json()
        self.assertEqual(len(listing["items"]), 1)

        created = self.client.post(
            "/api/admin/trap-rules",
            json={
                "name": "过度推理",
                "definition": "选项引入原文未给出的因果或结论",
                "signals": "must/always/therefore",
                "example": "原文只说相关，选项说导致",
                "tone": "amber",
            },
            headers=HEADERS,
        )
        self.assertEqual(created.status_code, 200, created.text)
        rule = created.json()
        self.assertEqual(rule["name"], "过度推理")

        updated = self.client.put(
            f"/api/admin/trap-rules/{rule['id']}",
            json={
                "name": "过度推理",
                "definition": "选项引入原文未给出的因果或结论（修订）",
                "signals": "must/always",
                "example": "示例",
                "tone": "red",
            },
            headers=HEADERS,
        )
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertIn("修订", updated.json()["definition"])

        duplicate = self.client.post(
            "/api/admin/trap-rules",
            json={"name": "过度推理", "definition": "重复"},
            headers=HEADERS,
        )
        self.assertEqual(duplicate.status_code, 400)


if __name__ == "__main__":
    unittest.main()