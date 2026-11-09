"""Task C: deterministic chat pipeline coverage (>= 8 scenarios).

Fixtures are synthetic; no network, no real exam text, no model key.
"""
import json
import sqlite3
import unittest
from unittest.mock import patch

from db import SCHEMA, migrate_schema
from question_bank import import_batch, transition
from workflows import run_chat_workflow


def document():
    passage = (
        "Alpha beta gamma delta epsilon zeta. Reliable feedback helps learners "
        "understand their mistakes and improve faster."
    )
    questions = []
    for number in range(21, 26):
        questions.append(
            {
                "number": number,
                "question_type": "细节题",
                "content": f"What does the author suggest in question {number}?",
                "options": {key: f"Option {key}" for key in "ABCD"},
                "correct_answer": "A",
                "answer_source": "provided",
                "answer_source_note": "Synthetic fixture key",
                "source_quote": "Alpha beta gamma delta epsilon zeta."
                if number == 21
                else "",
                "evidence_note": ""
                if number == 21
                else "Synthetic whole-passage evidence note",
            }
        )
    return {
        "format": "kaoyan-question-bank-v1",
        "passages": [
            {
                "year": 2025,
                "exam_type": "英语一",
                "text_number": 1,
                "source_note": "Synthetic fixture, not a real examination",
                "paragraphs": [passage],
                "questions": questions,
            }
        ],
    }


def make_conn(published=True):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    migrate_schema(conn)
    conn.commit()
    if published:
        result = import_batch(conn, document(), "tester")
        assert result["ok"], result
        passage_id = result["results"][0]["passage_id"]
        transition(conn, passage_id, 1, "publish-practice", "opener")
        conn.execute(
            "INSERT OR IGNORE INTO syllabus_vocabulary"
            " (word, basic_meaning, rare_meaning, exam_frequency, level)"
            " VALUES ('accountability', '责任；问责', NULL, 1, '核心')"
        )
        conn.commit()
    return conn


class ChatWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()
        self.addCleanup(self.conn.close)
        self.passage_id = self.conn.execute(
            "SELECT id FROM exam_passages WHERE publication_status='published'"
        ).fetchone()[0]

    def rows(self, workflow):
        return [
            dict(row)
            for row in self.conn.execute(
                "SELECT * FROM agent_runs WHERE workflow=?", (workflow,)
            )
        ]

    def test_capability_message_returns_sections_without_llm(self):
        result = run_chat_workflow(self.conn, "你能做什么", context_id="")
        self.assertTrue(result["sections"])
        self.assertFalse(result["llm_used"])
        self.assertIn("可以调用的工具", [item["title"] for item in result["sections"]])

    def test_sentence_intent_uses_context_and_traces_tools(self):
        result = run_chat_workflow(
            self.conn, "解析这个句子的从句", context_id=self.passage_id
        )
        self.assertTrue(result["tool_trace"])
        self.assertTrue(result["citations"])
        self.assertFalse(result["llm_used"])
        rows = self.rows("sentence")
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0]["input_json"])["source"], "chat")

    def test_options_intent_uses_context_and_traces_tools(self):
        result = run_chat_workflow(
            self.conn, "分析这道题的选项和陷阱", context_id=self.passage_id
        )
        tools = [item["tool"] for item in result["tool_trace"]]
        self.assertIn("record_trap_mistake", tools)
        self.assertTrue(result["citations"])
        self.assertEqual(len(self.rows("options")), 1)

    def test_add_word_is_deterministic_and_written(self):
        result = run_chat_workflow(
            self.conn, "把 accountability 加入单词本", context_id=self.passage_id
        )
        tools = [item["tool"] for item in result["tool_trace"]]
        self.assertIn("add_to_vocab_book", tools)
        self.assertFalse(result["llm_used"])
        count = self.conn.execute(
            "SELECT COUNT(*) FROM user_vocab_book WHERE spelling='accountability'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_no_model_key_falls_back_to_deterministic_sections(self):
        with patch("workflows.is_configured", return_value=False):
            result = run_chat_workflow(
                self.conn, "帮我安排复习计划", context_id=self.passage_id
            )
        self.assertFalse(result["llm_used"])
        self.assertTrue(result["sections"])
        self.assertIn("今天", [item["title"] for item in result["sections"]])

    def test_invalid_context_id_degrades_without_exception(self):
        result = run_chat_workflow(
            self.conn, "你能做什么", context_id="missing-passage-id"
        )
        self.assertTrue(result["sections"])
        self.assertFalse(result["llm_used"])

    def test_chat_logs_direct_source(self):
        run_chat_workflow(self.conn, "你能做什么", context_id="")
        rows = self.rows("chat")
        self.assertEqual(len(rows), 1)
        logged = json.loads(rows[0]["input_json"])
        self.assertEqual(logged["source"], "direct")
        output = json.loads(rows[0]["output_json"])
        self.assertIn("tools", output)

    def test_repeated_add_word_is_idempotent(self):
        message = "把 accountability 加入单词本"
        run_chat_workflow(self.conn, message, context_id=self.passage_id)
        run_chat_workflow(self.conn, message, context_id=self.passage_id)
        count = self.conn.execute(
            "SELECT COUNT(*) FROM user_vocab_book WHERE spelling='accountability'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_empty_database_is_graceful(self):
        empty = make_conn(published=False)
        self.addCleanup(empty.close)
        with patch("workflows.is_configured", return_value=False):
            result = run_chat_workflow(empty, "你能做什么", context_id="")
        self.assertFalse(result["llm_used"])
        self.assertIn("当前没有已发布的真题篇章", result["intro"])

    def test_unknown_intent_returns_capability_sections(self):
        result = run_chat_workflow(
            self.conn, "给我讲个笑话", context_id=self.passage_id
        )
        self.assertTrue(result["sections"])
        self.assertFalse(result["llm_used"])


if __name__ == "__main__":
    unittest.main()
