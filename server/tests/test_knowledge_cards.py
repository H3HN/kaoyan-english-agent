"""Trap method cards and learner profile contract tests."""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db import SCHEMA, migrate_schema
from knowledge_cards import get_learner_profile, get_trap_card, list_trap_cards


class KnowledgeCardTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.addCleanup(self.conn.close)

    def test_eight_trap_cards_and_lookup(self):
        cards = list_trap_cards()
        self.assertEqual(len(cards), 8)
        card = get_trap_card("无中生有")
        self.assertIsNotNone(card)
        self.assertTrue(card["steps"])
        self.assertTrue(card["signals"])

    def test_learner_profile_derives_weakest_trap(self):
        for trap in ("无中生有", "无中生有", "正反混淆"):
            self.conn.execute(
                "INSERT INTO practice_records "
                "(question_id, question_type, user_answer, correct_answer, is_correct, trap_type) "
                "VALUES ('q', '细节题', 'A', 'B', 0, ?)",
                (trap,),
            )
        self.conn.execute(
            "INSERT INTO practice_records "
            "(question_id, question_type, user_answer, correct_answer, is_correct, trap_type) "
            "VALUES ('q2', '细节题', 'A', 'A', 1, '正确')"
        )
        self.conn.commit()
        profile = get_learner_profile(self.conn)
        self.assertEqual(profile["total_attempts"], 4)
        self.assertEqual(profile["weakest_trap"], "无中生有")
        self.assertEqual(profile["trap_counts"]["无中生有"], 2)
        self.assertEqual(profile["weakest_trap_card"]["name"], "无中生有")


if __name__ == "__main__":
    unittest.main()
