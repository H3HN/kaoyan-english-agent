"""Feature home canvases.

Entering a mode must not silently load an example sentence, passage, or
article. A home canvas lets the learner choose the material first.
"""
from __future__ import annotations

from typing import Any

from ..canvas import _canvas_action

HOME_LABELS = {
    "listening": ("听力听写", "先选择真题、内容库文章，或粘贴一段英文。"),
    "writing": ("写作批改", "先选择题目，再开始写。"),
    "reader": ("泛读文章", "先从已发布内容库选择一篇文章。"),
    "studio": ("Studio 首页", "先选择训练模式，不再自动加载示例句。"),
}


def _home(feature: str) -> dict[str, Any]:
    label, hint = HOME_LABELS.get(feature, HOME_LABELS["studio"])
    return {
        "intro": hint,
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            _canvas_action("home", {"feature": feature}, label)
        ],
        "widgets": [],
        "llm_used": False,
    }
