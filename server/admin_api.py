"""Admin-side operations for the B-end content console.

Functions here stay HTTP-agnostic: authentication is enforced in app.py and the
offline CLI keeps using question_bank.py directly. All writes reuse the existing
question-bank state machine so bank_events remains the authoritative audit trail.
"""
import os
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any

from question_bank import (
    BankError,
    export_entry,
    import_batch,
    practice_readiness,
    readiness,
    transition,
)

ADMIN_TOKEN_ENV = "ADMIN_TOKEN"
DEFAULT_ADMIN_TOKEN = "dev-admin"

STATUS_LABELS = {
    "draft": "草稿",
    "reviewed": "待发布",
    "published": "已发布",
}


def expected_admin_token() -> str:
    """Token used by the admin gate; override with ADMIN_TOKEN in server/.env."""
    return os.getenv(ADMIN_TOKEN_ENV, DEFAULT_ADMIN_TOKEN)


def _passage_to_dict(
    row: sqlite3.Row,
    question_count: int,
    sentence_count: int,
    last_event_at: str | None,
) -> dict[str, Any]:
    return {
        "id": row["id"],
        "year": row["year"],
        "exam_type": row["exam_type"],
        "text_number": row["text_number"],
        "publication_status": row["publication_status"],
        "status_label": STATUS_LABELS.get(
            row["publication_status"], row["publication_status"]
        ),
        "revision": row["revision"],
        "reviewed_by": row["reviewed_by"],
        "reviewed_at": row["reviewed_at"],
        "published_at": row["published_at"],
        "question_count": question_count,
        "sentence_count": sentence_count,
        "last_event_at": last_event_at,
    }


