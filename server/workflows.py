import json
import sqlite3
from datetime import datetime
from typing import Any

from llm import is_configured, polish_chat
from tools import (
    add_to_vocab_book,
    check_syllabus_vocab,
    extract_words,
    get_meta,
    get_question,
    get_report,
    get_sentence,
    get_trap_rules,
    record_option_attempt,
    search_past_exams,
)

SENTENCE_MAIN = {
    "s4": {
        "code": "What remains clear is that the technology has become an inescapable part.",
        "body": "What remains clear 是主语从句，is 是系动词，that 引导表语从句；which 从句嵌套在表语从句内部，修饰 technology。",
        "points": [
            "主语从句 What remains clear 是主句主语，不要把 clear 误判为谓语。",
            "which 从句嵌套在表语从句内部，是本题最容易读丢的结构。",
            "raising 的逻辑主语是前面整个事实，不是 technology。",
        ],
        "translation": "有一点始终明确：这项曾经似乎只存在于科幻小说领域的技术，如今已成为我们日常生活中不可回避的一部分；这也引发了关于隐私、责任以及人类能力定义的种种问题。",
    }
}

OPTION_STATIC = {
    "2024_en1_t1-q1": {
        "location": "全文 · 首段总起 + 第三句转折",
        "core": "文章首句提出 excitement 与 anxiety 两面，随后分别展开支持者与批评者的观点，末句总结技术已进入日常生活并引发深层问题。",
    }
}


def _log_run(
    conn: sqlite3.Connection,
    workflow: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    tool_trace: list[dict[str, Any]],
) -> None:
    conn.execute(
        """
        INSERT INTO agent_runs (workflow, input_json, output_json, tool_trace_json)
        VALUES (?, ?, ?, ?)
        """,
        (
            workflow,
            json.dumps(input_payload, ensure_ascii=False),
            json.dumps(output_payload, ensure_ascii=False),
            json.dumps(tool_trace, ensure_ascii=False),
        ),
    )
    conn.commit()


