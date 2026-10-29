"""Contract tests for the planner/registry split; no network or model calls."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_core.canvas import _canvas_action
from agent_core.contracts import CanvasAction, CanvasUnit, TurnIntent
from agent_core.planner import plan_turn
from agent_core.registry import TOOL_REGISTRY


class AgentCoreContractTests(unittest.TestCase):
    def test_word_plan(self):
        intent = plan_turn("解析单词 novel", {})
        self.assertIsInstance(intent, TurnIntent)
        self.assertEqual(intent.name, "word_insight")
        self.assertEqual(intent.payload["word"], "novel")

    def test_external_sentence_and_paragraph_plans(self):
        sentence = plan_turn(
            "请翻译并拆解这句话：The Great Gatsby is a novel about the American Dream.",
            {},
        )
        self.assertEqual(sentence.name, "ad_hoc_sentence")
        paragraph = plan_turn(
            "分析这段：The Great Gatsby is a novel about the American Dream. "
            "However, the narrator observes the hollow lives of the wealthy. "
            "Therefore, the novel criticizes material success.",
            {},
        )
        self.assertEqual(paragraph.name, "paragraph")

    def test_auto_diagnosis_and_plan_registry(self):
        intent = plan_turn(
            "系统自动事件",
            {"recent_event": {"event_type": "QUESTION_SUBMITTED", "question_id": "q1"}},
            "AUTO_EVENT",
        )
        self.assertEqual(intent.name, "auto_diagnosis")
        self.assertIn("schedule", TOOL_REGISTRY)
        self.assertIn("sentence", TOOL_REGISTRY)
        self.assertIn("generic", TOOL_REGISTRY)

    def test_mode_entry_returns_home_not_default_content(self):
        for message, name in (
            ("进入听力", "listening_home"),
            ("进入写作", "writing_home"),
            ("进入泛读", "reader_home"),
            ("进入Studio", "studio_home"),
        ):
            self.assertEqual(plan_turn(message, {}).name, name)

    def test_reader_context_summary_plan(self):
        intent = plan_turn(
            "概括一下主旨大意",
            {
                "current_route": "/studio",
                "active_content_type": "reader",
                "active_content_title": "The Great Gatsby",
                "active_content_text": "The Great Gatsby is a novel about the American Dream.",
            },
        )
        self.assertEqual(intent.name, "summarize_content")
        self.assertEqual(intent.payload["title"], "The Great Gatsby")

    def test_natural_language_actions_are_executed(self):
        self.assertEqual(plan_turn("我要开始背诵今日单词", {}).name, "flashcard_review")
        self.assertEqual(plan_turn("我要泛读一篇长文", {}).name, "reader_home")
        self.assertEqual(plan_turn("我要练口语", {}).name, "clarify")
        self.assertEqual(plan_turn("开始阅读", {}).name, "reading_home")
        self.assertEqual(plan_turn("开始学习", {}).name, "studio_home")

    def test_writing_title_is_extracted(self):
        intent = plan_turn("我想进行标题为Love的写作训练", {})
        self.assertEqual(intent.name, "writing")
        self.assertEqual(intent.payload["prompt"], "Love")
        self.assertEqual(intent.payload["text"], "")
        self.assertEqual(plan_turn("我想练一下作文", {}).name, "writing_home")

    def test_listening_and_writing_plans(self):
        listening = plan_turn(
            "用这段做听力听写：The Great Gatsby is a novel about the American Dream.",
            {},
        )
        self.assertEqual(listening.name, "listening")
        writing = plan_turn("批改这篇作文：Nowadays many students use AI to do homework.", {})
        self.assertEqual(writing.name, "writing")

    def test_long_article_routes_to_reader(self):
        text = ("The Great Gatsby is a novel about the American Dream. " * 40).strip()
        intent = plan_turn(f"请带我泛读这篇：{text}", {})
        self.assertEqual(intent.name, "reader")

    def test_canvas_action_is_typed(self):
        action = _canvas_action("word", {"word": "novel"}, "novel")
        parsed = CanvasAction.model_validate(action)
        self.assertEqual(parsed.action_type, "APPLY_CANVAS_COMMAND")
        self.assertIsInstance(parsed.payload.unit, CanvasUnit)
        self.assertEqual(parsed.payload.unit.tier, "word")


if __name__ == "__main__":
    unittest.main()
