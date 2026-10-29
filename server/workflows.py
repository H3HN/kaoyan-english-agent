import json
import sqlite3
from datetime import datetime
from typing import Any

from llm import analyze_sentence_breakdown, is_configured, polish_chat
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

def _get_sentence_breakdown(
    conn: sqlite3.Connection, sentence_id: str, sentence_text: str
) -> dict[str, Any] | None:
    cached = conn.execute(
        "SELECT data_json FROM sentence_breakdowns WHERE sentence_id = ?",
        (sentence_id,),
    ).fetchone()
    if cached:
        try:
            return json.loads(cached["data_json"])
        except json.JSONDecodeError:
            return None
    data = analyze_sentence_breakdown(sentence_text)
    if not data:
        return None
    conn.execute(
        "INSERT OR REPLACE INTO sentence_breakdowns (sentence_id, data_json, llm_used) VALUES (?, ?, 1)",
        (sentence_id, json.dumps(data, ensure_ascii=False)),
    )
    conn.commit()
    return data


def _context(conn: sqlite3.Connection, context_id: str):
    passage = conn.execute(
        """
        SELECT p.*
        FROM exam_passages AS p
        WHERE p.id = ? AND p.publication_status = 'published'
        """,
        (context_id,),
    ).fetchone()
    if not passage:
        passage = conn.execute(
            """
            SELECT p.*
            FROM exam_passages AS p
            WHERE p.publication_status = 'published'
            ORDER BY p.year DESC, p.text_number, p.id
            LIMIT 1
            """
        ).fetchone()
    if not passage:
        return None, [], []
    sentences = conn.execute(
        """
        SELECT s.id, s.text
        FROM exam_sentences AS s
        JOIN exam_passages AS p ON p.id = s.passage_id
        WHERE s.passage_id = ? AND p.publication_status = 'published'
        ORDER BY s.paragraph, s.sentence_index
        """,
        (passage["id"],),
    ).fetchall()
    questions = conn.execute(
        """
        SELECT q.id
        FROM exam_questions AS q
        JOIN exam_passages AS p ON p.id = q.passage_id
        WHERE q.passage_id = ? AND p.publication_status = 'published'
        ORDER BY q.number
        """,
        (passage["id"],),
    ).fetchall()
    return passage, sentences, questions


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
    # 当前句必须出现在引用里，不能被同语法标签的其他年份挤出。
    own_citation = {
        "id": sentence["id"],
        "source": sentence["source"],
        "year": sentence["year"],
        "exam_type": sentence["exam_type"],
        "text": sentence["text"],
        "grammar_tags": sentence["grammar_tags"],
    }
    citations = [own_citation] + [
        item
        for item in citations
        if item["id"] != sentence["id"]
        and item.get("passage_id") == sentence["passage_id"]
    ][:3]
    citation_trace["summary"] = (
        f"定位到当前篇 {len(citations)} 条真题切片，"
        f"优先引用 {sentence['source']}"
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
    conn: sqlite3.Connection, message: str, context_id: str = ""
) -> dict[str, Any]:
    text = message.lower()
    passage, context_sentences, context_questions = _context(conn, context_id)
    tool_trace: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    if passage is None:
        return {
            "intro": "当前没有已发布的真题篇章，请等待管理员审核发布后再选择学习内容。",
            "sections": [],
            "tool_trace": tool_trace,
            "citations": citations,
            "llm_policy": "deterministic",
        }

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
            "llm_policy": "deterministic",
        }

    # 2) 长难句
    if any(key in message for key in ("从句", "长难句", "拆解", "句子")):
        if not context_sentences:
            return {
                "intro": "当前上下文没有可拆解的句子，请先在阅读训练页导入文章。",
                "sections": [],
                "tool_trace": tool_trace,
                "citations": [],
                "llm_policy": "deterministic",
            }
        sentence_id = max(
            context_sentences, key=lambda row: len(row["text"])
        )["id"]
        result = run_sentence_workflow(conn, sentence_id)
        assert result
        breakdown = _get_sentence_breakdown(
            conn, sentence_id, result["sentence"]["text"]
        )
        static = None
        if breakdown:
            static = {
                "code": breakdown.get("main") or result["sentence"]["text"],
                "body": breakdown.get("mainNote") or "",
                "points": (breakdown.get("examPoints") or [])[:4]
                or ["先找谓语，再判断从句修饰对象。"],
                "translation": breakdown.get("translation") or "",
            }
        if not static:
            static = {
                "code": result["sentence"]["text"],
                "body": "先找主干，再剥离从句与修饰，最后回到中文语序。",
                "points": ["结合工具返回的语法标签逐层拆解。"],
                "translation": "",
            }
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
            "intro": "这句话的难点不在词汇，而在结构层次。我先核对了大纲词库，再检索了同类真题切片。",
            "sections": [
                {
                    "title": "主干",
                    "code": static["code"],
                    "body": static["body"],
                },
                *(
                    [
                        {
                            "title": "从句与修饰",
                            "items": [
                                f"{item.get('label', '修饰')}：{item.get('text', '')}（{item.get('note', '')}）"
                                for item in [
                                    *(breakdown.get("clauses") or []),
                                    *(breakdown.get("modifiers") or []),
                                ][:6]
                            ],
                        }
                    ]
                    if breakdown
                    and (
                        breakdown.get("clauses")
                        or breakdown.get("modifiers")
                    )
                    else []
                ),
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
                    "items": static["points"],
                },
            ],
            "tool_trace": tool_trace,
            "citations": citations,
            "llm_policy": "deterministic",
        }

    # 3) 选项陷阱
    if any(key in message for key in ("选项", "陷阱", "错误选项", "排除")):
        if not context_questions:
            return {
                "intro": "当前上下文还没有题目，请先在阅读训练页导入完整文章。",
                "sections": [],
                "tool_trace": tool_trace,
                "citations": [],
                "llm_policy": "deterministic",
            }
        question_id = context_questions[0]["id"]
        result = run_options_workflow(conn, question_id, None)
        assert result
        option_location = (
            result["source_sentence"]["source"]
            if result.get("source_sentence")
            else "自定义导入"
        )
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
                        f"定位：{option_location}",
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
            "llm_policy": "deterministic",
        }

    # 4) 熟词僻义
    wants_core_words = any(
        key in message for key in ("核心词", "关键词", "生词", "词汇")
    )
    if (
        "熟词僻义" in message and not wants_core_words
    ) or any(
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

    # 5) 核心词提炼（上下文驱动）
    if any(key in message for key in ("核心词", "关键词", "生词", "词汇")):
        message_words = extract_words(message)
        if message_words:
            source_text = " ".join(message_words)
        else:
            source_text = " ".join(row["text"] for row in context_sentences)
        vocabulary, vocab_trace = check_syllabus_vocab(conn, source_text)
        tool_trace.append(vocab_trace)
        hits = [item for item in vocabulary if item["in_syllabus"]]
        hits.sort(
            key=lambda item: (
                item["rare_meaning"] is not None,
                item["level"] == "核心",
                item["exam_frequency"],
            ),
            reverse=True,
        )
        items = [
            f"{item['word']}（{item['level']}，切片频次 {item['exam_frequency']}）：{item['basic_meaning']}"
            + (f"；熟词僻义：{item['rare_meaning']}" if item["rare_meaning"] else "")
            for item in hits[:8]
        ] or ["当前上下文未命中大纲词。"]
        return {
            "intro": f"从当前篇章筛出 {len(hits)} 个大纲词，按核心度与切片频次排序。",
            "sections": [
                {"title": "核心词", "items": items},
                {
                    "title": "复习建议",
                    "body": "优先记搭配与原句语境；可直接把上方词条加入单词本。",
                },
            ],
            "tool_trace": tool_trace,
            "citations": [],
            "llm_policy": "deterministic",
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
                        f"周末用 {passage['year']} {passage['exam_type']} Text {passage['text_number']} 做一次整篇回读，把词放回原句。",
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

    # 7) 段落主旨
    if any(key in message for key in ("主旨", "总结", "段落", "态度")):
        first_sentence = (
            get_sentence(conn, context_sentences[0]["id"])
            if context_sentences
            else None
        )
        last_sentence = (
            get_sentence(conn, context_sentences[-1]["id"])
            if context_sentences
            else None
        )
        loc_items = []
        for question_row in context_questions[:3]:
            question = get_question(conn, question_row["id"])
            if not question:
                continue
            source_row = (
                get_sentence(conn, question["source_sentence_id"])
                if question.get("source_sentence_id")
                else None
            )
            loc_items.append(
                f"第 {question['number']} 题："
                + (
                    source_row["text"][:150]
                    if source_row
                    else question["content"][:150]
                )
            )
        citations = [
            {
                "id": item["id"],
                "source": item["source"],
                "text": item["text"],
                "year": passage["year"],
                "exam_type": passage["exam_type"],
                "text_number": passage["text_number"],
                "grammar_tags": [],
            }
            for item in (first_sentence, last_sentence)
            if item
        ]
        return {
            "intro": f"当前篇章共 {len(context_sentences)} 句。以下只抽取原文首尾与题干定位，不做无依据的主旨概括。",
            "sections": [
                {
                    "title": "原文首句",
                    "body": first_sentence["text"] if first_sentence else "暂无",
                },
                {
                    "title": "原文末句",
                    "body": last_sentence["text"] if last_sentence else "暂无",
                },
                {
                    "title": "题干定位",
                    "items": loc_items
                    or ["该篇章暂无已导入题目，可先在阅读训练页添加。"],
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
            "llm_policy": "deterministic",
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
    conn: sqlite3.Connection, message: str, context_id: str = ""
) -> dict[str, Any]:
    """Deterministic tools first, optional LLM rewrite second.

    Tool traces and citations are never generated by the model. The LLM only
    rewrites the teaching prose, so a failed or hallucinated model call cannot
    break provenance or software state.
    """
    base = _run_chat_deterministic(conn, message, context_id)
    if base.get("llm_policy") == "deterministic":
        base["llm_used"] = False
        return base
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
