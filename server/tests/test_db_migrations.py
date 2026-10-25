"""Regression tests use temporary databases/snapshots, never server/data/app.db."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

SERVER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER))
import db
import seed


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SERVER / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


load_demo = load_script("load_demo")
export_demo = load_script("export_demo")
PASSAGE_DEFAULTS = {
    "publication_status": "draft", "revision": 1, "reviewed_by": "",
    "reviewed_at": "", "published_at": "", "source_note": "",
}
QUESTION_DEFAULTS = {
    "answer_source": "unknown", "answer_source_note": "",
    "review_status": "pending", "source_quote": "", "location_status": "unverified",
    "evidence_note": "",
}
LEGACY_SCHEMA = """
CREATE TABLE exam_passages (
 id TEXT PRIMARY KEY, year INTEGER NOT NULL, exam_type TEXT NOT NULL,
 text_number INTEGER NOT NULL, text TEXT NOT NULL);
CREATE TABLE exam_sentences (
 id TEXT PRIMARY KEY, passage_id TEXT NOT NULL REFERENCES exam_passages(id),
 year INTEGER NOT NULL, exam_type TEXT NOT NULL, text_number INTEGER NOT NULL,
 paragraph INTEGER NOT NULL DEFAULT 1, sentence_index INTEGER NOT NULL,
 text TEXT NOT NULL, grammar_tags TEXT NOT NULL DEFAULT '[]', source_label TEXT NOT NULL);
CREATE TABLE exam_questions (
 id TEXT PRIMARY KEY, passage_id TEXT NOT NULL REFERENCES exam_passages(id),
 year INTEGER NOT NULL, exam_type TEXT NOT NULL, text_number INTEGER NOT NULL,
 number INTEGER NOT NULL, question_type TEXT NOT NULL, content TEXT NOT NULL,
 options_json TEXT NOT NULL, correct_answer TEXT NOT NULL, analysis_json TEXT NOT NULL,
 steps_json TEXT NOT NULL, source_sentence_id TEXT REFERENCES exam_sentences(id));