def list_passages(
    conn: sqlite3.Connection,
    status: str = "",
    keyword: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    clauses: list[str] = []
    params: list[Any] = []
    if status:
        clauses.append("p.publication_status = ?")
        params.append(status)
    keyword = keyword.strip()
    if keyword:
        clauses.append(
            "(p.id LIKE ? OR CAST(p.year AS TEXT) LIKE ? OR p.exam_type LIKE ?)"
        )
        like = f"%{keyword}%"
        params.extend([like, like, like])
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    total = conn.execute(
        f"SELECT COUNT(*) FROM exam_passages p {where}", params
    ).fetchone()[0]
    offset = (page - 1) * page_size
    rows = conn.execute(
        f"""
        SELECT p.*,
            (SELECT COUNT(*) FROM exam_questions q WHERE q.passage_id = p.id)
                AS question_count,
            (SELECT COUNT(*) FROM exam_sentences s WHERE s.passage_id = p.id)
                AS sentence_count,
            (SELECT MAX(e.created_at) FROM bank_events e WHERE e.passage_id = p.id)
                AS last_event_at
        FROM exam_passages p
        {where}
        ORDER BY p.year DESC, p.text_number, p.id
        LIMIT ? OFFSET ?
        """,
        (*params, page_size, offset),
    ).fetchall()
    items = [
        _passage_to_dict(
            row, row["question_count"], row["sentence_count"], row["last_event_at"]
        )
        for row in rows
    ]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


def get_stats(conn: sqlite3.Connection) -> dict[str, Any]:
    counts = {status: 0 for status in STATUS_LABELS}
    for row in conn.execute(
        "SELECT publication_status, COUNT(*) AS c FROM exam_passages "
        "GROUP BY publication_status"
    ):
        counts[row["publication_status"]] = row["c"]
    return {
        "draft": counts.get("draft", 0),
        "reviewed": counts.get("reviewed", 0),
        "published": counts.get("published", 0),
        "total": sum(counts.values()),
        "question_total": conn.execute(
            "SELECT COUNT(*) FROM exam_questions"
        ).fetchone()[0],
        "sentence_total": conn.execute(
            "SELECT COUNT(*) FROM exam_sentences"
        ).fetchone()[0],
    }


def passage_detail(conn: sqlite3.Connection, passage_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM exam_passages WHERE id = ?", (passage_id,)
    ).fetchone()
    if row is None:
        return None
    detail = _passage_to_dict(
        row,
        conn.execute(
            "SELECT COUNT(*) FROM exam_questions WHERE passage_id = ?",
            (passage_id,),
        ).fetchone()[0],
        conn.execute(
            "SELECT COUNT(*) FROM exam_sentences WHERE passage_id = ?",
            (passage_id,),
        ).fetchone()[0],
        conn.execute(
            "SELECT MAX(created_at) FROM bank_events WHERE passage_id = ?",
            (passage_id,),
        ).fetchone()[0],
    )
    detail["review_issues"] = readiness(conn, passage_id)
    detail["practice_issues"] = practice_readiness(conn, passage_id)
    detail["entry"] = export_entry(conn, passage_id)["passages"][0]
    return detail


def list_events(
    conn: sqlite3.Connection, passage_id: str, limit: int = 50
) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, passage_id, revision, action, actor, created_at "
        "FROM bank_events WHERE passage_id = ? ORDER BY id DESC LIMIT ?",
        (passage_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def import_document(
    conn: sqlite3.Connection, document: dict[str, Any], actor: str = "管理员"
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise BankError("document 必须是题库 JSON 对象")
    return import_batch(conn, document, actor)


def run_transition(
    conn: sqlite3.Connection, passage_id: str, action: str, actor: str = "管理员"
) -> dict[str, Any]:
    if action not in ("review", "publish", "publish-practice", "withdraw"):
        raise BankError("未知状态操作")
    row = conn.execute(
        "SELECT revision FROM exam_passages WHERE id = ?", (passage_id,)
    ).fetchone()
    if row is None:
        raise BankError("篇章不存在")
    return transition(conn, passage_id, row["revision"], action, actor)

# ---------------------------------------------------------------------------
# Knowledge base: vocabulary entries, citations and trap rules
# ---------------------------------------------------------------------------
VOCAB_LEVELS = ("核心", "高频", "中频", "基础")


def _vocab_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "word": row["word"],
        "phonetic": row["phonetic"],
        "basic_meaning": row["basic_meaning"],
        "rare_meaning": row["rare_meaning"] or "",
        "exam_frequency": row["exam_frequency"],
        "level": row["level"],
        "enabled": bool(row["enabled"]),
    }


def vocab_citations(
    conn: sqlite3.Connection, word: str, limit: int = 3
) -> list[dict[str, Any]]:
    """Published sentences that literally contain the word (drawer evidence)."""
    rows = conn.execute(
        """
        SELECT s.id, s.source_label, s.text, s.year, s.exam_type,
               (SELECT q.question_type FROM exam_questions AS q
                WHERE q.source_sentence_id = s.id ORDER BY q.number LIMIT 1)
                   AS question_type
        FROM exam_sentences AS s
        JOIN exam_passages AS p ON p.id = s.passage_id
        WHERE p.publication_status = 'published' AND lower(s.text) LIKE ?
        ORDER BY s.year DESC, s.id
        LIMIT ?
        """,
        (f"%{word.lower()}%", limit),
    ).fetchall()
    return [
        {
            "sentence_id": row["id"],
            "source": row["source_label"],
            "text": row["text"],
            "year": row["year"],
            "exam_type": row["exam_type"],
            "question_type": row["question_type"] or "",
        }
        for row in rows
    ]


def list_vocab_entries(
    conn: sqlite3.Connection,
    keyword: str = "",
    level: str = "",
    enabled: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    clauses: list[str] = []
    params: list[Any] = []
    keyword = keyword.strip()
    if keyword:
        clauses.append(
            "(word LIKE ? OR basic_meaning LIKE ? OR rare_meaning LIKE ?)"
        )
        params.extend([f"%{keyword}%"] * 3)
    if level:
        clauses.append("level = ?")
        params.append(level)
    if enabled in ("0", "1"):
        clauses.append("enabled = ?")
        params.append(int(enabled))
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    total = conn.execute(
        f"SELECT COUNT(*) FROM syllabus_vocabulary {where}", params
    ).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM syllabus_vocabulary {where} "
        "ORDER BY exam_frequency DESC, word LIMIT ? OFFSET ?",
        (*params, page_size, (page - 1) * page_size),
    ).fetchall()
    return {
        "items": [_vocab_to_dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, (total + page_size - 1) // page_size),
        "stats": {
            "total": conn.execute(
                "SELECT COUNT(*) FROM syllabus_vocabulary"
            ).fetchone()[0],
            "enabled": conn.execute(
                "SELECT COUNT(*) FROM syllabus_vocabulary WHERE enabled = 1"
            ).fetchone()[0],
            "disabled": conn.execute(
                "SELECT COUNT(*) FROM syllabus_vocabulary WHERE enabled = 0"
            ).fetchone()[0],
        },
    }


def get_vocab_entry(
    conn: sqlite3.Connection, word: str
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM syllabus_vocabulary WHERE word = ? COLLATE NOCASE", (word,)
    ).fetchone()
    if row is None:
        return None
    data = _vocab_to_dict(row)
    data["citations"] = vocab_citations(conn, row["word"])
    return data


def _vocab_fields(payload: dict[str, Any], current: dict[str, Any] | None = None) -> dict[str, Any]:
    current = current or {}
    word = (payload.get("word") or current.get("word") or "").strip().lower()
    basic = (
        payload.get("basic_meaning")
        if payload.get("basic_meaning") is not None
        else current.get("basic_meaning") or ""
    ).strip()
    if not word:
        raise BankError("单词不能为空")
    if not basic:
        raise BankError("基本释义不能为空")
    return {
        "word": word,
        "phonetic": (payload.get("phonetic") or "").strip(),
        "basic_meaning": basic,
        "rare_meaning": (payload.get("rare_meaning") or "").strip(),
        "exam_frequency": int(payload.get("exam_frequency") or 0),
        "level": (payload.get("level") or "基础").strip(),
        "enabled": 1 if payload.get("enabled", True) else 0,
    }


def create_vocab_entry(
    conn: sqlite3.Connection, payload: dict[str, Any]
) -> dict[str, Any]:
    data = _vocab_fields(payload)
    exists = conn.execute(
        "SELECT 1 FROM syllabus_vocabulary WHERE word = ? COLLATE NOCASE",
        (data["word"],),
    ).fetchone()
    if exists:
        raise BankError("词条已存在")
    conn.execute(
        "INSERT INTO syllabus_vocabulary "
        "(word, phonetic, basic_meaning, rare_meaning, exam_frequency, level, enabled) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data["word"],
            data["phonetic"],
            data["basic_meaning"],
            data["rare_meaning"],
            data["exam_frequency"],
            data["level"],
            data["enabled"],
        ),
    )
    conn.commit()
    return get_vocab_entry(conn, data["word"])


def update_vocab_entry(
    conn: sqlite3.Connection, word: str, payload: dict[str, Any]
) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM syllabus_vocabulary WHERE word = ? COLLATE NOCASE", (word,)
    ).fetchone()
    if row is None:
        raise BankError("词条不存在")
    # The spelling is the identity key; editing it would orphan lookups.
    payload = {**payload, "word": row["word"]}
    data = _vocab_fields(payload, _vocab_to_dict(row))
    conn.execute(
        "UPDATE syllabus_vocabulary SET phonetic = ?, basic_meaning = ?, "
        "rare_meaning = ?, exam_frequency = ?, level = ?, enabled = ? WHERE id = ?",
        (
            data["phonetic"],
            data["basic_meaning"],
            data["rare_meaning"],
            data["exam_frequency"],
            data["level"],
            data["enabled"],
            row["id"],
        ),
    )
    conn.commit()
    return get_vocab_entry(conn, row["word"])


def set_vocab_enabled(
    conn: sqlite3.Connection, word: str, enabled: bool
) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM syllabus_vocabulary WHERE word = ? COLLATE NOCASE", (word,)
    ).fetchone()
    if row is None:
        raise BankError("词条不存在")
    conn.execute(
        "UPDATE syllabus_vocabulary SET enabled = ? WHERE id = ?",
        (1 if enabled else 0, row["id"]),
    )
    conn.commit()
    return get_vocab_entry(conn, row["word"])


