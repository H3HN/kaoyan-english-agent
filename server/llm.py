import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("LLM_API_KEY", "").strip()
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1").strip()
MODEL = os.getenv("LLM_MODEL", "deepseek-chat").strip()

logger = logging.getLogger("yanyu.llm")

SYSTEM_PROMPT = """你是“研语智学（YanYu Agent）”，一名深耕考研英语（一/二）命题规律的首席教研智能体。
你只能基于系统提供的工具结果与真题出处作答，不得编造大纲属性、考频或真题出处。
输出必须是中文、结构清晰、面向学生，不写寒暄，不输出 Markdown 代码围栏。
如果上下文中没有依据，明确说明“当前知识库没有完全匹配项”。"""


def is_configured() -> bool:
    return bool(API_KEY)


def status() -> dict[str, Any]:
    return {
        "llm_configured": is_configured(),
        "llm_model": MODEL if is_configured() else None,
        "llm_base_url": BASE_URL if is_configured() else None,
    }


def _extract_json(content: str) -> dict[str, Any] | None:
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(text[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


def _sanitize(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None
    intro = str(payload.get("intro", "")).strip()
    raw_sections = payload.get("sections")
    if not intro or not isinstance(raw_sections, list):
        return None

    sections: list[dict[str, Any]] = []
    for raw in raw_sections[:5]:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title", "")).strip()
        body = str(raw.get("body", "")).strip()
        code = str(raw.get("code", "")).strip()
        items_raw = raw.get("items")
        items = (
            [str(item).strip() for item in items_raw if str(item).strip()][:8]
            if isinstance(items_raw, list)
            else []
        )
        if not title or not (body or code or items):
            continue
        section: dict[str, Any] = {"title": title[:80]}
        if body:
            section["body"] = body[:1200]
        if items:
            section["items"] = [item[:500] for item in items]
        if code:
            section["code"] = code[:800]
        sections.append(section)

    if not sections:
        return None
    return {"intro": intro[:1200], "sections": sections}


def polish_chat(
    message: str,
    base_result: dict[str, Any],
) -> dict[str, Any] | None:
    """Use DeepSeek to rewrite the deterministic answer into teaching prose.

    The deterministic result remains the source of truth: tool_trace and
    citations are always returned by the caller, never by the model.
    """
    if not is_configured():
        return None

    context = {
        "user_question": message,
        "deterministic_answer": {
            "intro": base_result.get("intro", ""),
            "sections": base_result.get("sections", []),
        },
        "tool_trace": base_result.get("tool_trace", []),
        "citations": base_result.get("citations", []),
    }

    user_prompt = f"""请基于下面的工具结果，把回答改写成一节面向考研学生的结构化讲解。

工具上下文：
{json.dumps(context, ensure_ascii=False)}

只输出 JSON，格式：
{{
  "intro": "一段导入，2-3 句",
  "sections": [
    {{
      "title": "小标题",
      "body": "可选段落",
      "items": ["可选列表项"],
      "code": "可选英文原句或主干"
    }}
  ]
}}

要求：
1. 3-5 个 sections，按“定位/结构/词句/考点”顺序组织。
2. 引用真题必须保留上下文中的出处，不得编造新出处。
3. 不要重复工具函数名，除非它有助于解释证据来源。
4. 不要输出 Markdown 代码围栏或额外说明。
5. 只能讨论 citations 与 deterministic_answer 中出现的内容；不得引用其他年份、其他篇目的句子，也不得凭记忆补充真题。
6. 如果不确定，保留 deterministic_answer 的原表述，不要扩写。
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=50)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1600,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            # Some OpenAI-compatible gateways do not support response_format.
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        return _sanitize(_extract_json(content))
    except Exception as exc:  # noqa: BLE001 - fall back to deterministic answer
        logger.warning("LLM polish failed: %s", exc)
        return None

VALID_TRAPS = {
    "偷换概念",
    "扩大范围",
    "缩小范围",
    "正反混淆",
    "无中生有",
    "过于绝对",
    "过度推理",
    "张冠李戴",
}


def analyze_imported_question(
    passage: str,
    content: str,
    options: dict[str, str],
    correct_answer: str,
) -> dict[str, Any] | None:
    """Generate per-option trap analysis for a newly imported question."""
    if not is_configured():
        return None

    user_prompt = f"""请分析这道考研英语阅读题，只输出 JSON。

文章：
{passage[:6000]}

题干：{content}

选项：
A. {options.get('A', '')}
B. {options.get('B', '')}
C. {options.get('C', '')}
D. {options.get('D', '')}

正确答案：{correct_answer}

输出格式：
{{
  "question_type": "细节题/主旨题/推理题/词义题/态度题 之一",
  "location": "原文定位句或段落",
  "analysis": {{
    "A": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
    "B": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
    "C": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
    "D": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}}
  }},
  "steps": ["步骤1", "步骤2", "步骤3", "步骤4"]
}}

要求：
1. 正确答案的 trapType 必须是“正确”；其他选项归入偷换概念、扩大范围、缩小范围、正反混淆、无中生有、过于绝对、过度推理、张冠李戴之一。
2. 每个错误选项都要给出原文反证，不能只说“不符合原文”。
3. 不要编造文章没有的信息。
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=50)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1400,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed:
            return None

        raw_analysis = parsed.get("analysis")
        if not isinstance(raw_analysis, dict):
            return None
        analysis: dict[str, dict[str, str]] = {}
        for key in ("A", "B", "C", "D"):
            raw = raw_analysis.get(key)
            if not isinstance(raw, dict):
                raw = {}
            trap = str(raw.get("trapType", "")).strip()
            explanation = str(raw.get("explanation", "")).strip()
            if key == correct_answer:
                trap = "正确"
                explanation = explanation or "与原文信息一致，为正确选项。"
            else:
                if trap == "正确":
                    trap = "待分析"
                    explanation = "自动分析结果与正确答案冲突，请复核。"
                trap = trap if trap in VALID_TRAPS else "待分析"
                explanation = explanation or "导入题目尚未生成该选项分析。"
            analysis[key] = {
                "trapType": trap,
                "explanation": explanation[:800],
            }

        question_type = str(parsed.get("question_type", "细节题")).strip()
        if question_type not in {
            "细节题",
            "主旨题",
            "推理题",
            "词义题",
            "态度题",
        }:
            question_type = "细节题"
        steps = [
            str(item).strip()
            for item in parsed.get("steps", [])
            if str(item).strip()
        ][:6]
        if not steps:
            steps = [
                "识别题型与题干关键词。",
                "回到原文定位对应句。",
                "逐项比对，标注陷阱类型。",
                "排除干扰项，确认正确答案。",
            ]
        return {
            "question_type": question_type,
            "location": str(parsed.get("location", "自定义导入")).strip()[:200],
            "analysis": analysis,
            "steps": steps,
        }
    except Exception as exc:  # noqa: BLE001 - import still works without LLM
        logger.warning("LLM option analysis failed: %s", exc)
        return None

