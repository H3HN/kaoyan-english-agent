"""Tests for the 2026-11 backend optimizations:

- /api/questions/full: fixed-query assembly, filters, include_passage=false
- chat workflow: agent_runs logging with direct/chat attribution
- retired import routes keep their 410 contract without dead handlers

Synthetic fixtures only; no real exam content, no network, no app.db.
"""
import json
import sqlite3
import unittest

from fastapi.testclient import TestClient

import app as api
from db import SCHEMA, migrate_schema
from question_bank import import_batch, transition
from workflows import run_chat_workflow, run_options_workflow, run_sentence_workflow


def document(year=2025, exam_type="英语一", text_number=1):
    passage = "Alpha beta gamma delta epsilon zeta. Reliable feedback helps learners understand their mistakes and improve faster."
    questions = []
    for n in range(21, 26):
        questions.append({
            "number": n, "question_type": "细节题",
            "content": f"What does the author suggest in question {n}?",
            "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "A",
            "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
            "source_quote": "Alpha beta gamma delta epsilon zeta." if n == 21 else "",
            "evidence_note": "" if n == 21 else "Synthetic whole-passage evidence note",
        })
    return {"format": "kaoyan-question-bank-v1", "passages": [{
        "year": year, "exam_type": exam_type, "text_number": text_number,
        "source_note": "Synthetic fixture, not a real examination",
        "paragraphs": [passage], "questions": questions}]}


class FullQuestionsTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.conn.commit()
        self.addCleanup(self.conn.close)
        result = import_batch(self.conn, document(), "tester")
        self.assertTrue(result["ok"], result)
        transition(self.conn, result["results"][0]["passage_id"], 1, "publish-practice", "opener")
        def override():
            yield self.conn
        api.app.dependency_overrides[api.get_db] = override
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    def test_full_listing_shape_is_backward_compatible(self):
        items = self.client.get("/api/questions/full").json()["items"]
        self.assertEqual(len(items), 5)
        first = items[0]
        for key in ("id", "number", "questionType", "content", "options", "correctAnswer",
                    "analysis", "steps", "location", "sourceSentence", "sourceSentenceId",
                    "answerSource", "answerSourceNote", "reviewStatus", "locationStatus",
                    "sourceQuote", "sourceHighlights", "passage", "passageId", "year",
                    "examType", "textNumber"):
            self.assertIn(key, first)
        # practice-published questions carry no analysis (same as before)
        self.assertEqual(first["analysis"], {})
        # passage body present by default (legacy behavior)
        self.assertIn("Alpha beta gamma", first["passage"])
        # only q21 has exact_quote evidence; others show the manual-pending marker
        bound = [item for item in items if item["locationStatus"] == "exact_quote"]
        self.assertEqual(len(bound), 1)
        self.assertIn("第1段第1句", bound[0]["location"])
        unbound = [item for item in items if item["locationStatus"] != "exact_quote"]
        self.assertTrue(all(item["sourceSentenceId"] is None for item in unbound))
        self.assertTrue(all(item["sourceSentence"] == "" for item in unbound))

    def test_include_passage_false_omits_bodies(self):
        items = self.client.get("/api/questions/full",
                                params={"include_passage": "false"}).json()["items"]
        self.assertEqual(len(items), 5)
        self.assertTrue(all(item["passage"] == "" for item in items))
        # metadata survives so the reading-train cascade still works
        self.assertTrue(all(item["year"] == 2025 for item in items))

    def test_year_exam_text_filters_return_single_passage(self):
        items = self.client.get("/api/questions/full", params={
            "year": 2025, "exam_type": "英语一", "text_number": 1,
        }).json()["items"]
        self.assertEqual(len(items), 5)
        self.assertEqual([item["number"] for item in items], [21, 22, 23, 24, 25])
        self.assertIn("Alpha beta gamma", items[0]["passage"])

    def test_filter_with_no_match_returns_empty(self):
        items = self.client.get("/api/questions/full", params={"year": 2019}).json()["items"]
        self.assertEqual(items, [])

    def test_invalid_filter_values_are_rejected(self):
        self.assertEqual(
            self.client.get("/api/questions/full", params={"year": 1999}).status_code, 422)
        self.assertEqual(
            self.client.get("/api/questions/full", params={"text_number": 9}).status_code, 422)


class ChatLoggingTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.conn.commit()
        self.addCleanup(self.conn.close)
        result = import_batch(self.conn, document(), "tester")
        self.assertTrue(result["ok"], result)
        pid = result["results"][0]["passage_id"]
        transition(self.conn, pid, 1, "publish-practice", "opener")

    def agent_rows(self, workflow=None):
        sql = "SELECT workflow, input_json, output_json, tool_trace_json FROM agent_runs"
        params = ()
        if workflow:
            sql += " WHERE workflow=?"
            params = (workflow,)
        return [dict(r) for r in self.conn.execute(sql, params)]

    def test_chat_workflow_logs_agent_runs(self):
        result = run_chat_workflow(self.conn, "解析这个句子的从句", context_id="bank_2025_1_1")
        self.assertIn("sections", result)
        rows = self.agent_rows("chat")
        self.assertEqual(len(rows), 1)
        logged_input = json.loads(rows[0]["input_json"])
        logged_output = json.loads(rows[0]["output_json"])
        self.assertEqual(logged_input["source"], "direct")
        self.assertEqual(logged_input["context_id"], "bank_2025_1_1")
        self.assertIn("message", logged_input)
        self.assertIn("section_count", logged_output)
        self.assertIn("tools", logged_output)

    def test_chat_forwarded_workflows_are_attributed_to_chat(self):
        run_chat_workflow(self.conn, "解析这个句子的从句", context_id="bank_2025_1_1")
        sentence_rows = self.agent_rows("sentence")
        options_rows = self.agent_rows("options")
        self.assertEqual(len(sentence_rows), 1)
        self.assertEqual(json.loads(sentence_rows[0]["input_json"])["source"], "chat")
        self.assertEqual(len(options_rows), 0)

    def test_direct_workflow_calls_log_as_direct(self):
        sid = self.conn.execute("SELECT id FROM exam_sentences LIMIT 1").fetchone()[0]
        run_sentence_workflow(self.conn, sid)
        rows = self.agent_rows("sentence")
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0]["input_json"])["source"], "direct")
        # legacy input fields stay at the top level alongside source
        self.assertEqual(json.loads(rows[0]["input_json"])["sentence_id"], sid)

    def test_chat_without_context_still_logs(self):
        run_chat_workflow(self.conn, "你能做什么", context_id="")
        rows = self.agent_rows("chat")
        self.assertEqual(len(rows), 1)
        self.assertFalse(json.loads(rows[0]["output_json"])["llm_used"])


class RetiredRoutesTests(unittest.TestCase):
    def test_import_routes_return_410_without_dead_handlers(self):
        client = TestClient(api.app)
        self.addCleanup(client.close)
        self.assertEqual(client.post("/api/exams/import", json={}).status_code, 410)
        self.assertEqual(client.post("/api/exams/auto-import", json={}).status_code, 410)
        self.assertEqual(client.get("/api/agent/runs").status_code, 410)


if __name__ == "__main__":
    unittest.main()