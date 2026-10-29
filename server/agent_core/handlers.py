"""Executable tool handlers for planner intents.

Each handler takes (connection, message, context, intent) and returns the
Agent response envelope. Handlers own domain work; the orchestrator only
dispatches and the planner only decides.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from sentence_library import add_word_from_sentence, save_current_sentence_to_library
from tools import check_syllabus_vocab, get_report
from workflows import run_chat_workflow, run_sentence_workflow

from .contracts import TurnIntent
from .reading import _diagnosis, _explain_current_sentence, _recommend, _similar_sentences
from .plan import _schedule
from .tools import (
    _ad_hoc_reading,
    _home,
    _summarize_content,
    _listening_insight,
    _reader_insight,
    _writing_insight,
    _ad_hoc_sentence,
    _ad_hoc_vocab,
    _batch_vocab,
    _paragraph_insight,
    _practice,
    _word_insight,
)


def _empty(intro: str, actions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "intro": intro,
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": actions or [],
        "widgets": [],
        "llm_used": False,
    }


def auto_diagnosis(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    result = _diagnosis(
        conn,
        intent.payload.get("question_id"),
        intent.payload.get("user_choice"),
        intent.payload.get("trap_type"),
    )
    return result or _empty("当前没有定位到具体错题。")


def save_sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    data = intent.payload.get("sentence_data") or {}
    if not isinstance(data, dict) or not data.get("sentence_en"):
        return _empty("当前没有可保存的句子。")
    result = save_current_sentence_to_library(
        conn,
        {
            "sentence_en": data.get("sentence_en", ""),
            "source_label": data.get("source_label", "自定义精析"),
            "sentence_data": data,
        },
    )
    return _empty(
        "已经把当前句子存入长难句库，之后可以从句库抽屉或生词本溯源回来。",
        [
            {
                "action_type": "SAVE_SENTENCE_STATE",
                "payload": {
                    "analysis_id": result["analysis_id"],
                    "source_label": result["source_label"],
                    "saved": True,
                },
            }
        ],
    )


def explain_word_in_sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    data = intent.payload.get("sentence_data") or {}
    word = str(intent.payload.get("word") or "").strip()
    if not word:
        return _empty("没有识别到要解释的单词。")
    sentence_text = str(data.get("sentence_en", ""))
    entries, trace = check_syllabus_vocab(conn, sentence_text)
    match = next((item for item in entries if item["word"].lower() == word.lower()), None)
    if match and match.get("in_syllabus") and match.get("basic_meaning"):
        intro = f"在“{sentence_text[:80]}…”中，{word} 的核心义是“{match['basic_meaning']}”。"
        if match.get("rare_meaning"):
            intro += f" 这里还带熟词僻义：{match['rare_meaning']}。"
    elif word[:1].isupper():
        intro = f"{word} 是专有名词（品牌/机构/人名），不是考研 5500 大纲词，不需要按大纲词背记。"
    elif match:
        intro = f"{word} 未进入考研大纲核心词表；先按当前句语境理解它的具体所指。"
    else:
        intro = f"词库没有收全 {word} 的独立释义，但从当前句语境看，它应结合上下文理解。"
    return {
        "intro": intro,
        "sections": [{"title": "当前语境", "body": sentence_text}],
        "tool_trace": [trace],
        "citations": [],
        "client_actions": [],
        "widgets": [],
        "llm_used": False,
    }


def add_word_to_sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    data = intent.payload.get("sentence_data") or {}
    word = str(intent.payload.get("word") or "").strip()
    if not word:
        return _empty("没有识别到要加入词本的单词。")
    result = add_word_from_sentence(
        conn,
        word=word,
        sentence_en=data.get("sentence_en", ""),
        sentence_data=data,
        analysis_id=intent.payload.get("analysis_id"),
        source_label=data.get("source_label", "自定义精析"),
    )
    actions: list[dict[str, Any]] = [
        {
            "action_type": "SAVE_SENTENCE_STATE",
            "payload": {
                "analysis_id": result["analysis_id"],
                "source_label": data.get("source_label", "自定义精析"),
                "saved": True,
            },
        }
    ]
    if result.get("ok"):
        actions.append({"action_type": "WORD_ADDED", "payload": {"word": word}})
    return {
        "intro": f"已把 {word} 连同当前原句语境收进生词本，并保存了这句话的溯源记录。",
        "sections": [],
        "tool_trace": [result.get("tool_trace", {})],
        "citations": [],
        "client_actions": actions,
        "widgets": [],
        "llm_used": False,
    }


def word_insight(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _word_insight(conn, str(intent.payload.get("word") or ""))


def ad_hoc_reading(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    result = _ad_hoc_reading(intent.payload.get("message") or message)
    return result or _empty("没有从输入中解析出题干与四个选项。")


def ad_hoc_vocab(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _ad_hoc_vocab(conn, str(intent.payload.get("text") or ""))


def paragraph(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _paragraph_insight(conn, str(intent.payload.get("text") or ""))


def ad_hoc_sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _ad_hoc_sentence(conn, str(intent.payload.get("text") or ""))


def recommend(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _recommend(conn)


def summarize_content(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _summarize_content(
        str(intent.payload.get("title") or ""),
        str(intent.payload.get("text") or ""),
    )


def studio_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _home("studio")


def reading_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _empty(
        "先选一套真题，再进入计时阅读。",
        [{"action_type": "NAVIGATE_TO", "payload": {"route": "/reading"}}],
    )


def vocab_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _empty(
        "先进入记忆舱，选择今日到期词或词测。",
        [{"action_type": "NAVIGATE_TO", "payload": {"route": "/vocab"}}],
    )


def listening_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _home("listening")


def writing_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _home("writing")


def reader_home(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _home("reader")


def listening(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    text = str(intent.payload.get("text") or "")
    if not text and not ctx.get("active_passage_id"):
        return _home("listening")
    return _listening_insight(conn, str(intent.payload.get("text") or ""), ctx)


def reader(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    text = str(intent.payload.get("text") or "")
    if not text:
        return _home("reader")
    return _reader_insight(text, ctx)


def writing(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    text = str(intent.payload.get("text") or "")
    prompt = str(intent.payload.get("prompt") or "")
    if not text and not prompt:
        return _home("writing")
    return _writing_insight(conn, text, prompt)


def practice(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _practice(conn)


def rare_words(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    raw = str(ctx.get("selected_raw_text") or "").strip()
    if not raw and ctx.get("active_content_text"):
        raw = str(ctx["active_content_text"]).strip()
    if not raw and ctx.get("active_sentence_id"):
        row = conn.execute(
            "SELECT text FROM exam_sentences WHERE id = ?",
            (ctx["active_sentence_id"],),
        ).fetchone()
        raw = row["text"] if row else ""
    if not raw:
        return _empty("先选中一个英文句子，我再查其中的熟词僻义。")
    entries, trace = check_syllabus_vocab(conn, raw)
    rare = [item for item in entries if item.get("rare_meaning")]
    return {
        "intro": f"这句里找到 {len(rare)} 个带熟词僻义的词。" if rare else "这句里没有检索到考研大纲中的熟词僻义。",
        "sections": [
            {
                "title": "熟词僻义",
                "items": [f"{item['word']}：{item['rare_meaning']}" for item in rare[:6]]
                or ["可以换一句，或把句子划选给我。"],
            }
        ],
        "tool_trace": [trace],
        "citations": [],
        "client_actions": [],
        "widgets": [],
        "llm_used": False,
    }


def batch_vocab(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _batch_vocab(conn, ctx)


def flashcard_review(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    report = get_report(conn)
    due = report["due_words"]
    total_words = conn.execute("SELECT COUNT(*) FROM user_vocab_book").fetchone()[0]
    if due:
        intro = f"今天有 {len(due)} 个单词到期。我已经打开闪卡抽屉，先做无提示回忆。"
        items = [f"{item['spelling']}：{item['meaning']}" for item in due[:6]]
        title = "今日到期"
    elif total_words:
        intro = (
            f"今天没有到期词。我已打开闪卡抽屉，本轮从词本 {total_words} 个词里随机抽卡，"
            "用“忘记 / 模糊 / 牢记”重新校准记忆。"
        )
        items = ["没有到期词，本轮使用整个词本作为新词/巩固队列。"]
        title = "今日策略"
    else:
        intro = "词本还是空的。先读一篇真题或泛读文章，把生词收进词本后就能开始闪卡。"
        items = ["打开今天下一步，先完成阅读或词汇采集。"]
        title = "还没有可背的词"
    actions = [{"action_type": "OPEN_FLASHCARD_DRAWER", "payload": {}}] if total_words else []
    return {
        "intro": intro,
        "sections": [{"title": title, "items": items}],
        "tool_trace": [],
        "citations": [],
        "client_actions": actions,
        "widgets": [],
        "llm_used": False,
    }


def schedule(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _schedule(conn)


def diagnosis(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    result = _diagnosis(
        conn,
        intent.payload.get("question_id"),
        intent.payload.get("user_choice"),
        intent.payload.get("trap_type"),
    )
    if result:
        return result
    return _empty(
        "当前页面还没有定位到具体题目。我先带你去联读室，选一道题后就能分析选项与定位句。",
        [{"action_type": "NAVIGATE_TO", "payload": {"route": "/reading"}}],
    )


def similar_sentences(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return _similar_sentences(conn, ctx)


def explain_sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    result = _explain_current_sentence(
        conn,
        str(intent.payload.get("sentence_id") or ""),
        str(intent.payload.get("message") or message),
    )
    return result or _empty("当前句还没有缓存拆解，请先在画布中完成五步分析。")


def sentence(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    sentence_id = ctx.get("active_sentence_id")
    row = None
    if sentence_id:
        row = conn.execute(
            "SELECT id, text, passage_id FROM exam_sentences WHERE id = ?",
            (sentence_id,),
        ).fetchone()
    if not row and ctx.get("active_passage_id"):
        row = conn.execute(
            "SELECT id, text, passage_id FROM exam_sentences WHERE passage_id = ? "
            "ORDER BY length(text) DESC LIMIT 1",
            (ctx["active_passage_id"],),
        ).fetchone()
    if not row and ctx.get("selected_raw_text"):
        snippet = str(ctx["selected_raw_text"]).strip()[:90].lower()
        row = conn.execute(
            "SELECT id, text, passage_id FROM exam_sentences "
            "WHERE lower(text) LIKE ? ORDER BY length(text) ASC LIMIT 1",
            (f"%{snippet}%",),
        ).fetchone()
    if not row:
        pasted = message.split("：", 1)[-1] if "：" in message else message
        snippet = pasted.strip()[:90].lower()
        if len(snippet) >= 18:
            row = conn.execute(
                "SELECT id, text, passage_id FROM exam_sentences "
                "WHERE lower(text) LIKE ? ORDER BY length(text) ASC LIMIT 1",
                (f"%{snippet}%",),
            ).fetchone()
    if not row:
        return _empty("没有定位到具体句子。可以直接把句子发给 Agent，或从画布中选中一句。")
    result = run_sentence_workflow(conn, row["id"])
    return {
        "intro": "我已经定位到当前句，打开长难句精析台可以看五步拆解。",
        "sections": [
            {
                "title": "当前句",
                "body": result["sentence"]["text"][:300] if result else row["text"][:300],
            }
        ],
        "tool_trace": result["tool_trace"] if result else [],
        "citations": result["citations"] if result else [],
        "client_actions": [
            {
                "action_type": "NAVIGATE_TO",
                "payload": {
                    "route": "/studio",
                    "sentence_id": row["id"],
                    "passage_id": row["passage_id"],
                },
            }
        ],
        "widgets": [],
        "llm_used": False,
    }


def clarify(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    return {
        "intro": "我可以直接开始。当前可以进入：背单词、阅读、听力、写作、泛读、长难句。告诉我一项，或直接在首页点对应入口。",
        "sections": [],
        "tool_trace": [],
        "citations": [],
        "client_actions": [],
        "widgets": [],
        "llm_used": False,
    }


def generic(conn, message, ctx, intent: TurnIntent) -> dict[str, Any]:
    base = run_chat_workflow(conn, message, ctx.get("active_passage_id") or "")
    return {
        "intro": base.get("intro", ""),
        "sections": base.get("sections", []),
        "tool_trace": base.get("tool_trace", []),
        "citations": base.get("citations", []),
        "client_actions": [],
        "widgets": [],
        "llm_used": bool(base.get("llm_used")),
    }