CREATE TABLE sentence_breakdowns (
 sentence_id TEXT PRIMARY KEY REFERENCES exam_sentences(id), data_json TEXT NOT NULL,
 llm_used INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
"""


def snapshot(metadata=False, prefix="auto_"):
    passage = dict(id=f"{prefix}test", year=2024, exam_type="english1", text_number=1,
                   text="前言。中😀文 sentence.")
    sentence = dict(id=f"{prefix}sentence", passage_id=passage["id"], year=2024,
                    exam_type="english1", text_number=1, paragraph=1,
                    sentence_index=1, text="中😀文 sentence.", grammar_tags="[]",
                    source_label="test")
    question = dict(id=f"{prefix}question", passage_id=passage["id"], year=2024,
                    exam_type="english1", text_number=1, number=21,
                    question_type="reading", content="question", options_json="[]",
                    correct_answer="B", analysis_json="{}", steps_json="[]",
                    source_sentence_id=sentence["id"])
    if metadata:
        passage.update(publication_status="published", revision=7, reviewed_by="reviewer",
                       reviewed_at="2025-01-02T03:04:05", published_at="2025-01-03T03:04:05",
                       source_note="official source p1")
        sentence.update(char_start=3, char_end=len(passage["text"]))
        question.update(answer_source="official", answer_source_note="answer key p2",
                        review_status="reviewed", source_quote=sentence["text"],
                        location_status="verified", evidence_note="cross-sentence evidence")
    return dict(format="kaoyan-demo-snapshot", version=1,
                counts=dict(passages=1, sentences=1, questions=1, breakdowns=0),
                passages=[passage], sentences=[sentence], questions=[question], breakdowns=[])


def insert_legacy(conn):
    data = snapshot()
    for table, key in (("exam_passages", "passages"), ("exam_sentences", "sentences"),
                       ("exam_questions", "questions")):
        row = data[key][0]
        conn.execute(f"INSERT INTO {table} ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
                     tuple(row.values()))
    conn.commit()


class NonClosingConnection:
    """Let command entry points close their handle while tests inspect the DB."""
    def __init__(self, conn):
        object.__setattr__(self, "conn", conn)

    def __getattr__(self, name):
        return getattr(self.conn, name)

    def __setattr__(self, name, value):
        setattr(self.conn, name, value)

    def close(self):
        pass


class MigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="migration-", dir=SERVER / "tests")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "test.db"

    def connect(self, legacy=False):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(LEGACY_SCHEMA if legacy else db.SCHEMA)
        self.addCleanup(conn.close)
        return conn

    def test_new_schema_has_correct_types_nullability_defaults_and_audit_table(self):
        conn = self.connect()
        insert_legacy(conn)
        passage = dict(conn.execute("SELECT * FROM exam_passages").fetchone())
        sentence = dict(conn.execute("SELECT * FROM exam_sentences").fetchone())
        question = dict(conn.execute("SELECT * FROM exam_questions").fetchone())
        self.assertEqual({key: passage[key] for key in PASSAGE_DEFAULTS}, PASSAGE_DEFAULTS)
        self.assertIsNone(sentence["char_start"])
        self.assertIsNone(sentence["char_end"])
        for table, names in (("exam_passages", PASSAGE_DEFAULTS),
                             ("exam_sentences", ["char_start", "char_end"]),
                             ("exam_questions", QUESTION_DEFAULTS)):
            columns = {row[1]: row for row in conn.execute(f"PRAGMA table_info({table})")}
            for name in names:
                expected_type = "INTEGER" if name in {"revision", "char_start", "char_end"} else "TEXT"
                self.assertEqual(columns[name][2], expected_type)
        self.assertEqual({key: question[key] for key in QUESTION_DEFAULTS}, QUESTION_DEFAULTS)
        self.assertEqual(
            {row[1] for row in conn.execute("PRAGMA table_info(bank_events)")},
            {"id", "passage_id", "revision", "action", "actor", "created_at", "snapshot_json"},
        )

    def test_legacy_migration_is_idempotent_and_preserves_answers_locations_and_defaults(self):
        conn = self.connect(legacy=True)
        insert_legacy(conn)
        db.migrate_schema(conn)
        db.migrate_schema(conn)
        passage = dict(conn.execute("SELECT * FROM exam_passages").fetchone())
        question = dict(conn.execute("SELECT * FROM exam_questions").fetchone())
        self.assertEqual(question["correct_answer"], "B")
        self.assertEqual(question["source_sentence_id"], "auto_sentence")
        self.assertEqual({key: passage[key] for key in PASSAGE_DEFAULTS}, PASSAGE_DEFAULTS)
        self.assertEqual({key: question[key] for key in QUESTION_DEFAULTS}, QUESTION_DEFAULTS)
        conn.execute("UPDATE exam_passages SET publication_status='published', revision=3, source_note='source'")
        conn.execute("UPDATE exam_questions SET answer_source='official', review_status='reviewed', location_status='verified', evidence_note='evidence'")
        conn.execute("UPDATE exam_sentences SET char_start=3, char_end=16")
        db.migrate_schema(conn)
        self.assertEqual(tuple(conn.execute("SELECT publication_status, revision, source_note FROM exam_passages").fetchone()),
                         ("published", 3, "source"))
        self.assertEqual(tuple(conn.execute("SELECT answer_source, review_status, location_status, evidence_note FROM exam_questions").fetchone()),
                         ("official", "reviewed", "verified", "evidence"))
        self.assertEqual(tuple(conn.execute("SELECT char_start, char_end FROM exam_sentences").fetchone()), (3, 16))

    def test_init_migrates_before_seed_and_can_repeat(self):
        conn = self.connect(legacy=True)

        def assert_migrated(actual):
            actual.execute("SELECT publication_status, revision, source_note FROM exam_passages")
            actual.execute("SELECT char_start, char_end FROM exam_sentences")
            actual.execute("SELECT answer_source, review_status, location_status, evidence_note FROM exam_questions")

        with patch.object(db, "connect", return_value=NonClosingConnection(conn)), \
                patch.object(seed, "seed_database", side_effect=assert_migrated) as seed_mock:
            db.init_db()
            db.init_db()
        self.assertEqual(seed_mock.call_count, 2)

    def roundtrip(self, metadata, prefix="auto_"):
        source = snapshot(metadata, prefix)
        input_path = self.root / "input.json"
        output_path = self.root / "output.json"
        input_path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
        with patch.object(db, "DATA_DIR", self.root), patch.object(db, "DB_PATH", self.path), \
                patch.object(seed, "seed_database"), patch.object(load_demo, "DB_PATH", self.path), \
                patch.object(sys, "argv", ["load_demo.py", "--snapshot", str(input_path)]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(load_demo.main(), 0)
        with patch.object(export_demo, "DB_PATH", self.path), patch.object(export_demo, "OUT_PATH", output_path), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(export_demo.main(), 0)
        result = json.loads(output_path.read_text(encoding="utf-8"))
        passage, question, sentence = result["passages"][0], result["questions"][0], result["sentences"][0]
        self.assertEqual(passage["publication_status"], "draft")
        self.assertEqual(passage["reviewed_by"], "")
        self.assertEqual(passage["reviewed_at"], "")
        self.assertEqual(passage["published_at"], "")
        self.assertEqual(passage["revision"], source["passages"][0].get("revision", 1))
        self.assertEqual(passage["source_note"], source["passages"][0].get("source_note", ""))
        for field, default in QUESTION_DEFAULTS.items():
            expected = "pending" if field == "review_status" else source["questions"][0].get(field, default)
            self.assertEqual(question[field], expected)
        for field in ("char_start", "char_end"):
            self.assertEqual(sentence[field], source["sentences"][0].get(field))
        self.assertEqual(question["correct_answer"], "B")
        self.assertEqual(question["source_sentence_id"], source["sentences"][0]["id"])
        self.assertEqual(result["counts"], source["counts"])
        if metadata:
            text = passage["text"]
            self.assertEqual(text[sentence["char_start"]:sentence["char_end"]], sentence["text"])

    def test_old_snapshot_uses_conservative_defaults(self):
        self.roundtrip(False)

    def test_new_snapshot_preserves_content_metadata_but_resets_review_state(self):
        self.roundtrip(True)

    def test_bank_and_custom_prefixes_roundtrip(self):
        self.roundtrip(True, "bank_")
        self.path.unlink()
        self.roundtrip(True, "custom_")

    def test_export_legacy_database_without_mutating_schema(self):
        conn = self.connect(legacy=True)
        insert_legacy(conn)
        output_path = self.root / "legacy.json"
        self.path.touch()
        with patch.object(export_demo, "DB_PATH", self.path), patch.object(export_demo, "OUT_PATH", output_path), \
                patch.object(export_demo.sqlite3, "connect", return_value=NonClosingConnection(conn)), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(export_demo.main(), 0)
        result = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual({key: result["passages"][0][key] for key in PASSAGE_DEFAULTS}, PASSAGE_DEFAULTS)
        self.assertEqual({key: result["questions"][0][key] for key in QUESTION_DEFAULTS}, QUESTION_DEFAULTS)
        self.assertIsNone(result["sentences"][0]["char_start"])
        self.assertNotIn("publication_status", {row[1] for row in conn.execute("PRAGMA table_info(exam_passages)")})
        self.assertNotIn("char_start", {row[1] for row in conn.execute("PRAGMA table_info(exam_sentences)")})


if __name__ == "__main__":
    unittest.main()
