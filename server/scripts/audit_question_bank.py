#!/usr/bin/env python3
"""Read-only question-bank audit. Exit 0: no structural errors; 1: defects; 2: input/output errors.

Examples:
  python scripts/audit_question_bank.py --snapshot data/demo_snapshot.json --output audit.json --markdown audit.md
  python scripts/audit_question_bank.py --database data/app.db --previous audit.json --triage triage.json

Reports are create-only. Human-review obligations do not imply approval or change
publication/review states. See bank_audit.attach_history for the triage format.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
from bank_audit import (ANSWER_SOURCES, LOCATION_STATUSES, REVIEW_STATUSES,
                        TABLES, attach_history, audit_database, audit_snapshot,
                        markdown_report)

REQUIRED_TABLES = tuple(TABLES.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--database", type=Path, help="Existing SQLite database; opened mode=ro")
    source.add_argument("--snapshot", type=Path, help="Portable kaoyan-demo-snapshot JSON (never restored)")
    parser.add_argument("--output", "--json", dest="output", type=Path, help="Create JSON report; default stdout")
    parser.add_argument("--markdown", type=Path, help="Create Markdown report")
    parser.add_argument("--previous", type=Path, help="Previous JSON audit report for stable-ID diff")
    parser.add_argument("--triage", type=Path, help="JSON issues mapping; annotations only, never suppression")
    args = parser.parse_args(argv)
    try:
        inputs = [p.resolve() for p in (args.database, args.snapshot, args.previous, args.triage) if p is not None]
        targets = [p.resolve() for p in (args.output, args.markdown) if p is not None]
        if len(set(targets)) != len(targets) or any(p in inputs for p in targets):
            raise ValueError("Report outputs must be distinct from each other and all inputs")
        for target in targets:
            if target.exists():
                raise FileExistsError(f"Report already exists (create-only): {target}")
        report = audit_snapshot(args.snapshot) if args.snapshot else audit_database(args.database or BASE / "data" / "app.db")
        previous = json.loads(args.previous.read_text(encoding="utf-8-sig")) if args.previous else None
        triage = json.loads(args.triage.read_text(encoding="utf-8-sig")) if args.triage else None
        attach_history(report, previous, triage)
        text = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        # Reserve both paths before writing either. O_EXCL prevents race overwrites;
        # on a second reservation failure close/unlink only our newly created file.
        handles = []
        try:
            for target in targets:
                handles.append((target, target.open("x", encoding="utf-8", newline="\n")))
        except OSError:
            for target, handle in handles:
                handle.close()
                target.unlink()
            raise
        try:
            contents = {args.output.resolve(): text} if args.output else {}
            if args.markdown:
                contents[args.markdown.resolve()] = markdown_report(report)
            for target, handle in handles:
                handle.write(contents[target])
        finally:
            for _, handle in handles:
                handle.close()
        if not args.output:
            print(text, end="")
        return 1 if report["summary"]["deterministic_issue_count"] else 0
    except (OSError, sqlite3.Error, ValueError, UnicodeError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
