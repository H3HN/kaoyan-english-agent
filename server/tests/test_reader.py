"""Extensive-reading source pipeline contract tests."""
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db import SCHEMA, migrate_schema
from reader import get_source, import_source, list_sources, publish_source


class ReaderPipelineTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        migrate_schema(self.conn)
        self.addCleanup(self.conn.close)

    def test_draft_then_publish_and_read(self):
        text = ("The Great Gatsby is a novel about the American Dream. " * 10).strip()
        source = import_source(
            self.conn,
            title="The Great Gatsby",
            text=text,
            source_url="https://example.com/gatsby",
            license="user-provided",
        )
        self.assertEqual(source["status"], "draft")
        self.assertGreater(source["word_count"], 50)
        self.assertEqual(len(list_sources(self.conn, "draft")), 1)
        self.assertEqual(len(list_sources(self.conn, "published")), 0)
        published = publish_source(self.conn, source["id"])
        self.assertEqual(published["status"], "published")
        self.assertTrue(published["published_at"])
        full = get_source(self.conn, source["id"])
        self.assertIn("American Dream", full["text"])

    def test_short_import_is_rejected(self):
        with self.assertRaises(ValueError):
            import_source(self.conn, title="x", text="too short")


if __name__ == "__main__":
    unittest.main()