VALID_QUESTION_TYPES = {"细节题", "主旨题", "推理题", "词义题", "态度题"}


def extract_exam_text(
    raw_text: str,
    year: int,
    exam_type: str,
    text_number: int,
    answer_key: str = "",
) -> dict[str, Any] | None:
    """Extract one reading passage and its questions from raw exam text."""
    if not is_configured():
        return None

    prompt = f"""从下面的考研英语真题原文中，提取 Text {text_number} 的阅读文章与题目。

考试：{year} 年 {exam_type}
Text：{text_number}
答案序列（可能为空）：{answer_key or "未提供"}

只输出 JSON：
{{
  "passage": "完整英文文章，不要包含题干和选项",
  "questions": [
    {{
      "number": 1,
      "question_type": "细节题/主旨题/推理题/词义题/态度题",
      "content": "题干",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "A/B/C/D",
      "location": "定位说明",
      "source_quote": "从文章中摘录的、能回答该题的原文句子"
    }}
  ],
  "answer_source": "provided 或 inferred"
}}

要求：
1. questions 按原文顺序，通常 5 题。
2. 如果提供了答案序列，必须使用答案序列；否则根据文章推断，并把 answer_source 设为 inferred。
3. 不要编造原文没有的题目或选项；无法确定的字段留空。
4. 只输出 JSON，不输出解释。

原文：
{raw_text[:16000]}
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=90)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.15,
            "max_tokens": 3200,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed:
            return None

        passage = str(parsed.get("passage", "")).strip()
        raw_questions = parsed.get("questions")
        if len(passage) < 100 or not isinstance(raw_questions, list):
            return None

        questions: list[dict[str, Any]] = []
        for index, raw in enumerate(raw_questions[:8], start=1):
            if not isinstance(raw, dict):
                continue
            content = str(raw.get("content", "")).strip()
            raw_options = raw.get("options")
            if not content or not isinstance(raw_options, dict):
                continue
            options = {
                key: str(raw_options.get(key, "")).strip()
                for key in ("A", "B", "C", "D")
            }
            if not all(options.values()):
                continue
            correct = str(raw.get("correct_answer", "")).strip().upper()[:1]
            if correct not in {"A", "B", "C", "D"}:
                continue
            qtype = str(raw.get("question_type", "细节题")).strip()
            if qtype not in VALID_QUESTION_TYPES:
                qtype = "细节题"
            questions.append(
                {
                    "number": index,
                    "question_type": qtype,
                    "content": content[:1500],
                    "options": options,
                    "correct_answer": correct,
                    "location": str(raw.get("location", "")).strip()[:200],
                    "source_quote": str(raw.get("source_quote", "")).strip()[:600],
                }
            )
        if not questions:
            return None
        return {
            "passage": passage[:20000],
            "questions": questions,
            "answer_source": str(parsed.get("answer_source", "inferred")),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM exam extraction failed: %s", exc)
        return None


def analyze_imported_questions_batch(
    passage: str,
    questions: list[dict[str, Any]],
) -> dict[int, dict[str, Any]] | None:
    """Analyze all options for a batch of imported questions in one call."""
    if not is_configured():
        return None

    q_payload = [
        {
            "number": item["number"],
            "content": item["content"],
            "options": item["options"],
            "correct_answer": item["correct_answer"],
        }
        for item in questions
    ]
    prompt = f"""请逐题分析下面这组考研英语阅读题，只输出 JSON。

