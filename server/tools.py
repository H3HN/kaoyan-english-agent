import json
import re
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Any

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "while", "as", "than",
    "that", "this", "these", "those", "it", "its", "they", "them", "their",
    "he", "she", "his", "her", "we", "our", "you", "your", "i", "my",
    "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "have", "has", "had", "having",
    "will", "would", "can", "could", "may", "might", "must", "should",
    "shall", "to", "of", "in", "on", "at", "by", "for", "with", "from",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "over", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all",
    "any", "both", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "too",
    "very", "just", "also", "however", "therefore", "thus", "which",
    "who", "whom", "whose", "what", "whether", "because", "although",
    "though", "since", "until", "unless", "upon", "within", "without",
    "among", "against", "across", "behind", "beyond", "during", "per",
    "one", "two", "three", "first", "second", "new", "many", "much",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def _now_iso(days: float = 0) -> str:
    return (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")


def _trace(tool: str, args: dict[str, Any], summary: str, started: float) -> dict[str, Any]:
    return {
        "tool": tool,
        "args": args,
        "summary": summary,
        "duration_ms": max(1, int((time.perf_counter() - started) * 1000)),
    }


def extract_words(text: str) -> list[str]:
    seen: set[str] = set()
    words: list[str] = []
    for token in WORD_RE.findall(text.lower()):
        token = token.strip("'-")
        if len(token) < 3 or token in STOPWORDS or token.isdigit():
            continue
        if token in seen:
            continue
        seen.add(token)
        words.append(token)
    return words


def _lemma_candidates(word: str) -> list[str]:
    candidates = [word]
    if word.endswith("'s"):
        candidates.append(word[:-2])
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("ied") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("es") and len(word) > 3:
        candidates.append(word[:-2])
        candidates.append(word[:-1])
    if word.endswith("s") and len(word) > 3:
        candidates.append(word[:-1])
    if word.endswith("ed") and len(word) > 4:
        candidates.append(word[:-2])
        candidates.append(word[:-1])
        if len(word) > 5 and word[-3] == word[-4]:
            candidates.append(word[:-3])
    if word.endswith("ing") and len(word) > 5:
        candidates.append(word[:-3])
        candidates.append(word[:-3] + "e")
        if len(word) > 6 and word[-4] == word[-5]:
            candidates.append(word[:-4])
    if word.endswith("ly") and len(word) > 5:
        candidates.append(word[:-2])
    if word.endswith("er") and len(word) > 5:
        candidates.append(word[:-2])
        candidates.append(word[:-1])
    if word.endswith("est") and len(word) > 6:
        candidates.append(word[:-3])
    return list(dict.fromkeys(candidates))


def _find_vocab(conn: sqlite3.Connection, word: str) -> sqlite3.Row | None:
    for candidate in _lemma_candidates(word):
        row = conn.execute(
            "SELECT * FROM syllabus_vocabulary WHERE word = ?", (candidate,)
        ).fetchone()
        if row:
            return row
    return None


def _vocab_entry(conn: sqlite3.Connection, word: str) -> dict[str, Any]:
    row = _find_vocab(conn, word)
    if not row:
        return {
            "word": word,
            "matched": None,
            "in_syllabus": False,
            "level": "超纲",
            "basic_meaning": "",
            "rare_meaning": None,
            "exam_frequency": 0,
            "source": "本地大纲词库",
        }
    return {
        "word": word,
        "matched": row["word"],
        "in_syllabus": True,
        "level": row["level"],
        "basic_meaning": row["basic_meaning"],
        "rare_meaning": row["rare_meaning"],
        "exam_frequency": row["exam_frequency"],
        "source": "本地大纲词库",
    }


def check_syllabus_vocab(
    conn: sqlite3.Connection, text_or_words: str | list[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    started = time.perf_counter()
    if isinstance(text_or_words, str):
        words = extract_words(text_or_words)
    else:
        words = []
        seen: set[str] = set()
        for raw in text_or_words:
            for token in WORD_RE.findall(str(raw).lower()):
                token = token.strip("'-")
                if len(token) >= 2 and token not in seen:
                    seen.add(token)
                    words.append(token)

    words = words[:80]
    entries = [_vocab_entry(conn, word) for word in words]
    hits = [entry for entry in entries if entry["in_syllabus"]]
    rare = [entry for entry in hits if entry["rare_meaning"]]
    summary = (
        f"检索 {len(entries)} 个实词，命中 {len(hits)} 个大纲词"
        + (f"，其中 {len(rare)} 个含熟词僻义" if rare else "")
    )
    trace = _trace(
        "check_syllabus_vocab",
        {"word_count": len(entries), "preview": words[:12]},
        summary,
        started,
    )
    return entries, trace


def search_past_exams(
    conn: sqlite3.Connection,
    query: str = "",
    grammar: str | list[str] | None = None,
    limit: int = 5,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    started = time.perf_counter()
    clauses: list[str] = []
    params: list[Any] = []

    query = (query or "").strip()
    if query:
        snippet = query[:80]
        clauses.append("(lower(text) LIKE ? OR lower(source_label) LIKE ?)")
        params.extend([f"%{snippet.lower()}%", f"%{snippet.lower()}%"])

    tags: list[str] = []
    if isinstance(grammar, str):
        tags = [item for item in re.split(r"[,，;；|/\s]+", grammar) if item]
    elif grammar:
        tags = [str(item) for item in grammar if item]
    if tags:
        tag_clauses = []
        for tag in tags[:4]:
            tag_clauses.append("grammar_tags LIKE ?")
            params.append(f"%{tag}%")
        clauses.append("(" + " OR ".join(tag_clauses) + ")")

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(
        f"""
        SELECT * FROM exam_sentences
        {where}
        ORDER BY year DESC, passage_id, sentence_index
        LIMIT ?
        """,
        (*params, max(1, min(limit, 20))),
    ).fetchall()

    citations = [
        {
            "id": row["id"],
            "source": row["source_label"],
            "passage_id": row["passage_id"],
            "year": row["year"],
            "exam_type": row["exam_type"],
            "text": row["text"],
            "grammar_tags": json.loads(row["grammar_tags"] or "[]"),
        }
        for row in rows
    ]
    summary = f"检索到 {len(citations)} 条真题切片"
    if citations:
        summary += f"，优先引用 {citations[0]['source']}"
    trace = _trace(
        "search_past_exams",
        {"query": query[:60], "grammar": tags, "limit": limit},
        summary,
        started,
    )
    return citations, trace


def get_sentence(conn: sqlite3.Connection, sentence_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM exam_sentences WHERE id = ?", (sentence_id,)
    ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "passage_id": row["passage_id"],
        "year": row["year"],
        "exam_type": row["exam_type"],
        "text_number": row["text_number"],
        "paragraph": row["paragraph"],
        "sentence_index": row["sentence_index"],
        "text": row["text"],
        "grammar_tags": json.loads(row["grammar_tags"] or "[]"),
        "source": row["source_label"],
    }


def get_question(conn: sqlite3.Connection, question_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM exam_questions WHERE id = ?", (question_id,)
    ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "passage_id": row["passage_id"],
        "year": row["year"],
        "exam_type": row["exam_type"],
        "text_number": row["text_number"],
        "number": row["number"],
        "question_type": row["question_type"],
        "content": row["content"],
        "options": json.loads(row["options_json"]),
        "correct_answer": row["correct_answer"],
        "analysis": {
            key: {
                "trapType": value.get("trapType") or value.get("trap_type", ""),
                "explanation": value.get("explanation", ""),
            }
            for key, value in json.loads(row["analysis_json"]).items()
        },
        "steps": json.loads(row["steps_json"]),
        "source_sentence_id": row["source_sentence_id"],
    }


def list_sentences(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, source_label, grammar_tags, text FROM exam_sentences ORDER BY year DESC, sentence_index"
    ).fetchall()
    return [
        {
            "id": row["id"],
            "source": row["source_label"],
            "grammar_tags": json.loads(row["grammar_tags"] or "[]"),
            "text": row["text"],
        }
        for row in rows
    ]


def list_questions(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, year, exam_type, text_number, number, question_type, content, correct_answer FROM exam_questions ORDER BY year DESC, number"
    ).fetchall()
    return [dict(row) for row in rows]


def word_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": f"w{row['id']}",
        "spelling": row["spelling"],
        "phonetic": row["phonetic"],
        "meaning": row["meaning"],
        "source": row["source"],
        "context": row["context"],
        "isOutline": bool(row["is_outline"]),
        "familiarity": row["familiarity"],
        "reviewCount": row["review_count"],
        "nextReview": row["next_review"],
    }


def add_to_vocab_book(
    conn: sqlite3.Connection,
    word: str,
    context: str = "",
    source: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.perf_counter()
    spelling = WORD_RE.findall((word or "").lower())
    normalized = spelling[0] if spelling else (word or "").strip().lower()
    if not normalized:
        return {}, _trace("add_to_vocab_book", {"word": word}, "单词为空，未写入", started)

    existing = conn.execute(
        "SELECT * FROM user_vocab_book WHERE spelling = ?", (normalized,)
    ).fetchone()
    if existing:
        return word_to_dict(existing), _trace(
            "add_to_vocab_book",
            {"word": normalized},
            f"{normalized} 已在单词本中，未重复写入",
            started,
        )

    vocab = _find_vocab(conn, normalized)
    meaning = vocab["basic_meaning"] if vocab else "（词库未收录，请手动补充释义）"
    rare = vocab["rare_meaning"] if vocab else None
    if rare:
        meaning = f"{meaning}；熟词僻义：{rare}"
    next_review = _now_iso(1)
    conn.execute(
        """
        INSERT INTO user_vocab_book
            (spelling, phonetic, meaning, source, context, is_outline,
             familiarity, review_count, easiness, interval_days, repetition,
             next_review)
        VALUES (?, '', ?, ?, ?, ?, 0, 0, 2.5, 1, 0, ?)
        """,
        (
            normalized,
            meaning,
            source or "Agent 自动归档",
            context[:500],
            1 if vocab else 0,
            next_review,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM user_vocab_book WHERE spelling = ?", (normalized,)
    ).fetchone()
    summary = f"已将 {normalized} 写入单词本，首次复习安排在明天"
    if rare:
        summary += "，并附带熟词僻义"
    return word_to_dict(row), _trace(
        "add_to_vocab_book",
        {"word": normalized, "source": source or "Agent 自动归档"},
        summary,
        started,
    )


def remove_word(conn: sqlite3.Connection, spelling: str) -> bool:
    cursor = conn.execute(
        "DELETE FROM user_vocab_book WHERE spelling = ?", (spelling.lower(),)
    )
    conn.commit()
    return cursor.rowcount > 0


def review_word(
    conn: sqlite3.Connection, spelling: str, remembered: bool
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM user_vocab_book WHERE spelling = ?", (spelling.lower(),)
    ).fetchone()
    if not row:
        return None
    familiarity = row["familiarity"] + (0.15 if remembered else -0.1)
    familiarity = round(max(0.0, min(1.0, familiarity)), 2)
    review_count = row["review_count"] + 1
    if remembered:
        interval = min(30, max(1, row["interval_days"] * 2))
        repetition = row["repetition"] + 1
    else:
        interval = 1
        repetition = 0
    conn.execute(
        """
        UPDATE user_vocab_book
        SET familiarity = ?, review_count = ?, interval_days = ?,
            repetition = ?, next_review = ?
        WHERE spelling = ?
        """,
        (
            familiarity,
            review_count,
            interval,
            repetition,
            _now_iso(interval),
            spelling.lower(),
        ),
    )
    conn.commit()
    updated = conn.execute(
        "SELECT * FROM user_vocab_book WHERE spelling = ?", (spelling.lower(),)
    ).fetchone()
    return word_to_dict(updated)


def get_state(conn: sqlite3.Connection) -> dict[str, Any]:
    words = [
        word_to_dict(row)
        for row in conn.execute(
            "SELECT * FROM user_vocab_book ORDER BY created_at DESC, id DESC"
        ).fetchall()
    ]
    records = [
        {
            "id": f"r{row['id']}",
            "questionId": row["question_id"],
            "questionType": row["question_type"],
            "userAnswer": row["user_answer"],
            "correctAnswer": row["correct_answer"],
            "isCorrect": bool(row["is_correct"]),
            "trapType": row["trap_type"],
            "time": row["created_at"],
        }
        for row in conn.execute(
            "SELECT * FROM practice_records ORDER BY created_at DESC, id DESC"
        ).fetchall()
    ]
    return {"words": words, "records": records}


def record_option_attempt(
    conn: sqlite3.Connection,
    question: dict[str, Any],
    user_answer: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    started = time.perf_counter()
    if not user_answer:
        return None, _trace(
            "record_trap_mistake",
            {"question_id": question["id"]},
            "未提交答案，跳过错题归档",
            started,
        )

    is_correct = user_answer == question["correct_answer"]
    trap_type = "正确"
    if not is_correct:
        trap_type = question["analysis"].get(user_answer, {}).get("trapType", "未归类")

    cursor = conn.execute(
        """
        INSERT INTO practice_records
            (question_id, question_type, user_answer, correct_answer, is_correct,
             trap_type, agent_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            question["id"],
            question["question_type"],
            user_answer,
            question["correct_answer"],
            1 if is_correct else 0,
            trap_type,
            json.dumps(
                question["analysis"].get(user_answer, {}), ensure_ascii=False
            ),
        ),
    )
    conn.commit()
    record = {
        "id": f"r{cursor.lastrowid}",
        "questionId": question["id"],
        "questionType": question["question_type"],
        "userAnswer": user_answer,
        "correctAnswer": question["correct_answer"],
        "isCorrect": is_correct,
        "trapType": trap_type,
        "time": datetime.now().isoformat(timespec="seconds"),
    }
    summary = (
        f"已记录第 {question['number']} 题作答：{user_answer}，"
        + ("回答正确" if is_correct else f"命中陷阱「{trap_type}」")
    )
    return record, _trace(
        "record_trap_mistake",
        {"question_id": question["id"], "trap_type": trap_type},
        summary,
        started,
    )


def get_report(conn: sqlite3.Connection) -> dict[str, Any]:
    records = conn.execute(
        "SELECT * FROM practice_records ORDER BY created_at DESC"
    ).fetchall()
    total = len(records)
    correct = sum(1 for row in records if row["is_correct"])
    by_type: dict[str, dict[str, Any]] = {}
    trap_distribution: dict[str, int] = {}
    for row in records:
        qtype = row["question_type"]
        bucket = by_type.setdefault(qtype, {"total": 0, "correct": 0})
        bucket["total"] += 1
        bucket["correct"] += 1 if row["is_correct"] else 0
        if not row["is_correct"] and row["trap_type"]:
            trap_distribution[row["trap_type"]] = (
                trap_distribution.get(row["trap_type"], 0) + 1
            )
    for bucket in by_type.values():
        bucket["accuracy"] = round(bucket["correct"] / bucket["total"], 2) if bucket["total"] else 0
    weak_types = sorted(
        [
            {"type": name, **data}
            for name, data in by_type.items()
            if data["total"] > 0 and data["accuracy"] < 0.7
        ],
        key=lambda item: item["accuracy"],
    )

    due_rows = conn.execute(
        "SELECT * FROM user_vocab_book WHERE next_review <= ? ORDER BY next_review",
        (datetime.now().isoformat(timespec="seconds"),),
    ).fetchall()
    due_words = [word_to_dict(row) for row in due_rows]

    suggestions: list[str] = []
    if weak_types:
        for item in weak_types[:2]:
            suggestions.append(
                f"{item['type']}正确率 {int(item['accuracy'] * 100)}%，建议每天精做 2–3 道同类题并复盘排除理由。"
            )
    else:
        suggestions.append("各题型正确率均达标，建议保持节奏并尝试限时训练。")
    if due_words:
        suggestions.append(
            f"有 {len(due_words)} 个单词到期，先完成无提示回忆，再开始新的阅读。"
        )
    if total < 30:
        suggestions.append(
            f"当前累计 {total} 题，样本还不够大；建议累计 30 题以上再做稳定薄弱分析。"
        )

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 2) if total else 0,
        "by_type": by_type,
        "trap_distribution": trap_distribution,
        "weak_types": weak_types,
        "due_words": due_words,
        "suggestions": suggestions,
    }


def get_meta(conn: sqlite3.Connection) -> dict[str, Any]:
    return {
        "vocab_count": conn.execute(
            "SELECT COUNT(*) FROM syllabus_vocabulary"
        ).fetchone()[0],
        "sentence_count": conn.execute(
            "SELECT COUNT(*) FROM exam_sentences"
        ).fetchone()[0],
        "question_count": conn.execute(
            "SELECT COUNT(*) FROM exam_questions"
        ).fetchone()[0],
        "passage_count": conn.execute(
            "SELECT COUNT(*) FROM exam_passages"
        ).fetchone()[0],
        "trap_count": conn.execute("SELECT COUNT(*) FROM trap_rules").fetchone()[0],
        "wordbook_count": conn.execute(
            "SELECT COUNT(*) FROM user_vocab_book"
        ).fetchone()[0],
        "record_count": conn.execute(
            "SELECT COUNT(*) FROM practice_records"
        ).fetchone()[0],
        "database": "SQLite",
        "knowledge_version": "2026.10",
    }


def get_trap_rules(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT name, definition, signals, example, tone FROM trap_rules ORDER BY id"
        ).fetchall()
    ]


def get_rare_words(conn: sqlite3.Connection, limit: int = 6) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT word, basic_meaning, rare_meaning, level, exam_frequency
        FROM syllabus_vocabulary
        WHERE rare_meaning IS NOT NULL
        ORDER BY exam_frequency DESC, word
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def search_vocab(conn: sqlite3.Connection, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM syllabus_vocabulary
        WHERE word LIKE ? OR basic_meaning LIKE ? OR rare_meaning LIKE ?
        ORDER BY exam_frequency DESC, word
        LIMIT ?
        """,
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit),
    ).fetchall()
    return [dict(row) for row in rows]


def list_vocab(
    conn: sqlite3.Connection,
    keyword: str = "",
    level: str = "",
    sort: str = "freq",
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """浏览词库：关键词为空时返回全量分页列表。"""
    where: list[str] = []
    params: list[Any] = []
    if keyword:
        where.append("(word LIKE ? OR basic_meaning LIKE ? OR rare_meaning LIKE ?)")
        params.extend([f"%{keyword}%"] * 3)
    if level:
        where.append("level = ?")
        params.append(level)
    clause = f"WHERE {' AND '.join(where)}" if where else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM syllabus_vocabulary {clause}", params
    ).fetchone()[0]

    order = "word ASC" if sort == "alpha" else "exam_frequency DESC, word ASC"
    rows = conn.execute(
        f"SELECT * FROM syllabus_vocabulary {clause} ORDER BY {order} LIMIT ? OFFSET ?",
        [*params, limit, offset],
    ).fetchall()
    return {"items": [dict(row) for row in rows], "total": total}
