"""Evidence relocation tests: deterministic binding, audit, and idempotence.

Synthetic fixtures only; no real exam content, no network, no app.db.
"""
import json
import sqlite3
import unittest

from db import SCHEMA, migrate_schema
from evidence_locator import relocate_all, relocate_passage, reliable_sentence_offsets
from question_bank import import_batch


PASSAGE_PARAGRAPHS = [
    "Alpha beta gamma delta epsilon zeta. Reliable feedback helps learners understand mistakes.",
    "Another paragraph contains repeated words for testing. Reliable feedback helps learners understand mistakes.",
]


def document():
    questions = [
        {"number": 21, "question_type": "细节题", "content": "Unique sentence question?",
         "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "A",
         "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
         "source_quote": "Alpha beta gamma delta epsilon zeta.", "evidence_note": ""},
        {"number": 22, "question_type": "细节题", "content": "Repeated quote question?",
         "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "B",
         "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
         "source_quote": "Reliable feedback helps learners understand mistakes.", "evidence_note": ""},
        {"number": 23, "question_type": "主旨题", "content": "Spanning quote question?",
         "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "C",
         "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
         "source_quote": "Alpha beta gamma delta epsilon zeta. Reliable feedback helps learners understand mistakes.",
         "evidence_note": "Whole-paragraph fixture evidence"},
        {"number": 24, "question_type": "细节题", "content": "Missing quote question?",
         "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "D",
         "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
         "source_quote": "", "evidence_note": ""},
        {"number": 25, "question_type": "细节题", "content": "Short quote question?",
         "options": {k: f"Option {k}" for k in "ABCD"}, "correct_answer": "A",
         "answer_source": "provided", "answer_source_note": "Synthetic fixture key",
         "source_quote": "too short", "evidence_note": ""},
    ]
    return {"format": "kaoyan-question-bank-v1", "passages": [{
        "year": 2025, "exam_type": "英语一", "text_number": 1,
        "source_note": "Synthetic fixture, not a real examination",
        "paragraphs": PASSAGE_PARAGRAPHS, "questions": questions}]}


