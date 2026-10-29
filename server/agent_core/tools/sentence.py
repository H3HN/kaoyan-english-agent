import json
import re
import sqlite3
from typing import Any

from llm import analyze_sentence_breakdown
from tools import check_syllabus_vocab

from ..canvas import _canvas_action

def _normalize_sentence_data(
    sentence_text: str,
    generated: dict[str, Any],
    vocabulary: list[dict[str, Any]],
) -> dict[str, Any]:
    clauses = generated.get("clauses") or []
    modifiers = generated.get("modifiers") or []
    grammar = generated.get("grammar") or []
    return {
        "sentence_en": sentence_text,
        "source_label": "自定义输入 · 实时精析",
        "word_count": len(re.findall(r"[A-Za-z][A-Za-z'’\-]*", sentence_text)),
        "step1_trunk": "\n".join(
            part for part in [generated.get("main", sentence_text), generated.get("mainNote", "")] if part
        ),
        "step2_clauses": [
            {
                "text": str(item.get("text", "")),
                "label": str(item.get("label", "从句")),
                "note": str(item.get("note", "")),
            }
            for item in clauses
            if isinstance(item, dict)
        ],
        "step3_modifiers": [
            {
                "text": str(item.get("text", "")),
                "label": str(item.get("label", "修饰")),
                "note": str(item.get("note", "")),
            }
            for item in modifiers
            if isinstance(item, dict)
        ],
        "step4_translation": generated.get("translation", ""),
        "step4_translation_layers": generated.get("translationLayers", []),
        "step5_vocab_and_grammar": {
            "vocabulary": [
                {
                    "word": item["word"],
                    "meaning": item.get("basic_meaning", ""),
                    "rare_meaning": item.get("rare_meaning"),
                }
                for item in vocabulary
                if item.get("in_syllabus")
            ][:8],
            "grammar": [
                {"name": str(item.get("name", "")), "note": str(item.get("note", ""))}
                for item in grammar
                if isinstance(item, dict)
            ],
            "exam_points": generated.get("examPoints", []),
        },
    }


def _ad_hoc_sentence(conn: sqlite3.Connection, sentence_text: str) -> dict[str, Any]:
    existing = conn.execute(
        "SELECT id, source_label FROM exam_sentences WHERE lower(text) = lower(?) LIMIT 1",
        (sentence_text.strip(),),
    ).fetchone()
    generated = None
    if existing:
        cached = conn.execute(
            "SELECT data_json FROM sentence_breakdowns WHERE sentence_id = ?",
            (existing["id"],),
        ).fetchone()
        if cached:
            generated = json.loads(cached["data_json"])
    if not generated:
        generated = analyze_sentence_breakdown(sentence_text)
    llm_used = bool(generated)
    if not generated:
        generated = {
            "main": sentence_text,
            "mainNote": "当前模型不可用，先保留原句，等待人工或重试生成结构化拆解。",
            "clauses": [],
            "modifiers": [],
            "translation": "",
            "translationLayers": [],
            "grammar": [],
            "examPoints": ["先找谓语；再判断从句与修饰的修饰对象。"],
        }
    vocabulary, vocab_trace = check_syllabus_vocab(conn, sentence_text)
    data = _normalize_sentence_data(sentence_text, generated, vocabulary)
    short = " ".join(re.findall(r"[A-Za-z][A-Za-z'’\-]*", sentence_text)[:4])
    data["source_label"] = f"自定义精析 · {short}" if short else "自定义精析"
    if existing:
        data["source_label"] = f"自定义精析 · 已匹配 {existing['source_label']}"
    tip = generated.get("mainNote") or "先锁定主句谓语，再判断每个从句修饰谁。"
    return {
        "intro": (
            "这句已经实时拆到左侧主画布。先看主干，再看从句和修饰，"
            "最后用翻译检查自己有没有把修饰关系接错。"
        ),
        "sections": [],
        "tool_trace": [vocab_trace],
        "citations": [],
        "client_actions": [
            _canvas_action(
                "sentence",
                data,
                data.get("source_label", "自定义长难句精析"),
                exam_sentence_id=existing["id"] if existing else None,
            )
        ],
        "widgets": [],
        "llm_used": llm_used,
    }
