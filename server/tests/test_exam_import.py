"""Offline regression tests: fake model output, in-memory SQLite, no project DB writes.

Run from server: python -m unittest discover -s tests -p 'test_*.py' -v
"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exam_import import (ImportValidationError, expected_numbers, locate_quote,
                         normalize_passage, parse_answer_key, slice_text, split_passage,
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

    def test_slice_text_extracts_text_block(self):
        raw = ("Directions: Read the following texts.\n"
               "Text 1 First passage body sentence here.\n"
               "Text 2 Second passage body follows.\n"
               "Part B Translation.")
        self.assertIn("First passage body", slice_text(raw, 1))
        self.assertNotIn("First passage body", slice_text(raw, 2))
        self.assertIn("Second passage body", slice_text(raw, 2))
        # No Text marker: return the whole dump unchanged (caller validates).
        self.assertEqual(slice_text("just raw text", 1), "just raw text")

