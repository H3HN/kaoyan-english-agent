#!/usr/bin/env python3
"""Recompute evidence locations for imported questions. Run from server:

    python scripts/locate_evidence.py --actor "操作人" --dry-run
    python scripts/locate_evidence.py --actor "操作人"
    python scripts/locate_evidence.py --actor "操作人" --passages bank_2018_1_1 auto_62abb41c

Deterministic and idempotent. Only source_sentence_id and location_status of
questions change (plus NULL sentence offsets get backfilled); publication,
review status, revision and analyses are untouched. One audit event per
passage is written to bank_events unless --dry-run is set.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from db import DB_PATH, SCHEMA, migrate_schema  # noqa: E402
from evidence_locator import relocate_all  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="批量重算题目原文证据定位（确定性、幂等；不改动发布/审核状态）")
    parser.add_argument("--database", type=Path, default=DB_PATH, help="默认 server/data/app.db；请先备份")
    parser.add_argument("--actor", required=True, help="审计署名（1—100 字符）")
    parser.add_argument("--dry-run", action="store_true", help="只计算并输出统计，不写库、不记审计")
    parser.add_argument("--passages", nargs="*", default=None, help="只处理指定 passage_id；缺省处理全部 auto_/bank_/custom_ 导入篇章")
    args = parser.parse_args(argv)

    if not isinstance(args.actor, str) or not args.actor.strip() or len(args.actor.strip()) > 100:
        print(json.dumps({"ok": False, "error": "必须填写 1—100 字符的操作人"}, ensure_ascii=False), file=sys.stderr)
        return 1
    actor = args.actor.strip()

    if not args.database.exists():
        print(json.dumps({"ok": False, "error": f"数据库不存在: {args.database}（请先用 setup_team.py 初始化）"}, ensure_ascii=False), file=sys.stderr)
        return 1
    conn = sqlite3.connect(args.database)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(SCHEMA)
        migrate_schema(conn)
        conn.commit()
        summary = relocate_all(conn, actor, passage_ids=args.passages, dry_run=args.dry_run)
        print(json.dumps({
            "ok": not summary["errors"],
            "passages": summary["passages"],
            "questions": summary["questions"],
            "bound_exact_quote": summary["bound"],
            "status_totals": summary["status_totals"],
            "changed_questions": summary["changed_questions"],
            "offset_backfilled": summary["offset_backfilled"],
            "reliable_sentences": summary["reliable_sentence_ratio"],
            "dry_run": summary["dry_run"],
            "errors": summary["errors"],
        }, ensure_ascii=False, indent=2))
        return 0 if not summary["errors"] else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())