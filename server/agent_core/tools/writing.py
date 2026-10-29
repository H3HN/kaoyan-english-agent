"""Writing review canvas tool."""
from __future__ import annotations

import sqlite3
from typing import Any

from ..canvas import _canvas_action


def _writing_insight(
    conn: sqlite3.Connection, text: str, prompt: str = ""
) -> dict[str, Any]:
    draft = text.strip()
    title = prompt.strip() or "考研英语写作练习"
    data = {
        "source_label": f"考研英语写作 · {title}",
        "prompt": title,
        "draft": draft,
    }
    return {
        "intro": (
            f"已打开《{title}》写作画布。先写作文，再点击批改；我会按内容、结构、语言、任务完成度给最小修改建议。"
            if not draft
            else f"《{title}》已放入左侧写作画布。我会优先保留你的原句，只做最小修改，再给一个更地道的示范段。"
        ),
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            _canvas_action("writing", data, data["source_label"])
        ],
        "widgets": [],
        "llm_used": False,
    }