def list_trap_rules(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute("SELECT * FROM trap_rules ORDER BY id").fetchall()
    ]


def _trap_fields(
    payload: dict[str, Any], current: dict[str, Any] | None = None
) -> dict[str, Any]:
    current = current or {}
    name = (payload.get("name") or current.get("name") or "").strip()
    definition = (payload.get("definition") or current.get("definition") or "").strip()
    if not name:
        raise BankError("陷阱名称不能为空")
    if not definition:
        raise BankError("陷阱定义不能为空")
    return {
        "name": name,
        "definition": definition,
        "signals": (payload.get("signals") or current.get("signals") or "").strip(),
        "example": (payload.get("example") or current.get("example") or "").strip(),
        "tone": (payload.get("tone") or current.get("tone") or "red").strip(),
    }


def create_trap_rule(
    conn: sqlite3.Connection, payload: dict[str, Any]
) -> dict[str, Any]:
    data = _trap_fields(payload)
    exists = conn.execute(
        "SELECT 1 FROM trap_rules WHERE name = ?", (data["name"],)
    ).fetchone()
    if exists:
        raise BankError("陷阱规则已存在")
    cursor = conn.execute(
        "INSERT INTO trap_rules (name, definition, signals, example, tone) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            data["name"],
            data["definition"],
            data["signals"],
            data["example"],
            data["tone"],
        ),
    )
    conn.commit()
    return dict(
        conn.execute(
            "SELECT * FROM trap_rules WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    )


def update_trap_rule(
    conn: sqlite3.Connection, rule_id: int, payload: dict[str, Any]
) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM trap_rules WHERE id = ?", (rule_id,)
    ).fetchone()
    if row is None:
        raise BankError("陷阱规则不存在")
    data = _trap_fields(payload, dict(row))
    conn.execute(
        "UPDATE trap_rules SET name = ?, definition = ?, signals = ?, "
        "example = ?, tone = ? WHERE id = ?",
        (
            data["name"],
            data["definition"],
            data["signals"],
            data["example"],
            data["tone"],
            rule_id,
        ),
    )
    conn.commit()
    return dict(
        conn.execute("SELECT * FROM trap_rules WHERE id = ?", (rule_id,)).fetchone()
    )

# ---------------------------------------------------------------------------
# Run monitoring and learning analytics
# ---------------------------------------------------------------------------
def _daily_window(days: int) -> list[str]:
    today = date.today()
    return [
        (today - timedelta(days=offset)).isoformat()
        for offset in range(days - 1, -1, -1)
    ]


def _daily_counts(conn: sqlite3.Connection, sql: str, days: int) -> list[dict[str, Any]]:
    mapping = {
        row["day"]: row["c"]
        for row in conn.execute(sql).fetchall()
        if row["day"]
    }
    return [{"date": day, "count": mapping.get(day, 0)} for day in _daily_window(days)]


def get_monitor(conn: sqlite3.Connection, days: int = 7) -> dict[str, Any]:
    """Aggregate agent runs, practice records, breakdowns and the wordbook."""
    runs_total = conn.execute("SELECT COUNT(*) FROM agent_runs").fetchone()[0]
    by_workflow = [
        {"workflow": row["workflow"], "count": row["c"]}
        for row in conn.execute(
            "SELECT workflow, COUNT(*) AS c FROM agent_runs "
            "GROUP BY workflow ORDER BY c DESC, workflow"
        ).fetchall()
    ]
    runs_daily = _daily_counts(
        conn, "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS c "
        "FROM agent_runs GROUP BY day", days,
    )

    practice_total = conn.execute("SELECT COUNT(*) FROM practice_records").fetchone()[0]
    practice_correct = conn.execute(
        "SELECT COUNT(*) FROM practice_records WHERE is_correct = 1"
    ).fetchone()[0]
    by_type = []
    for row in conn.execute(
        "SELECT question_type AS qtype, COUNT(*) AS total, "
        "SUM(is_correct) AS correct FROM practice_records "
        "GROUP BY question_type ORDER BY total DESC, qtype"
    ).fetchall():
        total = row["total"] or 0
        correct = row["correct"] or 0
        by_type.append(
            {
                "type": row["qtype"],
                "total": total,
                "correct": correct,
                "accuracy": round(correct / total, 2) if total else 0,
            }
        )
    practice_daily = _daily_counts(
        conn, "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS c "
        "FROM practice_records GROUP BY day", days,
    )

    breakdown_total = conn.execute(
        "SELECT COUNT(*) FROM sentence_breakdowns"
    ).fetchone()[0]
    breakdown_llm = conn.execute(
        "SELECT COUNT(*) FROM sentence_breakdowns WHERE llm_used = 1"
    ).fetchone()[0]
    wordbook_total = conn.execute("SELECT COUNT(*) FROM user_vocab_book").fetchone()[0]
    due_words = conn.execute(
        "SELECT COUNT(*) FROM user_vocab_book WHERE next_review <= ?",
        (datetime.now().isoformat(timespec="seconds"),),
    ).fetchone()[0]

    return {
        "days": days,
        "runs": {
            "total": runs_total,
            "by_workflow": by_workflow,
            "daily": runs_daily,
        },
        "practice": {
            "total": practice_total,
            "correct": practice_correct,
            "accuracy": round(practice_correct / practice_total, 2)
            if practice_total
            else 0,
            "by_type": by_type,
            "daily": practice_daily,
        },
        "breakdowns": {
            "total": breakdown_total,
            "llm_used": breakdown_llm,
            "llm_ratio": round(breakdown_llm / breakdown_total, 2)
            if breakdown_total
            else 0,
        },
        "wordbook": {"total": wordbook_total, "due": due_words},
    }