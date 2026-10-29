import sqlite3
from datetime import date, timedelta
from typing import Any

from tools import get_report

from .canvas import _canvas_action

def _schedule(conn: sqlite3.Connection) -> dict[str, Any]:
    report = get_report(conn)
    weak = report["weak_types"][:2]
    today = date.today()
    labels = ["今天", "明天", "后天"]
    tasks = []
    for index, label in enumerate(labels):
        if index == 0:
            title = (
                f"攻克「{weak[0]['type']}」：做 3 道同类真题"
                if weak
                else "完成一篇阅读并复盘定位句"
            )
            task_type = "READING"
            route = "/reading"
        elif index == 1:
            title = f"复习 {len(report['due_words']) or 8} 个到期词"
            task_type = "VOCAB"
            route = "/vocab"
        else:
            title = "拆解 1 个长难句并加入 2 个生词"
            task_type = "SENTENCE"
            route = "/studio"
        tasks.append(
            {
                "scheduled_date": (today + timedelta(days=index)).isoformat(),
                "day_label": label,
                "task_type": task_type,
                "title": title,
                "agent_reason": (
                    f"来自最近薄弱项：{weak[0]['type']}"
                    if weak and index == 0
                    else "按当前复习与训练节奏安排"
                ),
                "target_route": route,
                "status": "pending",
            }
        )
    conn.execute("DELETE FROM study_schedule_tasks WHERE status = 'pending'")
    for task in tasks:
        cursor = conn.execute(
            """
            INSERT INTO study_schedule_tasks
                (scheduled_date, day_label, task_type, title, agent_reason,
                 target_route, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task["scheduled_date"],
                task["day_label"],
                task["task_type"],
                task["title"],
                task["agent_reason"],
                task["target_route"],
                task["status"],
            ),
        )
        task["id"] = cursor.lastrowid
    conn.commit()
    widget = {"widget_type": "SCHEDULE_PLAN", "data": {"tasks": tasks}}
    return {
        "intro": "我已经把 3 天计划写入日历，并铺到左侧计划画布。可以逐项勾选执行。",
        "sections": [
            {
                "title": "排课依据",
                "items": [
                    f"总正确率：{int(report['accuracy'] * 100)}%",
                    f"到期词：{len(report['due_words'])} 个",
                    *(f"薄弱：{item['type']}（{int(item['accuracy'] * 100)}%）" for item in weak),
                ],
            }
        ],
        "tool_trace": [],
        "citations": [],
        "client_actions": [
            _canvas_action(
                "plan",
                {"source_label": "按错题生成的学习计划", "tasks": tasks},
                "按错题生成的学习计划",
            )
        ],
        "widgets": [widget],
        "llm_used": False,
    }
