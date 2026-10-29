"""Extensive-reading canvas tool."""
from __future__ import annotations

from typing import Any

from ..canvas import _canvas_action


def _reader_insight(text: str, ctx: dict[str, Any]) -> dict[str, Any]:
    title = "自定义泛读文章"
    label = ctx.get("active_passage_label")
    if label:
        title = str(label)
    data = {
        "title": title,
        "text": text.strip(),
        "source_label": "Agent 泛读 · 点词查义",
        "license": "用户提供文本",
    }
    return {
        "intro": "长文已铺到左侧泛读器。已知词会高亮，虚线词可点开查义；每段都能下钻到段落精读。",
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [_canvas_action("reader", data, title)],
        "widgets": [],
        "llm_used": False,
    }
