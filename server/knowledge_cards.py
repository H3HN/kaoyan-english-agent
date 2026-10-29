"""Kaoyan reading trap method cards.

Original content authored for this project. The structure is inspired by
method-card systems such as reading-analysis, but no third-party card text is
copied. Each card is a compact diagnostic routine, not a question-bank answer.
"""
from __future__ import annotations

import sqlite3
from typing import Any

TRAP_CARDS: list[dict[str, Any]] = [
    {
        "name": "无中生有",
        "tone": "cyan",
        "definition": "选项出现了原文完全没有的信息，常识上成立也不能选。",
        "signals": ["原文未出现的名词、比较或因果", "选项听起来很合理，但定位句找不到", "把常识当成作者观点"],
        "steps": ["回到题干定位句", "在定位段逐句找选项关键词", "找不到同义或指代依据就直接排除"],
        "correct_pattern": "正确项一定能在原文找到同义替换、指代或合理概括。",
        "question_types": ["细节题", "推理题"],
    },
    {
        "name": "正反混淆",
        "tone": "red",
        "definition": "把肯定说成否定，把支持说成反对，或把趋势说反。",
        "signals": ["not / never / fail to / rather than", "作者态度与选项褒贬相反", "原文是风险，选项说成收益"],
        "steps": ["圈出定位句的否定词和态度词", "判断作者是支持、反对还是保留", "把选项的褒贬方向与原文对齐"],
        "correct_pattern": "正确项保留原文的态度方向和否定范围。",
        "question_types": ["态度题", "细节题", "推理题"],
    },
    {
        "name": "偷换概念",
        "tone": "red",
        "definition": "把原文的主体、对象、时态、程度或因果关系换成相近但不同的说法。",
        "signals": ["近义词替换但对象变了", "把 could 说成 already", "把 A 的观点安到 B 身上"],
        "steps": ["逐词比对主语和宾语", "核对时态、情态和程度", "把选项改回原文，看看是否还成立"],
        "correct_pattern": "正确项只替换表达，不替换逻辑主体和事实关系。",
        "question_types": ["细节题", "词义题"],
    },
    {
        "name": "扩大范围",
        "tone": "amber",
        "definition": "把局部、有限、条件下成立的结论扩大为全部、普遍、必然。",
        "signals": ["all / every / always / entirely", "把 some 说成 most", "把某一行业说成所有行业"],
        "steps": ["圈出原文量词", "检查选项是否升级为全称", "把选项缩回原文范围再判断"],
        "correct_pattern": "正确项保留原文的限定词和适用边界。",
        "question_types": ["细节题", "推理题"],
    },
    {
        "name": "缩小范围",
        "tone": "amber",
        "definition": "把普遍结论缩小为某个局部对象，或把多种原因说成唯一原因。",
        "signals": ["only / merely / just / solely", "把多个原因压缩成一个", "把整类现象说成某个案例"],
        "steps": ["找原文的并列项和范围词", "检查选项是否漏掉其他对象", "确认选项是否把充分条件写成必要条件"],
        "correct_pattern": "正确项覆盖原文的必要范围，不偷减对象。",
        "question_types": ["细节题", "主旨题"],
    },
    {
        "name": "过于绝对",
        "tone": "red",
        "definition": "把可能、有时、在条件下成立说成必然、总是、无条件成立。",
        "signals": ["definitely / must / never / completely", "把 argue 说成 prove", "把建议说成强制"],
        "steps": ["找原文情态动词", "区分观点、事实和推测", "把选项的绝对词降级后核对"],
        "correct_pattern": "正确项保留原文的确定性等级。",
        "question_types": ["推理题", "态度题"],
    },
    {
        "name": "过度推理",
        "tone": "violet",
        "definition": "从原文信息推出超出作者表达范围的结论，常见于“由此可以证明”。",
        "signals": ["因此必须 / 由此证明 / 说明应该", "从现象直接跳到政策建议", "忽略原文的反例或限定"],
        "steps": ["区分原文事实与选项结论", "检查推理是否多走了一步", "找作者有没有明确支持这个结论"],
        "correct_pattern": "正确项只做原文允许的最小推理。",
        "question_types": ["推理题", "主旨题"],
    },
    {
        "name": "张冠李戴",
        "tone": "violet",
        "definition": "把文中 A 的观点、行为、特征或研究结论安到 B 身上。",
        "signals": ["主语错位", "把 critics 的担忧说成 scientists 的结论", "把研究者的发现说成作者的主张"],
        "steps": ["列出定位段的主体", "把选项主语与原文主语对齐", "检查动作和观点归属"],
        "correct_pattern": "正确项的主语、动作、观点三者与原文一致。",
        "question_types": ["细节题", "推理题"],
    },
]

_BY_NAME = {item["name"]: item for item in TRAP_CARDS}


def list_trap_cards() -> list[dict[str, Any]]:
    return TRAP_CARDS


def get_trap_card(name: str | None) -> dict[str, Any] | None:
    if not name:
        return None
    return _BY_NAME.get(name)


def get_learner_profile(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT question_type, is_correct, trap_type FROM practice_records"
    ).fetchall()
    total = len(rows)
    correct = sum(1 for row in rows if row["is_correct"])
    traps: dict[str, int] = {}
    by_type: dict[str, dict[str, int]] = {}
    for row in rows:
        qtype = row["question_type"]
        bucket = by_type.setdefault(qtype, {"total": 0, "correct": 0})
        bucket["total"] += 1
        bucket["correct"] += 1 if row["is_correct"] else 0
        if not row["is_correct"] and row["trap_type"]:
            traps[row["trap_type"]] = traps.get(row["trap_type"], 0) + 1
    weakest_trap = max(traps, key=traps.get) if traps else None
    question_stats = [
        {
            "question_type": name,
            "total": value["total"],
            "accuracy": round(value["correct"] / value["total"], 3)
            if value["total"]
            else 0,
        }
        for name, value in by_type.items()
    ]
    question_stats.sort(key=lambda item: (item["accuracy"], -item["total"]))
    return {
        "total_attempts": total,
        "correct": correct,
        "accuracy": round(correct / total, 3) if total else 0,
        "trap_counts": dict(sorted(traps.items(), key=lambda item: -item[1])),
        "weakest_trap": weakest_trap,
        "weakest_trap_card": get_trap_card(weakest_trap),
        "by_question_type": question_stats,
    }
