import re
from typing import Any

from llm import analyze_ad_hoc_reading

from ..canvas import _canvas_action

def _parse_ad_hoc_options(text: str) -> tuple[str, str, dict[str, str]] | None:
    matches = list(
        re.finditer(r"(?m)^\s*([A-D])\s*[\.\)、:：]\s*(.+?)\s*$", text)
    )
    if len(matches) < 4:
        return None
    options: dict[str, str] = {}
    for match in matches[:4]:
        options[match.group(1).upper()] = match.group(2).strip()
    if set(options) != {"A", "B", "C", "D"}:
        return None
    head = text[: matches[0].start()].strip()
    lines = [line.strip() for line in head.splitlines() if line.strip()]
    if not lines:
        return None
    if len(lines) == 1 and "?" in lines[0]:
        sentences = [
            item.strip()
            for item in re.split(r"(?<=[.!?])\s+", lines[0])
            if item.strip()
        ]
        if len(sentences) > 1 and "?" in sentences[-1]:
            return " ".join(sentences[:-1]).strip(), sentences[-1], options
    question = next((line for line in reversed(lines) if "?" in line), lines[-1])
    passage_lines = lines[:-1] if lines[-1] == question else lines
    return "\n".join(passage_lines).strip(), question, options


def _ad_hoc_reading(message: str) -> dict[str, Any] | None:
    raw = message.split("：", 1)[-1] if "：" in message else message
    parsed = _parse_ad_hoc_options(raw)
    if not parsed:
        return None
    passage, question, options = parsed
    analyzed = analyze_ad_hoc_reading(passage, question, options)
    if analyzed:
        analysis = analyzed["analysis"]
        correct = analyzed["correct_answer"]
        question_type = analyzed["question_type"]
        steps = analyzed["steps"]
        llm_used = True
    else:
        analysis = {
            key: {
                "trapType": "待分析",
                "explanation": "当前未配置模型，先保留选项结构；可点击 Agent 继续追问。",
            }
            for key in ("A", "B", "C", "D")
        }
        correct = ""
        question_type = "外源阅读题"
        steps = []
        llm_used = False
    data = {
        "passage_text": passage,
        "question_text": question,
        "options": options,
        "analysis": analysis,
        "correct_answer": correct,
        "question_type": question_type,
        "steps": steps,
        "source_label": "自定义输入 · 实时阅读验伪",
    }
    return {
        "intro": (
            "这道外源题已经铺到左侧联读画布。右侧只保留一句话：先回原文找定位句，"
            "再逐项检查是否偷换概念、扩大范围或无中生有。"
        ),
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            _canvas_action("reading", data, data["source_label"])
        ],
        "widgets": [],
        "llm_used": llm_used,
    }
