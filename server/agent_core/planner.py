"""Turn planner: converts a message + client context into a tool intent.

The planner is deliberately deterministic. It may read the client context and
the message text, but it never calls an LLM or a database tool. The
orchestrator is responsible for executing the selected intent.
"""
from __future__ import annotations

import re
from typing import Any

from .contracts import TurnIntent
from .text import _external_english, _sentence_parts, _word_target, _writing_prompt

SAVE_KEYS = ("把这句话存起来", "收藏这句", "保存这个句子", "存进句库", "加入句库")
WORD_CONTEXT_KEYS = ("词性", "语义", "语法功能", "什么意思", "意思")
SENTENCE_INTENT_KEYS = (
    "翻译", "拆解", "分析", "长难句", "句子", "语法", "成分", "精析", "这句", "这段",
)
RECOMMEND_KEYS = (
    "今天读什么", "读哪篇", "推荐一篇", "推荐阅读", "今天学什么",
    "今天要阅读", "阅读的文章", "带我去",
)
PRACTICE_KEYS = ("随便", "来一", "出一", "练一", "做一", "做题", "刷题", "给我一", "给我道", "推荐")
VOCAB_KEYS = ("生词", "核心词", "单词", "词汇", "词表", "挑出", "提取")
RARE_KEYS = ("熟词僻义",)
BATCH_KEYS = ("整理", "入库", "收了", "加入", "提取", "提炼")
FLASHCARD_KEYS = (
    "抽查", "背单词", "背词", "背诵", "闪卡", "到期词", "复习词",
    "今日单词", "复习单词", "单词复习", "开始背",
)
PLAN_KEYS = ("计划", "排课", "安排本周", "安排今天")
DIAGNOSIS_KEYS = ("错题", "这道题", "本题", "四个选项", "剖析", "分析选项", "错在哪")
SIMILAR_KEYS = ("同款语法", "同语法", "同结构", "同款句")
FOLLOWUP_KEYS = ("为什么", "同位语", "定语", "that", "这里的", "这个")
SENTENCE_KEYS = ("拆解", "从句", "长难句")
ACTION_REQUEST_KEYS = ("我要", "我想", "帮我", "带我", "开始", "进入", "打开", "继续", "练")
ACTION_FEATURE_KEYS = ("单词", "词汇", "阅读", "听力", "口语", "写作", "翻译", "泛读", "长难句", "计划", "闪卡")
QUESTION_KEYS = ("怎么", "为什么", "是什么", "区别", "如何", "吗", "？", "?")


def normalized_text(message: str) -> str:
    return (message or "").lower()


def is_auto_diagnosis(trigger_mode: str, event: dict[str, Any]) -> bool:
    return trigger_mode == "AUTO_EVENT" and event.get("event_type") == "QUESTION_SUBMITTED"


def _word_intent(text: str) -> bool:
    return any(
        key in text
        for key in ("单词", "短语", "词语", "什么意思", "释义", "解析一下", "看看这个词", "这词")
    )


