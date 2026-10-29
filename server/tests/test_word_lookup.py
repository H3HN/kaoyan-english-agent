"""Word lookup: online fallback is required for words absent from the syllabus."""
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_core.tools.word import _word_insight
from db import SCHEMA, migrate_schema


class WordLookupTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.addCleanup(self.conn.close)

    @patch("agent_core.tools.word.lookup_word_online")
    def test_unknown_word_is_looked_up_online(self, lookup):
        lookup.return_value = {
            "found": True,
            "word": "Love",
            "phonetic": "/lʌv/",
            "part_of_speech": "n./v.",
            "basic_meanings": ["爱；爱情", "热爱"],
            "rare_meaning": "",
            "collocations": ["fall in love"],
            "examples": [{"en": "I love reading.", "zh": "我喜欢阅读。"}],
            "is_proper_noun": False,
        }
        result = _word_insight(self.conn, "Love")
        unit = result["client_actions"][0]["payload"]["unit"]
        data = unit["data"]
        self.assertEqual(data["level"], "在线查询")
        self.assertEqual(data["lookup_source"], "llm")
        self.assertIn("爱情", data["basic_meaning"])
        self.assertFalse(data["is_proper_noun"])
        self.assertTrue(result["llm_used"])
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM word_lookup_cache").fetchone()[0],
            1,
        )

    @patch("agent_core.tools.word.lookup_word_online")
    def test_failed_lookup_does_not_guess_proper_noun(self, lookup):
        lookup.return_value = None
        result = _word_insight(self.conn, "Love")
        data = result["client_actions"][0]["payload"]["unit"]["data"]
        self.assertEqual(data["level"], "未收录")
        self.assertEqual(data["lookup_source"], "none")
        self.assertNotIn("专有名词", data["basic_meaning"])
        self.assertFalse(result["llm_used"])

    @patch("agent_core.tools.word.lookup_word_online")
    def test_examples_use_word_boundaries_not_substrings(self, lookup):
        lookup.return_value = None
        self.conn.execute(
            "INSERT INTO exam_passages (id, year, exam_type, text_number, text, publication_status) "
            "VALUES ('p1', 2024, '英语一', 1, 'A passage.', 'published')"
        )
        for index, text in enumerate(
            (
                "The bee is important for flowers.",
                "He has been reading for two hours.",
                "A bee flies over the garden.",
            )
        ):
            self.conn.execute(
                "INSERT INTO exam_sentences "
                "(id, passage_id, year, exam_type, text_number, paragraph, sentence_index, text, source_label) "
                "VALUES (?, 'p1', 2024, '英语一', 1, 1, ?, ?, '2024 英语一 Text 1')",
                (f"s{index}", index, text),
            )
        self.conn.commit()
        result = _word_insight(self.conn, "bee")
        examples = result["client_actions"][0]["payload"]["unit"]["data"]["examples"]
        self.assertEqual(len(examples), 2)
        for item in examples:
            self.assertIn("bee", item["text"].lower())
            self.assertNotIn("been", item["text"].lower())

    @patch("agent_core.tools.word.lookup_word_online")
    def test_cached_lookup_avoids_second_online_call(self, lookup):
        lookup.return_value = {
            "found": True,
            "word": "serendipity",
            "phonetic": "",
            "part_of_speech": "n.",
            "basic_meanings": ["机缘巧合"],
            "rare_meaning": "",
            "collocations": [],
            "examples": [],
            "is_proper_noun": False,
        }
        _word_insight(self.conn, "serendipity")
        _word_insight(self.conn, "serendipity")
        self.assertEqual(lookup.call_count, 1)


if __name__ == "__main__":
    unittest.main()
