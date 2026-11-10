"""Audit regression tests: isolated files only; never restore or migrate a bank."""
import copy
import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from bank_audit import (RULE_VERSION, attach_history, audit_database,
                        audit_snapshot, markdown_report)
from scripts.audit_question_bank import main


def snapshot():
    text = "A synthetic passage for an audit test."
    p = {"id": "p1", "year": 2025, "exam_type": "英语一", "text_number": 1,
         "text": text, "publication_status": "published", "source_note": "Synthetic fixture",
         "reviewed_by": "fixture reviewer"}
    s = {"id": "s1", "passage_id": "p1", "year": 2025, "exam_type": "英语一", "text_number": 1,
         "paragraph": 1, "sentence_index": 1, "text": text, "char_start": 0, "char_end": len(text)}
    questions = []
    for n in range(21, 26):
        questions.append({"id": f"q{n}", "passage_id": "p1", "year": 2025, "exam_type": "英语一", "text_number": 1,
                          "number": n, "content": "Synthetic question?", "options_json": json.dumps({k: "Option " + k for k in "ABCD"}),
                          "correct_answer": "A", "analysis_json": '{"A":"Synthetic reasoning"}', "steps_json": '["Compare"]',
                          "source_sentence_id": "s1", "answer_source": "provided", "review_status": "approved",
                          "source_quote": text, "location_status": "exact_quote"})
    return {"format": "kaoyan-demo-snapshot", "passages": [p], "sentences": [s], "questions": questions, "breakdowns": []}


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "snapshot.json"

    def put(self, data=None):
        self.path.write_text(json.dumps(data if data is not None else snapshot(), ensure_ascii=False), encoding="utf-8")
        return self.path

    def audit(self, data=None):
        return audit_snapshot(self.put(data))

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = main(list(map(str, args)))
        return result, out.getvalue(), err.getvalue()

    def test_reproducible_provenance_and_no_approval(self):
        path = self.put()
        before = path.read_bytes()
        a, b = audit_snapshot(path), audit_snapshot(path)
        self.assertEqual(a["summary"]["deterministic_issue_count"], 0)
        self.assertEqual(a["summary"]["published_passages"], 1)
        self.assertEqual(a["coverage"]["review_status"], {"approved": 5})
        self.assertEqual(a["provenance"]["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(a["provenance"]["rule_version"], RULE_VERSION)
        self.assertTrue(a["provenance"]["code_revision"])
        self.assertTrue(a["provenance"]["code_sha256"])
        self.assertIn("not approval", markdown_report(a))
        for r in (a, b):
            r["provenance"].pop("timestamp")
        self.assertEqual(a, b)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(a["human_review_items"]), 6)

    def test_stable_ids_values_diff_and_annotation_never_suppress(self):
        data = snapshot()
        data["questions"][0]["correct_answer"] = "Z"
        previous = self.audit(data)
        first = next(i for i in previous["deterministic_issues"] if i["kind"] == "invalid_answer")
        data["questions"][0]["correct_answer"] = "Y"
        current = self.audit(data)
        issue = next(i for i in current["deterministic_issues"] if i["kind"] == "invalid_answer")
        self.assertEqual(first["issue_id"], issue["issue_id"])
        attach_history(current, previous, {"issues": {issue["issue_id"]: {"state": "resolved", "reviewer": "Alice", "note": "Needs source check"}}})
        self.assertIn(issue["issue_id"], current["diff"]["persistent"])
        self.assertEqual(current["summary"]["deterministic_issue_count"], 1)
        self.assertEqual(issue["triage"]["state"], "resolved")
        fixed = self.audit()
        attach_history(fixed, previous)
        self.assertIn(issue["issue_id"], fixed["diff"]["resolved"])
        changed = self.audit(data)
        attach_history(changed, fixed)
        self.assertIn(issue["issue_id"], changed["diff"]["new"])

    def test_triage_validation_and_previous_validation(self):
        report = self.audit()
        iid = report["human_review_items"][0]["issue_id"]
        for bad in ({"issues": {"unknown": {"state": "open", "reviewer": "a", "note": ""}}},
                    {"issues": {iid: {"state": "approved", "reviewer": "a", "note": ""}}},
                    {"issues": {iid: {"state": "open", "reviewer": "", "note": ""}}},
                    {"issues": {iid: {"state": "open", "reviewer": "a"}}}, []):
            with self.subTest(triage=bad), self.assertRaises(ValueError):
                attach_history(copy.deepcopy(report), triage=bad)
        with self.assertRaises(ValueError):
            attach_history(report, {})
        old = copy.deepcopy(report)
        old["provenance"]["rule_version"] = "future"
        with self.assertRaises(ValueError):
            attach_history(report, old)

    def test_malformed_refs_options_ids_offsets_original_numbers(self):
        data = snapshot()
        data["questions"][0].update(passage_id="missing", source_sentence_id="missing", options_json='{"A":"x"}', number=1)
        data["questions"][1]["analysis_json"] = "garbled"
        data["questions"][1]["steps_json"] = "garbled"
        data["questions"].append(copy.deepcopy(data["questions"][1]))
        data["sentences"][0]["char_end"] = True
        data["breakdowns"] = [{"sentence_id": "absent", "data_json": "{}"}]
        report = self.audit(data)
        kinds = {i["kind"] for i in report["deterministic_issues"]}
        self.assertTrue({"orphan_passage", "orphan_source_sentence", "invalid_options", "invalid_question_number", "invalid_json", "duplicate_id", "invalid_offset", "orphan_breakdown", "question_numbers"} <= kinds, kinds)
        json_issues = [i for i in report["deterministic_issues"] if i["kind"] == "invalid_json"]
        self.assertEqual(len({i["issue_id"] for i in json_issues}), 2)
        self.assertEqual(report["deterministic_issues"], sorted(report["deterministic_issues"], key=lambda i: (i["entity"], i["rule"], i.get("field", ""))))

    def test_hostile_json_shapes_become_findings_or_input_errors(self):
        data = snapshot()
        data["passages"][0].update(publication_status=[], exam_type={}, text_number=[])
        data["questions"][0].update(passage_id=[], source_sentence_id={}, review_status=[], correct_answer=[], options_json=[], number={})
        data["questions"].append(None)
        report = self.audit(data)
        self.assertGreater(report["summary"]["deterministic_issue_count"], 0)
        self.put({"format": "wrong"})
        self.assertEqual(self.cli("--snapshot", self.path)[0], 2)

    def test_database_readonly_hash_and_missing_no_creation(self):
        target = self.root / "fixture.db"
        data = snapshot()
        conn = sqlite3.connect(target)
        for name, table in (("passages", "exam_passages"), ("sentences", "exam_sentences"), ("questions", "exam_questions")):
            fields = list(data[name][0])
            conn.execute(f'CREATE TABLE {table} (' + ','.join('"' + f + '"' for f in fields) + ')')
            for row in data[name]:
                conn.execute(f'INSERT INTO {table} VALUES (' + ','.join('?' for _ in fields) + ')', [row[f] for f in fields])
        conn.execute('CREATE TABLE sentence_breakdowns (sentence_id TEXT, data_json TEXT)')
        conn.execute('CREATE TABLE bank_events (id INTEGER, passage_id TEXT)')
        conn.commit()
        conn.close()
        before = target.read_bytes()
        report = audit_database(target)
        self.assertEqual(report["summary"]["deterministic_issue_count"], 0)
        self.assertEqual(before, target.read_bytes())
        self.assertEqual(report["provenance"]["source_sha256"], hashlib.sha256(before).hexdigest())
        missing = self.root / "missing.db"
        self.assertEqual(self.cli("--database", missing)[0], 2)
        self.assertFalse(missing.exists())

    def test_missing_tables_count_is_error(self):
        path = self.root / "empty.db"
        sqlite3.connect(path).close()
        report = audit_database(path)
        self.assertEqual(report["summary"]["deterministic_issue_count"], 5)
        self.assertEqual(self.cli("--database", path)[0], 1)

    def test_cli_reports_create_only_exit_and_diff(self):
        source = self.put()
        output, md = self.root / "report.json", self.root / "report.md"
        self.assertEqual(self.cli("--snapshot", source, "--output", output, "--markdown", md)[0], 0)
        before = output.read_bytes()
        parsed = json.loads(before.decode("utf-8"))
        self.assertEqual(parsed["summary"]["deterministic_issue_count"], 0)
        self.assertTrue(before.endswith(b"\n"))
        markdown = md.read_text(encoding="utf-8")
        self.assertTrue(markdown.startswith("# Question-bank audit\n"))
        self.assertIn("\n## Provenance\n", markdown)
        self.assertGreater(len(markdown.splitlines()), 20)
        self.assertEqual(self.cli("--snapshot", source, "--output", output)[0], 2)
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual(self.cli("--snapshot", source, "--output", source)[0], 2)
        self.assertEqual(self.cli("--snapshot", source, "--previous", output)[0], 0)
        data = snapshot()
        data["questions"][0]["correct_answer"] = "Z"
        self.put(data)
        code, stdout, _ = self.cli("--snapshot", source)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout)["summary"]["deterministic_issue_count"], 1)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
            main(["--snapshot", str(source), "--database", str(self.root / "x")])
        self.assertEqual(cm.exception.code, 2)

    def test_exact_quote_whitespace_wrong_sentence_and_ambiguity(self):
        data = snapshot()
        original = data["passages"][0]["text"]
        wrapped = original.replace("passage for", "passage\n  for")
        data["passages"][0]["text"] = wrapped
        data["sentences"][0].update(text=wrapped, char_end=len(wrapped))
        report = self.audit(data)
        self.assertEqual(report["summary"]["deterministic_issue_count"], 0)
        data["passages"][0]["text"] = wrapped + " " + wrapped
        duplicate = copy.deepcopy(data["sentences"][0])
        duplicate.update(id="s2", sentence_index=2, char_start=len(wrapped) + 1, char_end=2 * len(wrapped) + 1)
        data["sentences"].append(duplicate)
        report = self.audit(data)
        self.assertEqual(sum(i["kind"] == "invalid_source_quote" for i in report["deterministic_issues"]), 5)
        data = snapshot()
        other = "Another synthetic sentence with different evidence."
        start = len(original) + 1
        data["passages"][0]["text"] += " " + other
        duplicate = copy.deepcopy(data["sentences"][0])
        duplicate.update(id="s2", sentence_index=2, text=other, char_start=start, char_end=start + len(other))
        data["sentences"].append(duplicate)
        data["questions"][0]["source_sentence_id"] = "s2"
        data["questions"][1]["source_quote"] = "This quote never appears in the passage."
        report = self.audit(data)
        self.assertEqual(sum(i["kind"] == "invalid_source_quote" for i in report["deterministic_issues"]), 2)

    def test_snapshot_order_independence_and_counts(self):
        data = snapshot()
        first = self.audit(data)
        data["questions"].reverse()
        second = self.audit(data)
        self.assertEqual(first["deterministic_issues"], second["deterministic_issues"])
        self.assertEqual(first["human_review_items"], second["human_review_items"])
        self.assertEqual(first["provenance"]["normalized_rows_sha256"], second["provenance"]["normalized_rows_sha256"])
        data["counts"] = {}
        self.assertIn("snapshot_counts", {i["kind"] for i in self.audit(data)["deterministic_issues"]})


if __name__ == "__main__":
    unittest.main()
