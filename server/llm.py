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
  "source_quote": "逐字摘录能支持答案的原文，不能确定时留空",
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
            "source_quote": parsed.get("source_quote") if isinstance(parsed.get("source_quote"), str) else "",
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
      "number": 21,
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
1. questions 必须保留原卷题号，不得按列表顺序重编号。当前 Text 的题号应为 {21 + (text_number - 1) * 5}—{25 + (text_number - 1) * 5}，共五题；不能确定原题号时留空。
2. 如果提供了答案序列，按原题号对应；否则根据文章推断，并把 answer_source 设为 inferred。
3. 不要编造原文没有的题目或选项；无法确定的字段留空，不要丢弃不完整题目。
4. passage 必须保留原文段落，段落之间用两个换行符（JSON 中写 \\n\\n），不要自行合并或虚构段落。
5. source_quote 必须逐字摘录原文；无法确定证据时留空，主旨题可以留空待人工复核。
6. 只输出 JSON，不输出解释。

原文：
{raw_text}
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

        # Keep the raw question numbers and incomplete rows. The deterministic
        # import validator reports every defect instead of silently dropping and
        # renumbering questions (which used to shift the supplied answer key).
        if not isinstance(parsed, dict):
            return None
        return {
            "passage": parsed.get("passage"),
            "questions": parsed.get("questions"),
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
      "number": 21,
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


def analyze_sentence_breakdown(sentence: str) -> dict[str, Any] | None:
    """Generate a structured five-step breakdown for one imported sentence."""
    if not is_configured():
        return None
    prompt = f"""请拆解下面这个考研英语长难句，只输出 JSON。

句子：
{sentence}

输出格式：
{{
  "is_long": true,
  "main": "主句原文",
  "mainNote": "用中文说明主干与核心谓语",
  "clauses": [
    {{"text": "原文中的从句片段", "label": "定语从句/状语从句/宾语从句/主语从句/表语从句", "note": "它修饰谁、在句中起什么作用"}}
  ],
  "modifiers": [
    {{"text": "原文中的修饰片段", "label": "介词短语/分词短语/不定式/插入语", "note": "修饰对象与作用"}}
  ],
  "translation": "整句自然中文翻译",
  "translationLayers": ["按语义层次的中文翻译，2-4 条"],
  "grammar": [
    {{"name": "语法点名称", "note": "在本句中的具体体现"}}
  ],
  "examPoints": ["命题人可能设置的考点，2-4 条"],
  "tree": [
    {{"role": "主句", "label": "主句原文", "children": [{{"role": "定语从句", "label": "从句原文"}}]}}
  ]
}}

要求：
1. 所有 text / label 中的英文必须来自原句，不得补充原句之外的英文。
2. main 必须是原句中的连续片段。
3. 如果本句没有从句或修饰，返回空数组。
4. 中文讲解要具体，不要写“注意理解”这类空话。
5. 不要输出 Markdown 代码围栏。"""
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
            "max_tokens": 3000,
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

        words = [item for item in re.split(r"\s+", sentence) if item]
        result: dict[str, Any] = {
            "isLong": bool(parsed.get("is_long", len(words) >= 25)),
            "main": str(parsed.get("main") or sentence).strip(),
            "mainNote": str(parsed.get("mainNote") or "").strip(),
            "clauseNote": str(
                parsed.get("clauseNote")
                or "按连接词与标点剥离从句，再判断每层从句修饰的对象。"
            ).strip(),
            "translation": str(parsed.get("translation") or "").strip(),
            "clauses": [],
            "modifiers": [],
            "translationLayers": [],
            "grammar": [],
            "examPoints": [],
            "tree": [],
        }

        for key in ("clauses", "modifiers"):
            raw_items = parsed.get(key)
            if not isinstance(raw_items, list):
                continue
            for raw in raw_items[:6]:
                if not isinstance(raw, dict):
                    continue
                text = str(raw.get("text") or "").strip()
                if not text:
                    continue
                result[key].append(
                    {
                        "text": text,
                        "label": str(raw.get("label") or "修饰成分").strip(),
                        "note": str(raw.get("note") or "").strip(),
                    }
                )

        for key in ("translationLayers", "examPoints"):
            raw_items = parsed.get(key)
            if isinstance(raw_items, list):
                result[key] = [
                    str(item).strip()
                    for item in raw_items[:6]
                    if str(item).strip()
                ]

        raw_grammar = parsed.get("grammar")
        if isinstance(raw_grammar, list):
            for raw in raw_grammar[:6]:
                if not isinstance(raw, dict):
                    continue
                name = str(raw.get("name") or "").strip()
                if name:
                    result["grammar"].append(
                        {"name": name, "note": str(raw.get("note") or "").strip()}
                    )

        def normalize_tree(raw_nodes: Any, depth: int = 0) -> list[dict[str, Any]]:
            if not isinstance(raw_nodes, list) or depth > 2:
                return []
            nodes: list[dict[str, Any]] = []
            for raw in raw_nodes[:6]:
                if not isinstance(raw, dict):
                    continue
                role = str(raw.get("role") or "").strip()
                label = str(raw.get("label") or "").strip()
                if not role or not label:
                    continue
                node: dict[str, Any] = {"role": role, "label": label}
                children = normalize_tree(raw.get("children"), depth + 1)
                if children:
                    node["children"] = children
                nodes.append(node)
            return nodes

        result["tree"] = normalize_tree(parsed.get("tree"))
        if not result["translationLayers"] and result["translation"]:
            result["translationLayers"] = [result["translation"]]
        if not result["tree"]:
            result["tree"] = [{"role": "整句", "label": sentence}]
        result["segments"] = [{"text": sentence, "tone": "slate", "label": ""}]
        return result
    except Exception as exc:  # noqa: BLE001
        logger.warning("sentence breakdown failed: %s", exc)
        return None


def analyze_ad_hoc_reading(
    passage: str,
    question: str,
    options: dict[str, str],
) -> dict[str, Any] | None:
    """Analyze an external pasted question without importing it into the bank."""
    if not is_configured():
        return None
    prompt = f"""请分析下面这道用户粘贴的考研英语阅读题，只输出 JSON。

文章：
{passage[:5000]}

题目：
{question}

选项：
{json.dumps(options, ensure_ascii=False, indent=2)}

输出格式：
{{
  "question_type": "细节题/主旨题/推理题/词义题/态度题",
  "correct_answer": "A/B/C/D",
  "analysis": {{
    "A": {{"trapType": "正确或无中生有等陷阱类型", "explanation": "中文解释"}},
    "B": {{"trapType": "...", "explanation": "..."}},
    "C": {{"trapType": "...", "explanation": "..."}},
    "D": {{"trapType": "...", "explanation": "..."}}
  }},
  "steps": ["步骤1", "步骤2", "步骤3"]
}}

要求：
1. 正确答案 trapType 必须是“正确”；错误项归入偷换概念、扩大范围、缩小范围、正反混淆、无中生有、过于绝对、过度推理、张冠李戴之一。
2. 每个错误项给出原文反证；原文没有的信息不要编造。
3. 如果信息不足以判断，correct_answer 仍给出最可能项，并在 explanation 中注明不确定。
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
            "max_tokens": 3000,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed or not isinstance(parsed.get("analysis"), dict):
            return None
        analysis: dict[str, dict[str, str]] = {}
        for key in ("A", "B", "C", "D"):
            info = parsed["analysis"].get(key) or {}
            analysis[key] = {
                "trapType": str(info.get("trapType") or "待分析"),
                "explanation": str(info.get("explanation") or "暂无解释"),
            }
        correct = str(parsed.get("correct_answer") or "").upper()[:1]
        if correct not in analysis:
            correct = next(
                (key for key, value in analysis.items() if value.get("trapType") == "正确"),
                "A",
            )
        return {
            "question_type": str(parsed.get("question_type") or "阅读题"),
            "correct_answer": correct,
            "analysis": analysis,
            "steps": [str(item) for item in (parsed.get("steps") or []) if item][:4],
        }
    except Exception:
        return None


def analyze_paragraph(text: str) -> dict[str, Any] | None:
    """Generate a compact discourse map for an external paragraph."""
    if not is_configured():
        return None
    prompt = f"""请分析下面这段英文的语篇结构，只输出 JSON。

段落：
{text[:6000]}

输出格式：
{{
  "main_idea": "一句话中文主旨",
  "topic_sentence": "原文中的主旨句",
  "sentences": [
    {{
      "index": 1,
      "text": "原句",
      "translation": "中文精译",
      "logic": "提出话题/强转折/例证/结论/因果/递进/让步/承接",
      "logic_note": "该句在段落中的功能",
      "stars": 1
    }}
  ],
  "logic_flow": [{{"from": 1, "to": 2, "label": "强转折"}}]
}}

要求：每句必须保留原文；不要编造原文没有的信息；stars 取值 1-5，表示句子难度。
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
            "max_tokens": 4000,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed or not isinstance(parsed.get("sentences"), list):
            return None
        sentences = []
        for index, item in enumerate(parsed["sentences"], start=1):
            if not isinstance(item, dict):
                continue
            sentences.append(
                {
                    "index": int(item.get("index") or index),
                    "text": str(item.get("text") or ""),
                    "translation": str(item.get("translation") or ""),
                    "logic": str(item.get("logic") or "承接"),
                    "logic_note": str(item.get("logic_note") or ""),
                    "stars": int(item.get("stars") or 1),
                }
            )
        return {
            "main_idea": str(parsed.get("main_idea") or ""),
            "topic_sentence": str(parsed.get("topic_sentence") or ""),
            "sentences": sentences,
            "logic_flow": parsed.get("logic_flow") or [],
        }
    except Exception:
        return None


def analyze_writing(prompt: str, draft: str) -> dict[str, Any] | None:
    """Review a learner's English writing with structured, minimal-edit feedback."""
    if not is_configured():
        return None
    text = f"""请批改下面这篇考研英语写作，只输出 JSON。

题目：
{prompt or '考研英语写作练习'}

学生作文：
{draft[:8000]}

输出格式：
{{
  "scores": {{"content": 0, "structure": 0, "language": 0, "task": 0}},
  "summary": "2-3 句中文总评",
  "issues": [
    {{"type": "grammar|vocabulary|structure|content", "quote": "原文片段", "suggestion": "最小修改", "reason": "为什么改"}}
  ],
  "minimum_revision": "保留学生原句的最小修改版（1 段）",
  "rewrite_excerpt": "更地道的示范段落（1 段）",
  "next_action": "下一步最值得练的 1 件事"
}}

要求：分数 0-5；issues 最多 6 条；优先给最小修改，不要把学生作文整篇重写；不要编造原文没有的内容。
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "temperature": 0.2,
            "max_tokens": 3000,
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
        return {
            "scores": parsed.get("scores") or {},
            "summary": str(parsed.get("summary") or ""),
            "issues": parsed.get("issues") or [],
            "minimum_revision": str(parsed.get("minimum_revision") or ""),
            "rewrite_excerpt": str(parsed.get("rewrite_excerpt") or ""),
            "next_action": str(parsed.get("next_action") or ""),
            "llm_used": True,
        }
    except Exception:
        return None


def summarize_reading(title: str, text: str) -> dict[str, Any]:
    """Summarize the current on-canvas article; extractive fallback is always available."""
    fallback = _extractive_summary(text)
    if not is_configured():
        return {"summary": fallback, "structure": [], "llm_used": False}
    prompt = f"""请用中文概括下面这篇英语文章，面向考研英语学习者。

标题：{title or '未命名文章'}

文章：
{text[:12000]}

只输出 JSON：
{{
  "summary": "3-5 句主旨概括，必须基于文章，不要编造",
  "structure": ["按段落或逻辑层次列出 3-6 条结构"],
  "key_takeaway": "作者最想让读者记住的一点"
}}
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1200,
            response_format={"type": "json_object"},
        )
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed:
            return {"summary": fallback, "structure": [], "llm_used": False}
        return {
            "summary": str(parsed.get("summary") or fallback),
            "structure": [str(item) for item in (parsed.get("structure") or [])],
            "key_takeaway": str(parsed.get("key_takeaway") or ""),
            "llm_used": True,
        }
    except Exception:
        return {"summary": fallback, "structure": [], "llm_used": False}