def _top_vocab(entries: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    hits = [entry for entry in entries if entry["in_syllabus"]]
    hits.sort(
        key=lambda entry: (
            entry["rare_meaning"] is not None,
            entry["level"] == "核心",
            entry["exam_frequency"],
        ),
        reverse=True,
    )
    return hits[:limit]


def run_sentence_workflow(
    conn: sqlite3.Connection, sentence_id: str
) -> dict[str, Any] | None:
    sentence = get_sentence(conn, sentence_id)
    if not sentence:
        return None

    vocabulary, vocab_trace = check_syllabus_vocab(conn, sentence["text"])
    citations, citation_trace = search_past_exams(
        conn, grammar=sentence["grammar_tags"][:2], limit=4
    )
    top_vocab = _top_vocab(vocabulary)
    result = {
        "sentence": sentence,
        "vocabulary": top_vocab,
        "vocabulary_all_count": len([v for v in vocabulary if v["in_syllabus"]]),
        "citations": citations,
        "tool_trace": [vocab_trace, citation_trace],
    }
    _log_run(
        conn,
        "sentence",
        {"sentence_id": sentence_id},
        {
            "sentence_id": sentence_id,
            "vocab_count": len(top_vocab),
            "citation_count": len(citations),
        },
        result["tool_trace"],
    )
    return result


def run_options_workflow(
    conn: sqlite3.Connection,
    question_id: str,
    user_answer: str | None = None,
) -> dict[str, Any] | None:
    question = get_question(conn, question_id)
    if not question:
        return None

    source = (
        get_sentence(conn, question["source_sentence_id"])
        if question.get("source_sentence_id")
        else None
    )
    query = source["text"][:70] if source else question["content"][:50]
    citations, citation_trace = search_past_exams(conn, query=query, limit=3)
    record, record_trace = record_option_attempt(conn, question, user_answer)

    is_correct = (
        None if not user_answer else user_answer == question["correct_answer"]
    )
    result = {
        "question": question,
        "source_sentence": source,
        "citations": citations,
        "is_correct": is_correct,
        "selected_trap": (
            question["analysis"].get(user_answer, {}).get("trapType")
            if user_answer
            else None
        ),
        "record": record,
        "tool_trace": [citation_trace, record_trace],
    }
    _log_run(
        conn,
        "options",
        {"question_id": question_id, "user_answer": user_answer},
        {
            "question_id": question_id,
            "is_correct": is_correct,
            "selected_trap": result["selected_trap"],
        },
        result["tool_trace"],
    )
    return result


def _capability_text(conn: sqlite3.Connection) -> str:
    meta = get_meta(conn)
    return (
        f"当前领域库已载入 {meta['vocab_count']:,} 条考研词条、"
        f"{meta['passage_count']} 篇真题切片、{meta['trap_count']} 条陷阱规则。"
        "我可以在回答前调用大纲词库、真题检索、单词本归档与错题记录工具。"
    )


def _run_chat_deterministic(
    conn: sqlite3.Connection, message: str
) -> dict[str, Any]:
    text = message.lower()
    tool_trace: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []

    # 1) 写入单词本：展示 Agent 对软件状态的直接操作
    if "单词本" in message and any(
        key in message for key in ("加入", "记到", "归档", "收藏")
    ):
        vocabulary, vocab_trace = check_syllabus_vocab(conn, message)
        tool_trace.append(vocab_trace)
        candidates = [
            entry for entry in vocabulary if entry["in_syllabus"]
        ]
        if not candidates:
            return {
                "intro": "我没有在句子里识别到可归档的大纲词。请把单词单独发给我，例如“把 accountability 加入单词本”。",
                "sections": [],
                "tool_trace": tool_trace,
                "citations": [],
            }
        target = candidates[0]
        word, add_trace = add_to_vocab_book(
            conn,
            target["word"],
            context=message,
            source="Agent 对话归档",
        )
        tool_trace.append(add_trace)
        return {
            "intro": f"已经把 {target['word']} 归档到单词本。它的大纲等级是「{target['level']}」，在当前真题切片中出现 {target['exam_frequency']} 次。",
            "sections": [
                {
                    "title": "词条信息",
                    "items": [
                        f"常规释义：{target['basic_meaning'] or '未收录'}",
                        f"熟词僻义：{target['rare_meaning'] or '无'}",
                        f"复习安排：{word.get('nextReview', '明天')}",
                    ],
                },
                {
                    "title": "下一步",
                    "body": "单词本页会读取这条后端记录；下次复习时可以标记“记住/没记住”，SM-2 参数会继续更新。",
                },
            ],
            "tool_trace": tool_trace,
            "citations": [],
        }

    # 2) 长难句
    if any(key in message for key in ("从句", "长难句", "拆解", "句子")):
        result = run_sentence_workflow(conn, "s4")
        assert result
        tool_trace.extend(result["tool_trace"])
        citations.extend(result["citations"])
        vocab_items = []
        for item in result["vocabulary"][:10]:
            suffix = (
                f"；熟词僻义：{item['rare_meaning']}"
                if item["rare_meaning"]
                else ""
            )
            vocab_items.append(
                f"{item['word']}（{item['level']}，切片频次 {item['exam_frequency']}）：{item['basic_meaning']}{suffix}"
            )
        return {
            "intro": "这句话的难点不在词汇，而在三层嵌套。我先核对了大纲词库，再检索了同类真题切片。",
            "sections": [
                {
                    "title": "主干",
                    "code": SENTENCE_MAIN["s4"]["code"],
                    "body": SENTENCE_MAIN["s4"]["body"],
                },
                {
                    "title": "大纲词核验",
                    "items": vocab_items[:7],
                },
                {
                    "title": "真题溯源",
                    "items": [
                        f"[出处：{item['source']}] {item['text'][:110]}…"
                        for item in result["citations"][:3]
                    ],
                },
                {
                    "title": "考点",
                    "items": SENTENCE_MAIN["s4"]["points"],
                },
            ],
            "tool_trace": tool_trace,
            "citations": citations,
        }

    # 3) 选项陷阱
    if any(key in message for key in ("选项", "陷阱", "主旨题", "细节题")):
        result = run_options_workflow(conn, "2024_en1_t1-q1", None)
        assert result
        tool_trace.extend(result["tool_trace"])
        citations.extend(result["citations"])
        question = result["question"]
        option_items = [
            f"{key}. {info['trapType']}：{info['explanation']}"
            for key, info in question["analysis"].items()
        ]
        return {
            "intro": "这类题不要从“哪个像原文”入手，而是先定题型、再定位置，最后逐项验伪。",
            "sections": [
                {
                    "title": "题型与定位",
                    "items": [
                        f"题型：{question['question_type']}",
                        f"定位：{OPTION_STATIC['2024_en1_t1-q1']['location']}",
                        OPTION_STATIC["2024_en1_t1-q1"]["core"],
                    ],
                },
                {
                    "title": "四项定性",
                    "items": option_items,
                },
                {
                    "title": "真题溯源",
                    "items": [
                        f"[出处：{item['source']}] {item['text'][:110]}…"
                        for item in result["citations"][:2]
                    ],
                },
            ],
            "tool_trace": tool_trace,
            "citations": citations,
        }

    # 4) 熟词僻义
    if "熟词僻义" in message or any(
        word in text for word in ("address", "plant", "subject", "novel", "sound")
    ):
        words = extract_words(message)
        if not words:
            words = ["address", "plant", "subject", "novel", "sound"]
        vocabulary, vocab_trace = check_syllabus_vocab(conn, words)
        tool_trace.append(vocab_trace)
        rare = [item for item in vocabulary if item["rare_meaning"]]
        rare_items = [
            f"{item['word']}：{item['rare_meaning']}（常规释义：{item['basic_meaning']}）"
            for item in rare
        ] or ["这次没有命中含熟词僻义的词，可以试试 address / plant / subject / novel / sound。"]
        return {
            "intro": "考研阅读最怕“每个词都认识，句子还是读错”。熟词僻义要优先按语境判断，而不是背第一个释义。",
            "sections": [
                {
                    "title": "熟词僻义命中",
                    "items": rare_items,
                },
                {
                    "title": "判断方法",
                    "items": [
                        "先看搭配：be subject to / a school of thought / in this respect。",
                        "再看词性：address 作动词时更可能是“处理/致辞”。",
                        "最后回原文验证：把释义代入原句，看逻辑是否通顺。",
                    ],
                },
            ],
            "tool_trace": tool_trace,
            "citations": [],
        }

    # 5) 复习计划
    if any(key in message for key in ("计划", "复习", "单词")):
        report = get_report(conn)
        due = report["due_words"]
        due_items = [
            f"{item['spelling']}：{item['meaning']}（下次复习 {item['nextReview'][:10]}）"
            for item in due[:6]
        ] or ["今天没有到期单词，可以开始新的阅读。"]
        return {
            "intro": "先处理到期词，再安排新词。复习计划按“到期优先、薄弱词加权、每天不超过 20 分钟”来排。",
            "sections": [
                {
                    "title": "今天",
                    "items": due_items,
                },
                {
                    "title": "本周",
                    "items": [
                        "周一 / 周三 / 周五各安排一次 15 分钟复习。",
                        "没记住的词明天再来一次；记住的词按 2、4、7、15、30 天拉开。",
                        "周末用 2024 Text 1 做一次整篇回读，把词放回原句。",
                    ],
                },
                {
                    "title": "学习记录",
                    "items": report["suggestions"][:3],
                },
            ],
            "tool_trace": tool_trace,
            "citations": [],
        }

    # 6) 段落主旨
    if any(key in message for key in ("主旨", "总结", "段落", "态度")):
        citations, search_trace = search_past_exams(
            conn, query="artificial intelligence", limit=2
        )
        tool_trace.append(search_trace)
        return {
            "intro": "这段文字不是单纯介绍 AI，而是在“兴奋”与“焦虑”之间保持张力。主旨题要选的，是能同时覆盖两面的概括项。",
            "sections": [
                {
                    "title": "段落结构",
                    "items": [
                        "首句总起：AI 同时引发 excitement 与 anxiety。",
                        "第二句：支持者强调产业升级与新岗位。",
                        "第三句：批评者警告岗位流失与重复性劳动。",
                        "末句收束：技术已进入日常生活，并带来隐私、责任与能力定义的追问。",
                    ],
                },
                {
                    "title": "一句话主旨",
                    "body": "人工智能在带来产业变革的同时，也引发了就业、隐私与责任层面的深层争议。",
                },
                {
                    "title": "作者态度",
                    "items": [
                        "谨慎中立，不是盲目乐观，也不是全盘否定。",
                        "末句的 raising questions 说明作者更关心技术带来的未解问题。",
                        "主旨题优先排除 definitely、all、only 这类绝对化概括。",
                    ],
                },
                {
                    "title": "真题溯源",
                    "items": [
                        f"[出处：{item['source']}] {item['text'][:110]}…"
                        for item in citations
                    ],
                },
            ],
            "tool_trace": tool_trace,
            "citations": citations,
        }

    # 7) 默认：能力与数据状态
    meta = get_meta(conn)
    return {
        "intro": _capability_text(conn),
        "sections": [
            {
                "title": "可以调用的工具",
                "items": [
                    "check_syllabus_vocab：核查大纲属性、考频与熟词僻义。",
                    "search_past_exams：检索真题切片并强制标注出处。",
                    "add_to_vocab_book：把生词和语境写入单词本。",
                    "record_trap_mistake：记录误选陷阱，更新薄弱画像。",
                ],
            },
            {
                "title": "当前领域数据",
                "items": [
                    f"考研词条：{meta['vocab_count']:,} 条",
                    f"真题切片：{meta['sentence_count']} 句 / {meta['question_count']} 题",
                    f"陷阱规则：{meta['trap_count']} 条",
                ],
            },
        ],
        "tool_trace": tool_trace,
        "citations": [],
    }


def get_trap_knowledge(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return get_trap_rules(conn)


def run_chat_workflow(
    conn: sqlite3.Connection, message: str
) -> dict[str, Any]:
    """Deterministic tools first, optional LLM rewrite second.

    Tool traces and citations are never generated by the model. The LLM only
    rewrites the teaching prose, so a failed or hallucinated model call cannot
    break provenance or software state.
    """
    base = _run_chat_deterministic(conn, message)
    if not is_configured():
        base["llm_used"] = False
        return base

    # State-changing confirmations stay deterministic.
    if any(
        item.get("tool") == "add_to_vocab_book"
        for item in base.get("tool_trace", [])
    ):
        base["llm_used"] = False
        return base

    polished = polish_chat(message, base)
    if polished:
        base["intro"] = polished["intro"]
        base["sections"] = polished["sections"]
        base["llm_used"] = True
    else:
        base["llm_used"] = False
    return base
