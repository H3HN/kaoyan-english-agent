import json
import sqlite3
from typing import Any

from knowledge_cards import get_trap_card
from tools import check_syllabus_vocab, get_question, get_report, get_sentence, search_past_exams

def _diagnosis(
    conn: sqlite3.Connection,
    question_id: str | None,
    user_choice: str | None,
    trap_type: str | None,
) -> dict[str, Any] | None:
    payload = _question_payload(conn, question_id)
    if not payload:
        return None
    question = payload["question"]
    source = payload["source"]
    choice = (user_choice or "").upper()[:1]
    chosen = question["analysis"].get(choice, {})
    trap = trap_type or chosen.get("trapType") or "未归类"
    number = question["number"]
    source_text = source["text"] if source else question["content"]
    widget = {
        "widget_type": "TRAP_DIAGNOSIS",
        "data": {
            "question_id": question_id,
            "question_number": number,
            "user_choice": choice or None,
            "correct_choice": question["correct_answer"],
            "trap_type": trap,
            "method_card": get_trap_card(trap),
            "explanation": chosen.get("explanation", ""),
            "correct_explanation": payload["correct_analysis"].get("explanation", ""),
            "sentence_id": source["id"] if source else None,
            "sentence_text": source_text,
            "source": source["source"] if source else "题目定位",
        },
    }
    actions: list[dict[str, Any]] = []
    if source:
        actions.append(
            {
                "action_type": "HIGHLIGHT_SENTENCE",
                "payload": {
                    "sentence_id": source["id"],
                    "sentence_text": source_text,
                    "question_id": question_id,
                },
            }
        )
    actions.append(
        {
            "action_type": "REVEAL_OPTION_ANALYSIS",
            "payload": {"question_id": question_id},
        }
    )
    sections = [
        {
            "title": "名师点拨",
            "items": [
                f"误选 {choice or '未选'}：{trap}。{chosen.get('explanation', '')}",
                f"正确项 {question['correct_answer']}：{payload['correct_analysis'].get('explanation', '')}",
            ],
        },
    ]
    return {
        "intro": "我已经把这道题的错因、陷阱和原文定位串起来了。先看诊断卡，再回到定位句核对。",
        "sections": sections,
        "tool_trace": [],
        "citations": [],
        "client_actions": actions,
        "widgets": [widget],
        "llm_used": False,
    }


def _recommend(conn: sqlite3.Connection) -> dict[str, Any]:
    report = get_report(conn)
    weak = report["weak_types"][0]["type"] if report["weak_types"] else "阅读"
    row = conn.execute(
        """
        SELECT q.id, q.number, q.question_type, q.year, q.exam_type,
               q.text_number, q.passage_id
        FROM exam_questions q
        JOIN exam_passages p ON p.id = q.passage_id
        WHERE q.id NOT IN (SELECT question_id FROM practice_records)
          AND q.id LIKE 'auto_%'
        ORDER BY q.year DESC, q.text_number, q.number
        LIMIT 1
        """
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT id, number, question_type, year, exam_type, text_number, passage_id "
            "FROM exam_questions ORDER BY year DESC, text_number, number LIMIT 1"
        ).fetchone()
    if not row:
        return {
            "intro": "当前题库为空，请先在阅读训练页导入真题。",
            "sections": [],
            "tool_trace": [],
            "citations": [],
            "client_actions": [],
            "widgets": [],
            "llm_used": False,
        }
    reason = (
        f"你最近最薄弱的题型是「{weak}」，这篇的题号覆盖了同类定位与选项验伪。"
        if report["weak_types"]
        else "先按最新导入的完整篇章开始，保持每天一篇的阅读节奏。"
    )
    widget = {
        "widget_type": "PASSAGE_RECOMMEND",
        "data": {
            "passage_id": row["passage_id"],
            "year": row["year"],
            "exam_type": row["exam_type"],
            "text_number": row["text_number"],
            "question_id": row["id"],
            "question_number": row["number"],
            "question_type": row["question_type"],
            "reason": reason,
            "estimated_minutes": 8,
        },
    }
    return {
        "intro": f"今天建议先做 {row['year']} {row['exam_type']} Text {row['text_number']}。{reason} 已为你打开这篇阅读。",
        "sections": [
            {
                "title": "推荐依据",
                "items": [
                    f"历史正确率：{int(report['accuracy'] * 100)}%",
                    f"最薄弱题型：{weak}",
                    f"今日到期词：{len(report['due_words'])} 个",
                ],
            }
        ],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            {
                "action_type": "NAVIGATE_TO",
                "payload": {
                    "route": "/reading",
                    "year": row["year"],
                    "exam_type": row["exam_type"],
                    "text_number": row["text_number"],
                    "question_id": row["id"],
                },
            }
        ],
        "widgets": [widget],
        "llm_used": False,
    }


