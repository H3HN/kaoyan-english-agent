import sqlite3
from typing import Any

from sentence_library import add_word_from_sentence
from tools import add_to_vocab_book, check_syllabus_vocab

from ..canvas import _canvas_action

def _ad_hoc_vocab(conn: sqlite3.Connection, source_text: str) -> dict[str, Any]:
    entries, trace = check_syllabus_vocab(conn, source_text)
    existing = {
        row["spelling"]
        for row in conn.execute("SELECT spelling FROM user_vocab_book").fetchall()
    }
    candidates = [
        item
        for item in entries
        if item.get("in_syllabus") and item["word"].lower() not in existing
    ][:8]
    added: list[dict[str, Any]] = []
    for item in candidates:
        word, _ = add_to_vocab_book(
            conn,
            item["word"],
            context=source_text[:500],
            source="自定义输入 · 实时提取",
        )
        if word:
            added.append(
                {
                    "word": item["word"],
                    "meaning": item.get("basic_meaning", ""),
                    "rare": item.get("rare_meaning"),
                    "source": "自定义输入 · 实时提取",
                }
            )
    added_words = {item["word"] for item in added}
    all_words = [
        {
            "word": item["word"],
            "meaning": item.get("basic_meaning", ""),
            "rare": item.get("rare_meaning"),
            "source": "自定义输入 · 实时提取",
            "status": "new" if item["word"] in added_words else "existing",
        }
        for item in entries
        if item.get("in_syllabus")
    ][:12]
    data = {
        "source_text": source_text[:800],
        "added": added,
        "words": all_words,
        "skipped": len([item for item in all_words if item["status"] == "existing"]),
        "total": len(all_words),
    }
    return {
        "intro": (
            f"已从这段外源文本中提取 {data['total']} 个考研大纲词，"
            f"其中 {len(added)} 个新词已收进词本。左侧切到本次新增词视图。"
        ),
        "sections": [],
        "tool_trace": [trace],
        "citations": [],
        "client_actions": [
            _canvas_action("vocab", data, "外源生词提取")
        ],
        "widgets": [],
        "llm_used": False,
    }


def _batch_vocab(conn: sqlite3.Connection, ctx: dict[str, Any]) -> dict[str, Any]:
    source_text = str(ctx.get("active_content_text") or "").strip()
    source_label = str(ctx.get("active_content_title") or "").strip()
    passage_id = None
    if not source_text and ctx.get("active_passage_id"):
        passage = conn.execute(
            "SELECT * FROM exam_passages WHERE id = ?", (ctx["active_passage_id"],)
        ).fetchone()
        if passage:
            source_text = passage["text"]
            source_label = f"{passage['year']} {passage['exam_type']} Text {passage['text_number']}"
            passage_id = passage["id"]
    if not source_text:
        return {
            "intro": "当前画布还没有可扫描的文章。先打开泛读、段落或阅读训练，再提取生词。",
            "sections": [],
            "tool_trace": [],
            "citations": [],
            "client_actions": [],
            "widgets": [],
            "llm_used": False,
        }
    entries, trace = check_syllabus_vocab(conn, source_text)
    existing = {
        row["spelling"]
        for row in conn.execute("SELECT spelling FROM user_vocab_book").fetchall()
    }
    candidates = [
        item
        for item in entries
        if item["in_syllabus"] and item["word"].lower() not in existing
    ][:6]
    added: list[dict[str, Any]] = []
    for item in candidates:
        word, _ = add_to_vocab_book(
            conn,
            item["word"],
            context=source_text[:500],
            source=source_label or "当前画布",
        )
        if word:
            added.append(
                {
                    "word": item["word"],
                    "meaning": item["basic_meaning"],
                    "rare": item["rare_meaning"],
                    "source": source_label or "当前画布",
                }
            )
    widget = {
        "widget_type": "VOCAB_BATCH_SAVED",
        "data": {
            "added_count": len(added),
            "skipped_count": max(0, len(candidates) - len(added)),
            "words": added[:4],
            "passage_id": passage_id,
        },
    }
    return {
        "intro": f"已从《{source_label or '当前画布'}》扫描生词，新增 {len(added)} 个到词本。",
        "sections": [
            {
                "title": "入库结果",
                "items": [
                    f"新增：{len(added)} 个",
                    f"跳过已存在：{max(0, len(candidates) - len(added))} 个",
                    *[
                        f"{item['word']}：{item['meaning']}"
                        + (f"；熟词僻义：{item['rare']}" if item["rare"] else "")
                        for item in added[:4]
                    ],
                ],
            }
        ],
        "tool_trace": [trace],
        "citations": [],
        "client_actions": [
            {"action_type": "REFRESH_QUERY", "payload": {"query": "vocab"}},
        ],
        "widgets": [widget],
        "llm_used": False,
    }
