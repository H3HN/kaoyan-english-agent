"""LLM-backed intent router constrained to the Skill catalog.

The model picks one skill name and optional slots. It never returns executable
code or arbitrary actions. Invalid/unsupported decisions fall back to the
deterministic planner.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from pydantic import BaseModel, Field

from llm import API_KEY, BASE_URL, MODEL, SYSTEM_PROMPT, _extract_json, is_configured

from .contracts import TurnIntent
from .skills import SKILL_NAMES, catalog_for_prompt
from .text import _external_english, _word_target, _writing_prompt


class IntentDecision(BaseModel):
    intent: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    args: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


def intent_router_enabled() -> bool:
    return os.getenv("AGENT_LLM_INTENT", "1").strip().lower() not in {
        "0", "false", "off", "no",
    }


def _context_summary(ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "current_route": ctx.get("current_route"),
        "active_passage_id": ctx.get("active_passage_id"),
        "active_sentence_id": ctx.get("active_sentence_id"),
        "selected_text": ctx.get("selected_raw_text"),
        "active_content_type": ctx.get("active_content_type"),
        "active_content_title": ctx.get("active_content_title"),
        "has_active_content": bool(str(ctx.get("active_content_text") or "").strip()),
        "recent_event": ctx.get("recent_event"),
    }


def _router_prompt(message: str, ctx: dict[str, Any]) -> str:
    return f"""你是学习 OS 的意图路由器，不负责回答知识问题。

用户输入：{message}

当前上下文：
{json.dumps(_context_summary(ctx), ensure_ascii=False)}

可选 Skill：
{json.dumps(catalog_for_prompt(), ensure_ascii=False)}

规则：
1. 只输出 JSON，不要回答用户问题。
2. 用户说“开始/我要/帮我/进入/打开/练/背/读/听/写”等动作时，优先选择能直接执行的动作 Skill。
3. 没有给正文却想泛读/听力/写作，选择对应的 *_home，不要选择内容 Skill。
4. 用户提供了英文正文时，内容 Skill 的正文由后端提取，不要复述正文。
5. 当前画布有 active_content 且用户问主旨/结构/总结，选择 summarize_content。
6. 没有合适 Skill 才选 generic；用户想学习但功能不存在，选 clarify。
7. 绝不要因为“方法/建议”而选 generic，如果用户是在请求执行学习动作。
8. confidence 低于 0.55 时仍返回 best guess，但后端会回退。