def _similar_sentences(conn: sqlite3.Connection, ctx: dict[str, Any]) -> dict[str, Any]:
    row = None
    if ctx.get("active_sentence_id"):
        row = conn.execute(
            "SELECT id, text, grammar_tags, source_label FROM exam_sentences WHERE id = ?",
            (ctx["active_sentence_id"],),
        ).fetchone()
    if not row and ctx.get("active_passage_id"):
        row = conn.execute(
            "SELECT id, text, grammar_tags, source_label FROM exam_sentences "
            "WHERE passage_id = ? ORDER BY length(text) DESC LIMIT 1",
            (ctx["active_passage_id"],),
        ).fetchone()
    if not row:
        return {
            "intro": "先打开一个句子，我才能按它的语法结构检索同款真题。",
            "sections": [],
            "tool_trace": [],
            "citations": [],
            "client_actions": [],
            "widgets": [],
            "llm_used": False,
        }
    import json

    tags = json.loads(row["grammar_tags"] or "[]")
    citations, trace = search_past_exams(conn, grammar=tags[:2], limit=3)
    return {
        "intro": f"按当前句的「{('、'.join(tags[:2]) or '语法结构')}」检索到 {len(citations)} 条历年真题切片。",
        "sections": [
            {
                "title": "同款语法",
                "items": [
                    f"{item['source']}：{item['text'][:130]}"
                    for item in citations
                ] or ["当前题库没有足够相似的同款句。"],
            }
        ],
        "tool_trace": [trace],
        "citations": citations,
        "client_actions": [],
        "widgets": [],
        "llm_used": False,
    }


def _explain_current_sentence(
    conn: sqlite3.Connection, sentence_id: str, question: str
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT id, text, source_label, passage_id FROM exam_sentences WHERE id = ?",
        (sentence_id,),
    ).fetchone()
    if not row:
        return None
    cached = conn.execute(
        "SELECT data_json FROM sentence_breakdowns WHERE sentence_id = ?",
        (sentence_id,),
    ).fetchone()
    if not cached:
        return None
    data = json.loads(cached["data_json"])
    clauses = data.get("clauses") or []
    modifiers = data.get("modifiers") or []
    target = "that" if "that" in question.lower() else ""
    relevant = [
        clause
        for clause in clauses
        if not target or target in str(clause.get("text", "")).lower()
    ]
    focus = relevant[0] if relevant else None
    intro = "我直接按当前画布上的五步拆解回答，不额外编造结构。"
    if focus:
        intro = (
            f"当前句中的 `{focus.get('text', '')}` 被标为「{focus.get('label', '从句')}」："
            f"{focus.get('note', '')}"
        )
    elif target:
        intro = "当前句的缓存拆解里没有出现 that 从句；我按现有拆解树给你核对主干、从句与修饰。"
    sections = [
        {
            "title": "主干",
            "body": f"{data.get('main', '')}\n{data.get('mainNote', '')}".strip(),
        },
        {
            "title": "从句与修饰",
            "items": [
                f"{item.get('label', '')}：{item.get('text', '')} —— {item.get('note', '')}"
                for item in (clauses + modifiers)[:5]
            ]
            or ["当前缓存拆解没有进一步拆分从句。"],
        },
        {
            "title": "整句翻译",
            "body": data.get("translation") or "当前缓存未提供翻译。",
        },
    ]
    return {
        "intro": intro,
        "sections": sections,
        "tool_trace": [],
        "citations": [],
        "client_actions": [],
        "widgets": [],
        "llm_used": False,
    }
