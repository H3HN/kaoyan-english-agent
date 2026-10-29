"""Offline regression tests: fake model output, in-memory SQLite, no project DB writes.

Run from server: python -m unittest discover -s tests -p 'test_*.py' -v
"""
import copy
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import HTTPException
from fastapi.testclient import TestClient
import app as api
import db
from exam_import import (ImportValidationError, expected_numbers, locate_quote,
                         normalize_passage, parse_answer_key, split_passage,
                         validate_extraction)

PASSAGE = (
    "The U.S. Supreme Court considered a new policy. Dr. Smith explained the policy clearly. "
    "The policy would protect public education and provide support for local schools.\n\n"
    "Researchers measured the effect on students. Their report contains 3.14 units of data. "
    "The final results require careful interpretation."
)


def extraction(text_number=1):
    return {"passage": PASSAGE, "questions": [
        {"number": n, "content": f"What does question {n} ask?", "question_type": "细节题",
         "options": {"A": "First option", "B": "Second option", "C": "Third option", "D": "Fourth option"},
         "correct_answer": "D", "source_quote": "Researchers measured the effect on students."}
        for n in expected_numbers(text_number)
    ]}


class ValidationTests(unittest.TestCase):
    def test_answer_formats_and_numbered_mapping(self):
        for text in ("ABCDA", "A B C D A", "21-25 ABCDA", "21:A,22:B,23:C,24:D,25:A",
                     "25:A;23:C;21:A;24:D;22:B"):
            self.assertEqual(parse_answer_key(text, expected_numbers(1)), dict(zip(range(21, 26), "ABCDA")))
        self.assertEqual(parse_answer_key("", expected_numbers(1)), {})

    def test_invalid_answer_formats_never_extract_letters_from_junk(self):
        for value in ("ABCD", "ABCDAA", "Answer ABCDA", "26-30 ABCDA", "21:A,21:B,23:C,24:D,25:A", "ABXDA"):
            with self.subTest(value=value), self.assertRaises(ImportValidationError):
                parse_answer_key(value, expected_numbers(1))

    def test_shuffled_questions_map_answers_by_original_number(self):
        raw = extraction()
        raw["questions"].reverse()
        result = validate_extraction(raw, 1, "ABCDA")
        self.assertEqual([q["number"] for q in result["questions"]], list(range(21, 26)))
        self.assertEqual("".join(q["correct_answer"] for q in result["questions"]), "ABCDA")
        self.assertEqual(result["answer_source"], "provided")

    def test_missing_middle_question_is_rejected_not_shifted(self):
        raw = extraction()
        raw["questions"].pop(1)
        with self.assertRaises(ImportValidationError) as error:
            validate_extraction(raw, 1, "ABCDA")
        self.assertIn("22", str(error.exception))

    def test_missing_option_duplicate_number_relative_number_rejected(self):
        for kind in ("missing_option", "duplicate", "relative", "bad_number", "extra"):
            raw = extraction()
            if kind == "missing_option":
                del raw["questions"][1]["options"]["D"]
            elif kind == "duplicate":
                raw["questions"][1]["number"] = 21
            elif kind == "relative":
                for i, q in enumerate(raw["questions"], 1):
                    q["number"] = i
            elif kind == "bad_number":
                raw["questions"][0]["number"] = 21.0
            else:
                raw["questions"].append(copy.deepcopy(raw["questions"][0]))
            with self.subTest(kind=kind), self.assertRaises(ImportValidationError):
                validate_extraction(raw, 1, "ABCDA")

    def test_provided_answers_can_replace_missing_model_answers(self):
        raw = extraction(4)
        for q in raw["questions"]:
            q["correct_answer"] = ""
        self.assertEqual(validate_extraction(raw, 4, "36-40 ABCDA")["questions"][0]["correct_answer"], "A")
        with self.assertRaises(ImportValidationError):
            validate_extraction(raw, 4)

    def test_inferred_source_cannot_be_forged_by_model(self):
        raw = extraction()
        raw["answer_source"] = "provided"
        self.assertEqual(validate_extraction(raw, 1)["answer_source"], "inferred")

    def test_wrong_shapes_return_validation_errors(self):
        for raw in (None, {}, {"passage": PASSAGE, "questions": [None] * 5}):
            with self.subTest(raw=raw), self.assertRaises(ImportValidationError):
                validate_extraction(raw, 1)

    def test_no_silent_passage_truncation(self):
        raw = extraction()
        raw["passage"] = "x" * 20001
        with self.assertRaises(ImportValidationError):
            validate_extraction(raw, 1)

    def test_unsupported_text(self):
        with self.assertRaises(ImportValidationError):
            expected_numbers(5)