def _extractive_summary(text: str) -> str:
    sentences = [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", text.strip())
        if len(item.strip()) > 30
    ]
    if not sentences:
        return "当前文章还没有足够正文可供概括。"
    selected = sentences[:3]
    if len(sentences) > 4:
        selected.append(sentences[-1])
    return " ".join(selected)[:900]


def lookup_word_online(word: str) -> dict[str, Any] | None:
    """Look up an uncollected word/phrase and return learner-friendly Chinese data."""
    cleaned = word.strip()
    if not cleaned or not is_configured():
        return None
    prompt = f"""请查询下面这个英文单词或短语，面向考研英语学习者。不要编造不存在的词义。

词/短语：{cleaned}

只输出 JSON：
{{
  "found": true,
  "word": "原词或短语",
  "phonetic": "/.../",
  "part_of_speech": "n./v./adj./phr.",
  "basic_meanings": ["中文释义 1", "中文释义 2"],
  "rare_meaning": "熟词僻义或语境义；没有则空字符串",
  "collocations": ["搭配 1", "搭配 2"],
  "examples": [
    {{"en": "英文例句", "zh": "中文翻译"}}
  ],
  "is_proper_noun": false
}}

要求：
- 普通单词必须给出基础中文释义，不能因为首字母大写就判定为专有名词。
- 只有确实是品牌、机构、人名、地名等专有名词时，is_proper_noun 才为 true。
- 最多 3 条例句，最多 4 个搭配。
- 若这个词不存在或无法确认，found 为 false。
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20)
        kwargs: dict[str, Any] = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
            "response_format": {"type": "json_object"},
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception:
            kwargs.pop("response_format", None)
            response = client.chat.completions.create(**kwargs)
        parsed = _extract_json(response.choices[0].message.content or "")
        if not parsed or not parsed.get("found"):
            return None
        return {
            "found": True,
            "word": str(parsed.get("word") or cleaned),
            "phonetic": str(parsed.get("phonetic") or ""),
            "part_of_speech": str(parsed.get("part_of_speech") or ""),
            "basic_meanings": [str(x) for x in (parsed.get("basic_meanings") or []) if x],
            "rare_meaning": str(parsed.get("rare_meaning") or ""),
            "collocations": [str(x) for x in (parsed.get("collocations") or []) if x],
            "examples": [
                {"en": str(x.get("en") or ""), "zh": str(x.get("zh") or "")}
                for x in (parsed.get("examples") or [])
                if isinstance(x, dict) and x.get("en")
            ][:3],
            "is_proper_noun": bool(parsed.get("is_proper_noun")),
        }
    except Exception:
        return None
