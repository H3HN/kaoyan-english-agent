import json
import re
import sqlite3
from typing import Any

from llm import lookup_word_online
from tools import check_syllabus_vocab

from ..canvas import _canvas_action


def _cached_lookup(conn: sqlite3.Connection, word: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT payload_json FROM word_lookup_cache WHERE word = ?",
        (word.lower(),),
    ).fetchone()
    if not row:
        return None
    try:
        data = json.loads(row["payload_json"])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _cache_lookup(conn: sqlite3.Connection, word: str, payload: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO word_lookup_cache (word, payload_json, source)
        VALUES (?, ?, 'llm')
        ON CONFLICT(word) DO UPDATE SET
            payload_json = excluded.payload_json,
            source = excluded.source,
            updated_at = datetime('now')
        """,
        (word.lower(), json.dumps(payload, ensure_ascii=False)),
    )
    conn.commit()


def _word_pattern(word: str) -> re.Pattern[str]:
    # SQL LIKE '%bee%' also matches 'been'; use real word boundaries here.
    return re.compile(
        r"(?<![A-Za-z])" + re.escape(word.strip()) + r"(?![A-Za-z])",
        re.IGNORECASE,
    )


def _word_insight(conn: sqlite3.Connection, target: str) -> dict[str, Any]:
    cleaned = target.strip()
    phrase = len(re.findall(r"[A-Za-z][A-Za-z'’\-]*", cleaned)) > 1
    vocab = conn.execute(
        "SELECT * FROM syllabus_vocabulary WHERE lower(word) = lower(?) LIMIT 1",
        (cleaned,),
    ).fetchone()
    entries, vocab_trace = check_syllabus_vocab(conn, cleaned)
    if not vocab and entries:
        vocab = conn.execute(
            "SELECT * FROM syllabus_vocabulary WHERE lower(word) = lower(?) LIMIT 1",
            (entries[0]["word"],),
        ).fetchone()
    examples = conn.execute(
        """
        SELECT s.id, s.text, s.source_label
        FROM exam_sentences AS s
        JOIN exam_passages AS p ON p.id = s.passage_id
        WHERE p.publication_status = 'published'
          AND lower(s.text) LIKE ?
        ORDER BY length(s.text) ASC, s.year DESC
        LIMIT 200
        """,
        (f"%{cleaned.lower()}%",),
    ).fetchall()
    pattern = _word_pattern(cleaned)
    examples = [row for row in examples if pattern.search(row["text"])][:4]
    local_meaning = vocab["basic_meaning"] if vocab and vocab["basic_meaning"] else ""
    if not local_meaning and entries:
        local_meaning = "；".join(
            item["basic_meaning"] for item in entries[:2] if item.get("basic_meaning")
        )
    online: dict[str, Any] | None = None
    if not local_meaning or not vocab:
        online = _cached_lookup(conn, cleaned)
        if not online:
            online = lookup_word_online(cleaned)
            if online:
                _cache_lookup(conn, cleaned, online)

    online_examples = []
    if online:
        online_examples = [
            {
                "sentence_id": f"lookup-{cleaned.lower()}-{index}",
                "source": "在线词典",
                "text": example.get("en", ""),
                "translation": example.get("zh", ""),
            }
            for index, example in enumerate(online.get("examples") or [])
            if example.get("en") and pattern.search(example["en"])
        ]
    exam_examples = [
        {
            "sentence_id": row["id"],
            "source": row["source_label"],
            "text": row["text"],
        }
        for row in examples
    ]
    if online:
        basic_meaning = "；".join(online.get("basic_meanings") or []) or local_meaning
        level = "专有名词" if online.get("is_proper_noun") else "在线查询"
        phonetic = str(online.get("phonetic") or "")
        rare_meaning = str(online.get("rare_meaning") or "")
        collocations = list(online.get("collocations") or [])
        if phrase and not collocations:
            collocations = [cleaned]
        lookup_source = "llm"
    else:
        basic_meaning = local_meaning
        level = vocab["level"] if vocab else "未收录"
        phonetic = ""
        rare_meaning = vocab["rare_meaning"] if vocab else ""
        collocations = [cleaned] if phrase else []
        lookup_source = "local" if local_meaning else "none"

    data = {
        "word": cleaned,
        "phonetic": phonetic,
        "level": level,
        "exam_frequency": vocab["exam_frequency"] if vocab else 0,
        "basic_meaning": basic_meaning,
        "rare_meaning": rare_meaning,
        "is_phrase": phrase,
        "collocations": collocations,
        "examples": (exam_examples + online_examples)[:6],
        "lookup_source": lookup_source,
        "part_of_speech": online.get("part_of_speech") if online else "",
        "is_proper_noun": bool(online.get("is_proper_noun")) if online else False,
    }
    if online:
        intro = (
            f"本地大纲词库没有收录 {cleaned}，我已经在线查询并挂到左侧词汇透视卡。"
            "先看基础义，再结合例句和搭配理解。"
        )
    elif local_meaning:
        intro = (
            f"已经把这{'个短语' if phrase else '个词'}挂到左侧词汇透视卡。"
            "先看基础义，再看琥珀色标注的熟词僻义与真题例句。"
        )
    else:
        intro = f"暂时无法查询 {cleaned} 的释义。请检查网络或模型配置后重试。"
    return {
        "intro": intro,
        "sections": [],
        "tool_trace": [vocab_trace],
        "citations": [],
        "client_actions": [
            _canvas_action(
                "phrase" if phrase else "word",
                data,
                cleaned,
            )
        ],
        "widgets": [],
        "llm_used": bool(online),
    }