class TextLocationTests(unittest.TestCase):
    def test_paragraphs_abbreviations_offsets_and_decimal(self):
        normalized = normalize_passage(PASSAGE.replace("\n\n", "\r\n\r\n"))
        rows = split_passage(normalized)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["text"], "The U.S. Supreme Court considered a new policy.")
        self.assertEqual(rows[1]["text"], "Dr. Smith explained the policy clearly.")
        self.assertEqual(rows[3]["paragraph"], 2)
        self.assertEqual(rows[3]["sentence_index"], 1)
        self.assertIn("3.14", rows[4]["text"])
        for row in rows:
            self.assertEqual(normalized[row["char_start"]:row["char_end"]], row["text"])

    def test_soft_wrap_not_a_new_paragraph(self):
        text = normalize_passage("A line\nwrapped within one paragraph.\n\nAnother paragraph.")
        self.assertEqual(text, "A line wrapped within one paragraph.\n\nAnother paragraph.")
        self.assertEqual(len(split_passage(text)), 2)

    def test_unicode_character_offsets(self):
        text = "前言😀. An English sentence ends.\n\nSecond paragraph follows."
        for row in split_passage(text):
            self.assertEqual(text[row["char_start"]:row["char_end"]], row["text"])

    def rows(self, passage=PASSAGE):
        return [dict(row, id=f"s{i}") for i, row in enumerate(split_passage(passage))]

    def test_exact_quote_binds_only_actual_sentence(self):
        result = locate_quote("Researchers measured the effect on students.", PASSAGE, self.rows())
        self.assertEqual(result, {"source_sentence_id": "s3", "location_status": "exact_quote"})

    def test_absent_or_short_quote_never_selects_first_sentence(self):
        for quote in ("", "school", "An invented sentence not present in the passage."):
            result = locate_quote(quote, PASSAGE, self.rows())
            self.assertIsNone(result["source_sentence_id"])
            self.assertEqual(result["location_status"], "pending")

    def test_multi_sentence_quote_preserved_but_not_bound(self):
        quote = "Researchers measured the effect on students. Their report contains 3.14 units of data."
        self.assertEqual(locate_quote(quote, PASSAGE, self.rows())["location_status"], "multi_sentence")

    def test_repeated_quote_is_ambiguous(self):
        text = "This sentence appears twice. This sentence appears twice."
        result = locate_quote("This sentence appears twice.", text, self.rows(text))
        self.assertEqual(result["location_status"], "ambiguous")
        self.assertIsNone(result["source_sentence_id"])


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(db.SCHEMA)
        self.addCleanup(self.conn.close)
        self.raw = extraction()
        for name, value in (("llm_status", {"llm_configured": True}),
                            ("extract_exam_text", self.raw), ("analyze_imported_questions_batch", None),
                            ("analyze_imported_question", None)):
            mock = patch.object(api, name, return_value=value).start()
            setattr(self, name, mock)
        self.addCleanup(patch.stopall)
        self.payload = api.AutoImportRequest(year=2024, exam_type="英语一", text_number=1,
                                              text="raw exam text", answer_key="ABCDA")

    def counts(self):
        return tuple(self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                     for table in ("exam_passages", "exam_sentences", "exam_questions"))

    def test_success_persists_original_numbers_paragraphs_provenance(self):
        self.raw["questions"].reverse()
        response = api.auto_import_exam(self.payload, self.conn)
        self.assertEqual(self.counts(), (1, 6, 5))
        self.assertEqual([q["number"] for q in response["questions"]], list(range(21, 26)))
        self.assertEqual("".join(q["correctAnswer"] for q in response["questions"]), "ABCDA")
        self.assertEqual(response["questions"][0]["answerSource"], "provided")
        self.assertEqual(response["questions"][0]["reviewStatus"], "pending")
        self.assertIn("第2段第1句", response["questions"][0]["location"])
        self.assertFalse(self.conn.in_transaction)

    def test_missing_option_leaves_all_tables_empty(self):
        del self.raw["questions"][1]["options"]["D"]
        with self.assertRaises(HTTPException) as error:
            api.auto_import_exam(self.payload, self.conn)
        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(self.counts(), (0, 0, 0))
        self.analyze_imported_questions_batch.assert_not_called()

    def test_invalid_answer_rejected_before_model(self):
        self.payload.answer_key = "ABCD"
        with self.assertRaises(HTTPException):
            api.auto_import_exam(self.payload, self.conn)
        self.extract_exam_text.assert_not_called()
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_duplicate_is_409_before_calling_model_again(self):
        api.auto_import_exam(self.payload, self.conn)
        self.extract_exam_text.reset_mock()
        with self.assertRaises(HTTPException) as error:
            api.auto_import_exam(self.payload, self.conn)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(self.counts(), (1, 6, 5))
        self.extract_exam_text.assert_not_called()

    def test_sql_failure_rolls_back_passage_sentences_and_questions(self):
        self.conn.executescript("CREATE TRIGGER fail_question BEFORE INSERT ON exam_questions "
                                "WHEN NEW.number=23 BEGIN SELECT RAISE(ABORT, 'test failure'); END;")
        with self.assertRaises(sqlite3.IntegrityError):
            api.auto_import_exam(self.payload, self.conn)
        self.assertEqual(self.counts(), (0, 0, 0))
        self.assertFalse(self.conn.in_transaction)

    def test_model_calls_do_not_hold_write_transaction(self):
        def batch(*args):
            self.assertFalse(self.conn.in_transaction)
        self.analyze_imported_questions_batch.side_effect = batch
        api.auto_import_exam(self.payload, self.conn)

    def test_inferred_answer_and_pending_location_survive_reload(self):
        self.payload.answer_key = ""
        for q in self.raw["questions"]:
            q["source_quote"] = "An invented sentence not found here."
        result = api.auto_import_exam(self.payload, self.conn)
        result = api._full_question(self.conn, result["question_ids"][0])
        self.assertEqual(result["answerSource"], "inferred")
        self.assertEqual(result["location"], "待人工定位")
        self.assertEqual(result["sourceSentence"], "")
        self.assertIsNone(result["sourceSentenceId"])
        self.assertEqual(result["sourceQuote"], "An invented sentence not found here.")

    def test_manual_import_has_no_longest_sentence_fallback(self):
        payload = api.ExamImportRequest(year=2024, exam_type="英语一", passage=PASSAGE,
                                        content="What is the policy?", options={k: k for k in "ABCD"},
                                        correct_answer="A")
        response = api.import_exam(payload, self.conn)
        self.assertEqual(response["question"]["answerSource"], "manual")
        self.assertIsNone(response["question"]["sourceSentenceId"])
        with self.assertRaises(HTTPException) as error:
            api.import_exam(payload, self.conn)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(self.counts(), (1, 6, 1))

    def test_http_validation_and_error_contract_without_startup_db(self):
        def override():
            yield self.conn
        api.app.dependency_overrides[api.get_db] = override
        self.addCleanup(api.app.dependency_overrides.clear)
        # Deliberately no client context: lifespan must not initialize the real DB.
        client = TestClient(api.app)
        self.addCleanup(client.close)
        data = self.payload.model_dump()
        data["text_number"] = 5
        # Student HTTP ingestion was retired; validation remains in internal helpers.
        self.assertEqual(client.post("/api/exams/auto-import", json=data).status_code, 410)
        with self.assertRaises(ValueError):
            api.AutoImportRequest(**data)
        data["text_number"] = 1
        data["answer_key"] = "ABCD"
        with self.assertRaises(HTTPException) as error:
            api.auto_import_exam(api.AutoImportRequest(**data), self.conn)
        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail["code"], "invalid_exam")


if __name__ == "__main__":
    unittest.main()
