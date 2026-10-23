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
            "temperature": 0.35,
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