输出格式：
{{"intent":"skill_name","confidence":0.0,"args":{{}},"reason":"一句话"}}
"""


def _call_router(message: str, ctx: dict[str, Any]) -> IntentDecision | None:
    if not is_configured() or not intent_router_enabled():
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=12)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n你现在只做意图路由，不回答知识问题。"},
                {"role": "user", "content": _router_prompt(message, ctx)},
            ],
            temperature=0.0,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        raw = _extract_json(response.choices[0].message.content or "")
        if not raw:
            return None
        decision = IntentDecision.model_validate(raw)
        if decision.intent not in SKILL_NAMES:
            return None
        if decision.confidence < 0.55:
            return None
        return decision
    except Exception:
        return None


def _word_from_args(args: dict[str, Any], message: str) -> str:
    candidate = str(args.get("word") or "").strip()
    if re.fullmatch(r"[A-Za-z][A-Za-z'’\-]*(?: [A-Za-z][A-Za-z'’\-]*)?", candidate):
        return candidate
    return _word_target(message) or ""


def decision_to_intent(
    decision: IntentDecision,
    message: str,
    ctx: dict[str, Any],
) -> TurnIntent | None:
    """Validate a model decision against real runtime context."""
    name = decision.intent
    args = decision.args or {}
    active_content = str(ctx.get("active_content_text") or "").strip()
    active_sentence = ctx.get("active_sentence_data")
    active_sentence_id = ctx.get("active_sentence_id")
    external = _external_english(message) or ""

    if name in {
        "flashcard_review", "recommend", "practice", "schedule",
        "reading_home", "vocab_home", "studio_home", "clarify", "generic",
    }:
        return TurnIntent(name=name)

    if name == "reader_home":
        return TurnIntent(name="reader", payload={"text": external}) if external else TurnIntent(name="reader_home")
    if name == "listening_home":
        return TurnIntent(name="listening", payload={"text": external}) if external else TurnIntent(name="listening_home")
    if name == "writing_home":
        prompt = _writing_prompt(message) or str(args.get("prompt") or "").strip()
        if prompt:
            is_title_only = len(external.split()) <= len(prompt.split()) + 2
            return TurnIntent(
                name="writing",
                payload={"text": "" if is_title_only else external, "prompt": prompt},
            )
        return TurnIntent(name="writing", payload={"text": external}) if external else TurnIntent(name="writing_home")

    if name == "reader":
        if not external:
            return TurnIntent(name="reader_home")
        return TurnIntent(name="reader", payload={"text": external})

    if name == "listening":
        if not external:
            return TurnIntent(name="listening_home")
        return TurnIntent(name="listening", payload={"text": external})

    if name == "writing":
        prompt = _writing_prompt(message) or str(args.get("prompt") or "").strip()
        if prompt:
            is_title_only = len(external.split()) <= len(prompt.split()) + 2
            return TurnIntent(
                name="writing",
                payload={"text": "" if is_title_only else external, "prompt": prompt},
            )
        if not external:
            return TurnIntent(name="writing_home")
        return TurnIntent(name="writing", payload={"text": external})

    if name == "summarize_content":
        if not active_content:
            return None
        return TurnIntent(
            name="summarize_content",
            payload={
                "title": str(ctx.get("active_content_title") or "当前文章"),
                "text": active_content,
            },
        )

    if name == "word_insight":
        word = _word_from_args(args, message)
        if not word:
            return None
        return TurnIntent(name="word_insight", payload={"word": word})

    if name == "sentence":
        if external:
            return TurnIntent(name="ad_hoc_sentence", payload={"text": external})
        if not (active_sentence_id or ctx.get("active_passage_id") or ctx.get("selected_raw_text")):
            return None
        return TurnIntent(name="sentence")

    if name == "save_sentence":
        if not isinstance(active_sentence, dict):
            return None
        return TurnIntent(name="save_sentence", payload={"sentence_data": active_sentence})

    if name == "explain_word_in_sentence":
        if not isinstance(active_sentence, dict):
            return None
        word = _word_from_args(args, message) or str(ctx.get("selected_raw_text") or "")
        return TurnIntent(
            name="explain_word_in_sentence",
            payload={"word": word, "sentence_data": active_sentence},
        )

    if name == "add_word_to_sentence":
        if not isinstance(active_sentence, dict):
            return None
        return TurnIntent(
            name="add_word_to_sentence",
            payload={
                "word": _word_from_args(args, message) or str(ctx.get("selected_raw_text") or ""),
                "sentence_data": active_sentence,
                "analysis_id": active_sentence_id,
            },
        )

    if name == "batch_vocab":
        if not (active_content or ctx.get("active_passage_id")):
            return None
        return TurnIntent(name="batch_vocab")

    if name == "rare_words":
        if not (ctx.get("selected_raw_text") or active_sentence_id or active_content):
            return None
        return TurnIntent(name="rare_words")

    if name == "diagnosis":
        return TurnIntent(
            name="diagnosis",
            payload={
                "question_id": ctx.get("active_question_id"),
                "user_choice": (ctx.get("recent_event") or {}).get("user_choice"),
                "trap_type": (ctx.get("recent_event") or {}).get("trap_type"),
            },
        )

    if name == "similar_sentences":
        return TurnIntent(name="similar_sentences") if active_sentence_id else None

    if name == "explain_sentence":
        if not active_sentence_id:
            return None
        return TurnIntent(
            name="explain_sentence",
            payload={"sentence_id": active_sentence_id, "message": message},
        )

    return None


def infer_intent(message: str, ctx: dict[str, Any]) -> TurnIntent | None:
    decision = _call_router(message, ctx)
    if not decision:
        return None
    return decision_to_intent(decision, message, ctx)
