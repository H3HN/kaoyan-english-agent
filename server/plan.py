"""Deterministic study-plan scheduling and proactive insights.

The planner is rule-based on purpose: every recommendation is reproducible from
SQLite state and recorded in ``study_plans.source_json``. The LLM layer never
takes part, so the plan works with or without an API key.
"""
import json
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any

from tools import get_report

WEEKDAY_LABELS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")


def _today() -> date:
    return date.today()


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _settings_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "exam_date": row["exam_date"],
        "daily_minutes": row["daily_minutes"],
        "target_score": row["target_score"],
    }


def get_or_create_settings(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM plan_settings WHERE id = 1").fetchone()
    if row is None:
        conn.execute("INSERT INTO plan_settings (id) VALUES (1)")
        conn.commit()
        row = conn.execute("SELECT * FROM plan_settings WHERE id = 1").fetchone()
    return _settings_to_dict(row)


def update_settings(
    conn: sqlite3.Connection,
    exam_date: str = "",
    daily_minutes: int = 60,
    target_score: int = 70,
) -> dict[str, Any]:
    """Persist planner settings; ``exam_date`` must be YYYY-MM-DD or empty."""
    if exam_date:
        try:
            date.fromisoformat(exam_date)
        except ValueError as exc:
            raise ValueError("exam_date must be YYYY-MM-DD") from exc
    get_or_create_settings(conn)
    conn.execute(
        "UPDATE plan_settings SET exam_date = ?, daily_minutes = ?, "
        "target_score = ?, updated_at = ? WHERE id = 1",
        (exam_date, daily_minutes, target_score, _now_iso()),
    )
    conn.commit()
    return get_or_create_settings(conn)


def _days_until_exam(settings: dict[str, Any]) -> int | None:
    if not settings["exam_date"]:
        return None
    return (date.fromisoformat(settings["exam_date"]) - _today()).days


def _count_untried_questions(conn: sqlite3.Connection) -> int:
    return conn.execute(
        """
        SELECT COUNT(*)
        FROM exam_questions AS q
        JOIN exam_passages AS p ON p.id = q.passage_id
        WHERE p.publication_status = 'published'
          AND q.id NOT IN (SELECT question_id FROM practice_records)
        """
    ).fetchone()[0]


def _plan_window(week_offset: int = 0) -> list[date]:
    start = _today() + timedelta(days=week_offset * 7)
    return [start + timedelta(days=offset) for offset in range(7)]


def _existing_dates(conn: sqlite3.Connection, start: date, end: date) -> set[str]:
    """Dates that already hold pending tasks; done-only days get refilled."""
    rows = conn.execute(
        "SELECT DISTINCT plan_date FROM study_plans WHERE plan_date BETWEEN ? AND ? "
        "AND status = 'pending'",
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return {row["plan_date"] for row in rows}


def _insert_item(
    conn: sqlite3.Connection,
    plan_date: date,
    task_type: str,
    title: str,
    target_count: int,
    link: str,
    source: dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO study_plans
            (plan_date, task_type, title, target_count, link, source_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            plan_date.isoformat(),
            task_type,
            title,
            target_count,
            link,
            json.dumps(source, ensure_ascii=False),
        ),
    )


def _daily_items(
    due_words: int,
    weak_types: list[dict[str, Any]],
    untried: int,
    offset: int,
) -> list[dict[str, Any]]:
    """Return the deterministic task list for one day of the plan window."""
    items: list[dict[str, Any]] = []
    daily_vocab = min(due_words, 15)
    if daily_vocab > 0:
        items.append(
            {
                "task_type": "vocab_review",
                "title": f"复习 {daily_vocab} 个到期单词",
                "target_count": daily_vocab,
                "link": "/wordbook",
                "source": {"rule": "due_words", "due_words": due_words},
            }
        )
    if weak_types:
        rotated = weak_types[offset % len(weak_types)]
        items.append(
            {
                "task_type": "weak_type_practice",
                "title": f"专项训练：{rotated['type']} 2 道",
                "target_count": 2,
                "link": "/options",
                "source": {
                    "rule": "weakest_rotating",
                    "weak_type": rotated["type"],
                    "accuracy": rotated["accuracy"],
                },
            }
        )
    if untried > 0:
        items.append(
            {
                "task_type": "exam_practice",
                "title": "真题练习 3 道",
                "target_count": 3,
                "link": "/options",
                "source": {"rule": "untried_questions", "remaining": untried},
            }
        )
    if not items:
        items.append(
            {
                "task_type": "sentence_practice",
                "title": "拆解 1 个长难句保持手感",
                "target_count": 1,
                "link": "/sentence",
                "source": {"rule": "fallback_keep_momentum"},
            }
        )
    return items


def generate_plan(
    conn: sqlite3.Connection, days: int = 7, force: bool = False
) -> dict[str, Any]:
    """Generate the next ``days`` days of tasks; idempotent per date."""
    days = max(1, min(days, 28))
    today = _today()
    dates = [today + timedelta(days=offset) for offset in range(days)]
    if force:
        conn.execute(
            "DELETE FROM study_plans WHERE plan_date >= ? AND status = 'pending'",
            (today.isoformat(),),
        )
        conn.commit()

    report = get_report(conn)
    due_words = len(report["due_words"])
    weak_types = report["weak_types"]
    untried = _count_untried_questions(conn)

    existing = _existing_dates(conn, dates[0], dates[-1])
    created_dates = 0
    for offset, current in enumerate(dates):
        if current.isoformat() in existing:
            continue
        for item in _daily_items(due_words, weak_types, untried, offset):
            _insert_item(
                conn,
                current,
                item["task_type"],
                item["title"],
                item["target_count"],
                item["link"],
                item["source"],
            )
        created_dates += 1
    conn.commit()
    return {"created_dates": created_dates, "days": days, **get_plan_for_dates(conn, dates)}


def _item_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "plan_date": row["plan_date"],
        "task_type": row["task_type"],
        "title": row["title"],
        "detail": row["detail"],
        "target_count": row["target_count"],
        "done_count": row["done_count"],
        "status": row["status"],
        "link": row["link"],
    }


def get_plan_for_dates(
    conn: sqlite3.Connection, dates: list[date]
) -> dict[str, Any]:
    start, end = dates[0].isoformat(), dates[-1].isoformat()
    rows = conn.execute(
        "SELECT * FROM study_plans WHERE plan_date BETWEEN ? AND ? "
        "ORDER BY plan_date, id",
        (start, end),
    ).fetchall()
    items = [_item_to_dict(row) for row in rows]
    by_date: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_date.setdefault(item["plan_date"], []).append(item)
    today_iso = _today().isoformat()
    days_payload = []
    for current in dates:
        key = current.isoformat()
        day_items = by_date.get(key, [])
        days_payload.append(
            {
                "date": key,
                "weekday": WEEKDAY_LABELS[current.weekday()],
                "is_today": key == today_iso,
                "items": day_items,
                "done_count": sum(1 for item in day_items if item["status"] == "done"),
                "total_count": len(day_items),
            }
        )
    done = sum(1 for item in items if item["status"] == "done")
    total = len(items)
    return {
        "items": items,
        "days": days_payload,
        "summary": {
            "total": total,
            "done": done,
            "pending": total - done,
            "ratio": round(done / total, 2) if total else 0,
        },
    }


def get_plan(conn: sqlite3.Connection, week_offset: int = 0) -> dict[str, Any]:
    return get_plan_for_dates(conn, _plan_window(week_offset))


def mark_item_done(
    conn: sqlite3.Connection, item_id: int, done: bool = True
) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM study_plans WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return None
    status = "done" if done else "pending"
    done_count = row["target_count"] if done else 0
    conn.execute(
        "UPDATE study_plans SET status = ?, done_count = ? WHERE id = ?",
        (status, done_count, item_id),
    )
    conn.commit()
    return {"id": item_id, "status": status, "done_count": done_count}


def _streak_days(conn: sqlite3.Connection) -> tuple[int, int | None]:
    """Return (current consecutive streak, idle days since last practice)."""
    rows = conn.execute("SELECT created_at FROM practice_records").fetchall()
    studied = {(row["created_at"] or "")[:10] for row in rows if row["created_at"]}
    if not studied:
        return 0, None
    today = _today()
    streak = 0
    cursor = today
    while cursor.isoformat() in studied:
        streak += 1
        cursor -= timedelta(days=1)
    last = max(studied)
    idle = (today - date.fromisoformat(last)).days
    return streak, idle


def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 9:
        return "早上好"
    if hour < 12:
        return "上午好"
    if hour < 18:
        return "下午好"
    return "晚上好"


def get_insights(conn: sqlite3.Connection) -> dict[str, Any]:
    """Proactive dashboard payload: what to do today and why."""
    settings = get_or_create_settings(conn)
    report = get_report(conn)
    today_iso = _today().isoformat()
    today_items = [
        _item_to_dict(row)
        for row in conn.execute(
            "SELECT * FROM study_plans WHERE plan_date = ? AND status = 'pending' "
            "ORDER BY id",
            (today_iso,),
        ).fetchall()
    ]
    all_today = conn.execute(
        "SELECT status FROM study_plans WHERE plan_date = ?", (today_iso,)
    ).fetchall()
    done_today = sum(1 for row in all_today if row["status"] == "done")
    weakest = report["weak_types"][0] if report["weak_types"] else None
    streak, idle = _streak_days(conn)
    countdown = _days_until_exam(settings)

    suggestions = list(report["suggestions"])
    if countdown is not None:
        if countdown > 0:
            suggestions.insert(0, f"距离考试还有 {countdown} 天，按计划保持每日训练即可。")
        else:
            suggestions.insert(0, "考试日期已到或已过，建议复盘错题并保持轻量复习。")
    if idle is not None and idle >= 3:
        suggestions.insert(0, f"已经 {idle} 天没有练习，今天先完成 1 组单词复习找回节奏。")

    return {
        "greeting": _greeting(),
        "due_word_count": len(report["due_words"]),
        "weakest_type": weakest,
        "streak_days": streak,
        "idle_days": idle,
        "exam_countdown": countdown,
        "plan_ready": len(all_today) > 0,
        "today_tasks": today_items,
        "today_progress": {
            "total": len(all_today),
            "done": done_today,
            "ratio": round(done_today / len(all_today), 2) if all_today else 0,
        },
        "suggestions": suggestions[:4],
    }