class EvidenceLocatorTests(unittest.TestCase):
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
        self.pid = result["results"][0]["passage_id"]

    def reset_to_unverified(self):
        """Simulate the snapshot-restored state: everything unverified, no binding."""
        self.conn.execute(
            "UPDATE exam_questions SET location_status='unverified', source_sentence_id=NULL")
        self.conn.commit()

    def question(self, number):
        return dict(self.conn.execute(
            "SELECT * FROM exam_questions WHERE number=?", (number,)).fetchone())

    def sentence_ids(self):
        return [r["id"] for r in self.conn.execute(
            "SELECT id FROM exam_sentences ORDER BY paragraph, sentence_index")]

    def test_reliable_sentence_offsets_excludes_repeated_and_short(self):
        passage = "\n\n".join(PASSAGE_PARAGRAPHS)
        rows = [{"id": sid, "text": text} for sid, text in zip(
            ["s1", "s2", "s3", "s4", "s5"],
            ["Alpha beta gamma delta epsilon zeta.",
             "Reliable feedback helps learners understand mistakes.",
             "Another paragraph contains repeated words for testing.",
             "Reliable feedback helps learners understand mistakes.",
             "x"])]
        reliable = reliable_sentence_offsets(passage, rows)
        self.assertEqual([r["id"] for r in reliable], ["s1", "s3"])
        for row in reliable:
            self.assertIn(passage[row["char_start"]:row["char_end"]], passage)
            self.assertGreater(row["char_end"], row["char_start"])

    def test_relocation_statuses_and_bindings(self):
        self.reset_to_unverified()
        summary = relocate_all(self.conn, "locator", dry_run=False)
        self.assertEqual(summary["passages"], 1)
        self.assertEqual(summary["questions"], 5)
        # q21 unique quote inside one reliable sentence -> bound
        q21 = self.question(21)
        self.assertEqual(q21["location_status"], "exact_quote")
        self.assertEqual(q21["source_sentence_id"], self.sentence_ids()[0])
        # q22 quote occurs twice -> ambiguous, no binding
        q22 = self.question(22)
        self.assertEqual(q22["location_status"], "ambiguous")
        self.assertIsNone(q22["source_sentence_id"])
        # q23 quote spans two sentences -> multi_sentence, no binding
        q23 = self.question(23)
        self.assertEqual(q23["location_status"], "multi_sentence")
        self.assertIsNone(q23["source_sentence_id"])
        # q24 missing quote -> pending
        self.assertEqual(self.question(24)["location_status"], "pending")
        # q25 short quote -> pending
        self.assertEqual(self.question(25)["location_status"], "pending")
        self.assertEqual(summary["bound"], 1)

    def test_idempotent_after_bank_import(self):
        # import_batch already located quotes; re-running must change nothing
        summary = relocate_all(self.conn, "locator", dry_run=False)
        self.assertEqual(summary["changed_questions"], 0)
        self.assertEqual(self.question(21)["location_status"], "exact_quote")

    def test_idempotent_on_second_run(self):
        self.reset_to_unverified()
        first = relocate_all(self.conn, "locator", dry_run=False)
        self.assertEqual(first["changed_questions"], 5)
        second = relocate_all(self.conn, "locator", dry_run=False)
        self.assertEqual(second["changed_questions"], 0)
        self.assertEqual(second["bound"], 1)

    def test_dry_run_writes_nothing(self):
        self.reset_to_unverified()
        before = self.question(21)
        summary = relocate_all(self.conn, "locator", dry_run=True)
        after = self.question(21)
        self.assertEqual(after["location_status"], before["location_status"])
        self.assertEqual(after["source_sentence_id"], before["source_sentence_id"])
        self.assertEqual(summary["bound"], 1)
        events = self.conn.execute(
            "SELECT COUNT(*) FROM bank_events WHERE action='evidence_located'").fetchone()[0]
        self.assertEqual(events, 0)

    def test_publication_and_review_state_untouched(self):
        from question_bank import transition
        transition(self.conn, self.pid, 1, "publish-practice", "opener")
        state_before = dict(self.conn.execute(
            "SELECT publication_status, revision, reviewed_by, published_at "
            "FROM exam_passages WHERE id=?", (self.pid,)).fetchone())
        review_before = self.question(21)["review_status"]
        relocate_all(self.conn, "locator", dry_run=False)
        state_after = dict(self.conn.execute(
            "SELECT publication_status, revision, reviewed_by, published_at "
            "FROM exam_passages WHERE id=?", (self.pid,)).fetchone())
        self.assertEqual(state_before, state_after)
        self.assertEqual(self.question(21)["review_status"], review_before)

    def test_audit_event_recorded_with_before_after(self):
        self.reset_to_unverified()
        relocate_all(self.conn, "locator", dry_run=False)
        rows = self.conn.execute(
            "SELECT * FROM bank_events WHERE action='evidence_located' AND passage_id=?",
            (self.pid,)).fetchall()
        self.assertEqual(len(rows), 1)
        snap = json.loads(rows[0]["snapshot_json"])
        self.assertEqual(snap["counts"]["total"], 5)
        self.assertEqual(len(snap["updates"]), 5)
        update21 = next(u for u in snap["updates"] if u["number"] == 21)
        self.assertEqual(update21["old_status"], "unverified")
        self.assertEqual(update21["new_status"], "exact_quote")

    def test_null_sentence_offsets_backfilled_only_when_unique(self):
        self.conn.execute("UPDATE exam_sentences SET char_start=NULL, char_end=NULL")
        self.conn.commit()
        self.reset_to_unverified()
        relocate_all(self.conn, "locator", dry_run=False)
        rows = {r["id"]: dict(r) for r in self.conn.execute("SELECT * FROM exam_sentences")}
        sids = self.sentence_ids()
        self.assertIsNotNone(rows[sids[0]]["char_start"])   # unique sentence backfilled
        self.assertIsNone(rows[sids[1]]["char_start"])     # repeated sentence stays NULL
        self.assertIsNone(rows[sids[3]]["char_start"])     # repeated sentence stays NULL
        self.assertIsNotNone(rows[sids[2]]["char_start"])  # unique sentence backfilled
        # binding still works with offsets previously NULL (auto-style passages)
        self.assertEqual(self.question(21)["location_status"], "exact_quote")

    def test_selected_passages_and_missing_passage(self):
        from evidence_locator import LocationError
        self.reset_to_unverified()
        summary = relocate_all(self.conn, "locator", passage_ids=[self.pid])
        self.assertEqual(summary["passages"], 1)
        with self.assertRaises(LocationError):
            relocate_passage(self.conn, "bank_9999_1_1")


if __name__ == "__main__":
    unittest.main()