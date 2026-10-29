import sqlite3
from typing import Any

from ..reading import _recommend

def _practice(conn: sqlite3.Connection) -> dict[str, Any]:
    base = _recommend(conn)
    if not base["widgets"]:
        return base
    data = base["widgets"][0]["data"]
    base["intro"] = (
        f"好，给你挑了一道真实真题：{data['year']} {data['exam_type']} "
        f"Text {data['text_number']} 第 {data['question_number']} 题。"
        "我已为你铺开联读室，先自己选，再看陷阱诊断。"
    )
    base["sections"] = [
        {
            "title": "这道题怎么用",
            "items": [
                f"题型：{data.get('question_type', '阅读')}",
                "先读题干，回原文定位，不要先看选项。",
                "选完后 Agent 会自动核对定位句与选项陷阱。",
            ],
        }
    ]
    return base