def plan_turn(
    message: str,
    ctx: dict[str, Any],
    trigger_mode: str = "USER_CHAT",
) -> TurnIntent:
    text = normalized_text(message)
    event = ctx.get("recent_event") or {}
    active_sentence_data = ctx.get("active_sentence_data")

    if is_auto_diagnosis(trigger_mode, event):
        return TurnIntent(
            name="auto_diagnosis",
            payload={
                "question_id": event.get("question_id") or ctx.get("active_question_id"),
                "user_choice": event.get("user_choice"),
                "trap_type": event.get("trap_type"),
            },
        )

    if any(key in text for key in SAVE_KEYS) and isinstance(active_sentence_data, dict):
        return TurnIntent(name="save_sentence", payload={"sentence_data": active_sentence_data})

    active_content_text = str(ctx.get("active_content_text") or "").strip()
    if active_content_text and any(
        key in text
        for key in ("主旨", "大意", "概括", "总结", "这篇文章", "全文", "文章结构", "讲了什么")
    ):
        return TurnIntent(
            name="summarize_content",
            payload={
                "title": str(ctx.get("active_content_title") or "当前文章"),
                "text": active_content_text,
            },
        )

    if isinstance(active_sentence_data, dict) and any(
        key in text for key in WORD_CONTEXT_KEYS
    ):
        word = str(ctx.get("selected_raw_text") or "").strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z'’\-]*", word):
            words = re.findall(r"[A-Za-z][A-Za-z'’\-]{2,}", message)
            word = words[-1] if words else ""
        return TurnIntent(
            name="explain_word_in_sentence",
            payload={"word": word, "sentence_data": active_sentence_data},
        )

    if isinstance(active_sentence_data, dict) and "加入生词本" in text and "句" in text:
        words = re.findall(r"[A-Za-z][A-Za-z'’\-]{2,}", message)
        return TurnIntent(
            name="add_word_to_sentence",
            payload={
                "word": words[-1] if words else "",
                "sentence_data": active_sentence_data,
                "analysis_id": ctx.get("active_sentence_id"),
            },
        )

    if any(key in text for key in ("进入studio", "进入 studio", "学习首页", "训练首页", "进入长难句", "开始学习", "继续学习")):
        return TurnIntent(name="studio_home")
    if any(key in text for key in ("进入阅读", "打开阅读", "阅读首页", "开始阅读", "做阅读", "阅读训练")):
        return TurnIntent(name="reading_home")
    if any(key in text for key in ("进入词汇", "打开词本", "词汇首页")):
        return TurnIntent(name="vocab_home")

    if any(key in text for key in ("写作", "作文", "批改")):
        writing_prompt = _writing_prompt(message)
        external = _external_english(message) or ""
        if writing_prompt:
            is_title_only = len(external.split()) <= len(writing_prompt.split()) + 2
            return TurnIntent(
                name="writing",
                payload={
                    "text": "" if is_title_only else external,
                    "prompt": writing_prompt,
                },
            )
        if external:
            return TurnIntent(name="writing", payload={"text": external})
        return TurnIntent(name="writing_home")

    word_target = _word_target(message)
    short_english = (
        len(re.findall(r"[A-Za-z][A-Za-z'’\-]*", message)) <= 3
        and not _external_english(message)
    )
    if word_target and (_word_intent(text) or short_english):
        return TurnIntent(name="word_insight", payload={"word": word_target})

    if any(key in text for key in ("听力", "听写", "磨耳朵")):
        external = _external_english(message)
        if external:
            return TurnIntent(name="listening", payload={"text": external})
        return TurnIntent(name="listening_home")

    external = _external_english(message)
    if any(key in text for key in ("泛读", "长文")):
        if external:
            return TurnIntent(name="reader", payload={"text": external})
        return TurnIntent(name="reader_home")
    if external:
        if any(key in text for key in ("选项", "题目", "阅读题", "这道题", "分析选项")):
            return TurnIntent(name="ad_hoc_reading", payload={"message": message})
        if any(key in text for key in VOCAB_KEYS):
            return TurnIntent(name="ad_hoc_vocab", payload={"text": external})
        sentence_count = len(_sentence_parts(external))
        word_count = len(re.findall(r"[A-Za-z][A-Za-z'’\-]*", external))
        if word_count >= 220 or sentence_count >= 8:
            return TurnIntent(name="reader", payload={"text": external})
        if sentence_count >= 3 or word_count >= 45:
            return TurnIntent(name="paragraph", payload={"text": external})
        if (
            any(key in text for key in SENTENCE_INTENT_KEYS) or word_count >= 8
        ) and not any(key in text for key in ("今天读什么", "读哪篇", "推荐")):
            return TurnIntent(name="ad_hoc_sentence", payload={"text": external})

    if any(key in text for key in RECOMMEND_KEYS):
        return TurnIntent(name="recommend")

    if "题" in text and any(key in text for key in PRACTICE_KEYS):
        return TurnIntent(name="practice")

    if any(key in text for key in RARE_KEYS) and not any(
        key in text for key in ("入库", "加入", "整理", "提取", "提炼")
    ):
        return TurnIntent(name="rare_words")

    if any(key in text for key in VOCAB_KEYS) and any(key in text for key in BATCH_KEYS):
        return TurnIntent(name="batch_vocab")

    if any(key in text for key in FLASHCARD_KEYS):
        return TurnIntent(name="flashcard_review")

    if any(key in text for key in PLAN_KEYS):
        return TurnIntent(name="schedule")

    if any(key in text for key in DIAGNOSIS_KEYS):
        return TurnIntent(
            name="diagnosis",
            payload={
                "question_id": ctx.get("active_question_id"),
                "user_choice": event.get("user_choice"),
                "trap_type": event.get("trap_type"),
            },
        )

    if any(key in text for key in SIMILAR_KEYS):
        return TurnIntent(name="similar_sentences")

    if (
        ctx.get("current_route") in ("/studio", "/sentence")
        and ctx.get("active_sentence_id")
        and any(key in text for key in FOLLOWUP_KEYS)
    ):
        return TurnIntent(
            name="explain_sentence",
            payload={
                "sentence_id": ctx["active_sentence_id"],
                "message": message,
            },
        )

    if any(key in text for key in SENTENCE_KEYS):
        return TurnIntent(name="sentence")

    if (
        any(key in text for key in ACTION_REQUEST_KEYS)
        and any(key in text for key in ACTION_FEATURE_KEYS)
        and not any(key in text for key in QUESTION_KEYS)
    ):
        return TurnIntent(name="clarify")

    return TurnIntent(name="generic")