文章：
{passage[:6000]}

题目：
{json.dumps(q_payload, ensure_ascii=False, indent=2)}

输出格式：
{{
  "questions": [
    {{
      "number": 1,
      "question_type": "细节题/主旨题/推理题/词义题/态度题",
      "analysis": {{
        "A": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
        "B": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
        "C": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}},
        "D": {{"trapType": "正确或陷阱类型", "explanation": "中文解释"}}
      }},
      "steps": ["步骤1", "步骤2", "步骤3"]
    }}
  ]
}}

要求：
1. 正确答案的 trapType 必须是“正确”；错误选项归入偷换概念、扩大范围、缩小范围、正反混淆、无中生有、过于绝对、过度推理、张冠李戴之一。
2. 每个错误选项给出原文反证。
3. 不要编造文章没有的信息。
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 6000,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed or not isinstance(parsed.get("questions"), list):
            return None

        result: dict[int, dict[str, Any]] = {}
        for raw in parsed["questions"]:
            if not isinstance(raw, dict):
                continue
            number = int(raw.get("number", 0))
            raw_analysis = raw.get("analysis")
            if number <= 0 or not isinstance(raw_analysis, dict):
                continue
            analysis: dict[str, dict[str, str]] = {}
            for key in ("A", "B", "C", "D"):
                info = raw_analysis.get(key) or {}
                if not isinstance(info, dict):
                    info = {}
                analysis[key] = {
                    "trapType": str(info.get("trapType", "待分析")).strip()[:20],
                    "explanation": str(info.get("explanation", "")).strip()[:800],
                }
            steps = [
                str(item).strip()
                for item in raw.get("steps", [])
                if str(item).strip()
            ][:6]
            qtype = str(raw.get("question_type", "细节题")).strip()
            if qtype not in VALID_QUESTION_TYPES:
                qtype = "细节题"
            result[number] = {
                "question_type": qtype,
                "analysis": analysis,
                "steps": steps,
            }
        return result or None
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM batch analysis failed: %s", exc)
        return None
