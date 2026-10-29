"""Intent router validation without network calls."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["AGENT_LLM_INTENT"] = "0"

from agent_core.intent_llm import IntentDecision, decision_to_intent
from agent_core.registry import TOOL_REGISTRY
from agent_core.skills import SKILL_NAMES


class IntentRouterTests(unittest.TestCase):
    def decision(self, name, confidence=0.9, args=None):
        return IntentDecision(intent=name, confidence=confidence, args=args or {})

    def test_every_skill_name_has_a_handler(self):
        missing = SKILL_NAMES - set(TOOL_REGISTRY)
        self.assertEqual(missing, set())

    def test_action_intent_maps_to_flashcard(self):
        intent = decision_to_intent(
            self.decision("flashcard_review"), "我要开始背诵今日单词", {}
        )
        self.assertEqual(intent.name, "flashcard_review")

    def test_reader_without_text_goes_home(self):
        intent = decision_to_intent(self.decision("reader"), "我要泛读一篇长文", {})
        self.assertEqual(intent.name, "reader_home")

    def test_reader_with_text_uses_backend_extraction(self):
        text = "The Great Gatsby is a novel about the American Dream."
        intent = decision_to_intent(
            self.decision("reader"), f"泛读这篇：{text}", {}
        )
        self.assertEqual(intent.name, "reader")
        self.assertIn("Great Gatsby", intent.payload["text"])

    def test_writing_title_maps_to_writing_canvas(self):
        intent = decision_to_intent(
            self.decision("writing", args={"prompt": "Love"}),
            "我想进行标题为Love的写作训练",
            {},
        )
        self.assertEqual(intent.name, "writing")
        self.assertEqual(intent.payload["prompt"], "Love")
        self.assertEqual(intent.payload["text"], "")

    def test_summary_requires_active_content(self):
        self.assertIsNone(
            decision_to_intent(self.decision("summarize_content"), "概括主旨", {})
        )
        intent = decision_to_intent(
            self.decision("summarize_content"),
            "概括主旨",
            {
                "active_content_text": "The Great Gatsby is a novel.",
                "active_content_title": "The Great Gatsby",
            },
        )
        self.assertEqual(intent.name, "summarize_content")
        self.assertEqual(intent.payload["title"], "The Great Gatsby")

    def test_word_intent_requires_valid_word(self):
        intent = decision_to_intent(
            self.decision("word_insight", args={"word": "novel"}),
            "看看这个词",
            {},
        )
        self.assertEqual(intent.payload["word"], "novel")
        self.assertIsNone(
            decision_to_intent(
                self.decision("word_insight", args={"word": "<script>"}),
                "看看这个词",
                {},
            )
        )


if __name__ == "__main__":
    unittest.main()
