"""Deterministic evidence relocation for imported exam questions.

Recomputes ``source_sentence_id`` and ``location_status`` for every question of
a passage from the stored passage text and the sentence table. Nothing else
changes: publication status, review status, revision and analysis stay as they
are, so already-published practice content is upgraded in place.

Binding rules (same spirit as exam_import.locate_quote):
- A sentence is *reliable* only when its text occurs exactly once in the
  passage (whitespace-tolerant). Ambiguous sentences never bind.
- A quote binds a sentence only when it occurs exactly once and lies wholly
  inside exactly one reliable sentence (exact_quote).
- Repeated quotes -> ambiguous; quotes spanning several sentences ->
  multi_sentence; missing/short/unmatchable quotes -> pending.

The module never invents evidence: no source_quote, no binding.
"""
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from exam_import import locate_quote

STATUSES = ("exact_quote", "ambiguous", "multi_sentence", "pending")


class LocationError(ValueError):
    pass


def _whitespace_pattern(text: str) -> re.Pattern:
    parts = [re.escape(part) for part in text.split()]
    if not parts:
        return re.compile(r"(?!x)x")  # never matches
    return re.compile(r"\s+".join(parts))


def reliable_sentence_offsets(passage: str, sentence_rows: list[dict]) -> list[dict]:
    """Return reliable rows [{id, char_start, char_end}] for sentences whose
    text occurs exactly once in the passage."""
    reliable = []
    for row in sentence_rows:
        text = (row["text"] or "").strip()
        if len(text) < 2:
            continue
        matches = list(_whitespace_pattern(text).finditer(passage))
        if len(matches) != 1:
            continue
        reliable.append({
            "id": row["id"],
            "char_start": matches[0].start(),
            "char_end": matches[0].end(),
        })
    return reliable


def _passage_questions(conn: sqlite3.Connection, passage_id: str) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT id, number, source_quote, location_status, source_sentence_id "
        "FROM exam_questions WHERE passage_id=? ORDER BY number", (passage_id,))]


def relocate_passage(conn: sqlite3.Connection, passage_id: str) -> dict:
    """Compute new locations for one passage without writing anything."""
    passage_row = conn.execute(
        "SELECT id, text FROM exam_passages WHERE id=?", (passage_id,)).fetchone()
    if not passage_row:
        raise LocationError(f"文章不存在: {passage_id}")
    passage = passage_row["text"]
    sentence_rows = [dict(r) for r in conn.execute(
        "SELECT id, text, char_start, char_end FROM exam_sentences "
        "WHERE passage_id=? ORDER BY paragraph, sentence_index", (passage_id,))]
    reliable = reliable_sentence_offsets(passage, sentence_rows)

    updates = []
    for q in _passage_questions(conn, passage_id):
        outcome = locate_quote(q["source_quote"] or "", passage, reliable)
        updates.append({
            "question_id": q["id"],
            "number": q["number"],
            "old_status": q["location_status"],
            "old_sentence_id": q["source_sentence_id"],
            "new_status": outcome["location_status"],
            "new_sentence_id": outcome["source_sentence_id"],
        })

    offset_backfill = []
    for row in sentence_rows:
        match = next((r for r in reliable if r["id"] == row["id"]), None)
        if match and (row["char_start"] is None or row["char_end"] is None):
            offset_backfill.append({
                "id": row["id"],
                "char_start": match["char_start"],
                "char_end": match["char_end"],
            })

    counts = {status: sum(1 for u in updates if u["new_status"] == status)
              for status in STATUSES}
    counts["total"] = len(updates)
    return {
        "passage_id": passage_id,
        "reliable_sentences": len(reliable),
        "total_sentences": len(sentence_rows),
        "updates": updates,
        "offset_backfill": offset_backfill,
        "counts": counts,
    }


def apply_relocation(conn: sqlite3.Connection, report: dict, actor: str) -> None:
    """Persist a computed relocation report and record one audit event."""
    passage_id = report["passage_id"]
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        for u in report["updates"]:
            conn.execute(
                "UPDATE exam_questions SET source_sentence_id=?, location_status=? "
                "WHERE id=?", (u["new_sentence_id"], u["new_status"], u["question_id"]))
        for s in report["offset_backfill"]:
            conn.execute(
                "UPDATE exam_sentences SET char_start=?, char_end=? WHERE id=?",
                (s["char_start"], s["char_end"], s["id"]))
        revision = conn.execute(
            "SELECT revision FROM exam_passages WHERE id=?", (passage_id,)).fetchone()[0]
        conn.execute(
            "INSERT INTO bank_events (passage_id, revision, action, actor, created_at, snapshot_json) "
            "VALUES (?,?,?,?,datetime('now'),?)",
            (passage_id, revision, "evidence_located", actor,
             json.dumps({"counts": report["counts"],
                         "reliable_sentences": report["reliable_sentences"],
                         "offset_backfill": len(report["offset_backfill"]),
                         "updates": report["updates"]}, ensure_ascii=False)))


def relocate_all(conn: sqlite3.Connection, actor: str, *,
                 passage_ids: list[str] | None = None,
                 dry_run: bool = False,
                 imported_only: bool = True) -> dict:
    """Recompute evidence for all (or selected) passages.

    Returns a summary; only writes when dry_run is False.
    """
    if passage_ids is None:
        if imported_only:
            rows = conn.execute(
                "SELECT id FROM exam_passages WHERE id LIKE 'auto_%' "
                "OR id LIKE 'bank_%' OR id LIKE 'custom_%' ORDER BY id").fetchall()
        else:
            rows = conn.execute("SELECT id FROM exam_passages ORDER BY id").fetchall()
        passage_ids = [r["id"] for r in rows]

    reports, errors = [], []
    for pid in passage_ids:
        try:
            report = relocate_passage(conn, pid)
            if not dry_run:
                apply_relocation(conn, report, actor)
            reports.append(report)
        except (LocationError, sqlite3.Error) as exc:
            errors.append({"passage_id": pid, "error": str(exc)})

    status_totals = {status: sum(r["counts"][status] for r in reports)
                     for status in STATUSES}
    changed = sum(1 for r in reports for u in r["updates"]
                  if u["new_status"] != u["old_status"]
                  or u["new_sentence_id"] != u["old_sentence_id"])
    return {
        "passages": len(reports),
        "questions": sum(r["counts"]["total"] for r in reports),
        "bound": status_totals["exact_quote"],
        "status_totals": status_totals,
        "changed_questions": changed,
        "offset_backfilled": sum(len(r["offset_backfill"]) for r in reports),
        "reliable_sentence_ratio": (
            f"{sum(r['reliable_sentences'] for r in reports)}/"
            f"{sum(r['total_sentences'] for r in reports)}"),
        "dry_run": dry_run,
        "errors": errors,
        "reports": reports,
    }