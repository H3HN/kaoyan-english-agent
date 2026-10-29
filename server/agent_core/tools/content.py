"""Current-canvas content tools: summarize the article/paragraph the user sees."""
from __future__ import annotations

from typing import Any

from llm import summarize_reading


def _summarize_content(title: str, text: str) -> dict[str, Any]:
    result = summarize_reading(title, text)
    sections = []
    structure = result.get("structure") or []
    if structure:
        sections.append({"title": "文章结构", "items": structure})
    if result.get("key_takeaway"):
        sections.append({"title": "作者意图", "body": result["key_takeaway"]})
    return {
        "intro": result.get("summary", ""),
        "sections": sections,
        "tool_trace": [],
        "citations": [],
        "client_actions": [],
        "widgets": [],
        "llm_used": bool(result.get("llm_used")),
    }
