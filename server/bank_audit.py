"""Read-only bank audit; machine integrity is NOT human content approval.

No application DB helpers are imported: neither snapshot ingestion nor a database
inspection can run migrations, seed, restore, or lifecycle transitions here.
Triage is annotation only; even resolved/false_positive findings stay in reports.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from exam_import import locate_quote

RULE_VERSION = "bank-audit-1"
REPORT_FORMAT = "kaoyan-bank-audit-v1"
TRIAGE_STATES = frozenset({"open", "in_progress", "resolved", "accepted_risk", "false_positive", "deferred"})
TABLES = {"passages": "exam_passages", "sentences": "exam_sentences", "questions": "exam_questions", "breakdowns": "sentence_breakdowns", "events": "bank_events"}
LOCATION_STATUSES = {"exact_quote", "pending", "ambiguous", "multi_sentence", "unverified"}
ANSWER_SOURCES = {"provided", "inferred", "manual", "unknown"}
REVIEW_STATUSES = {"pending", "practice", "approved"}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None


def _integer(value: Any) -> bool:
    return type(value) is int


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _provenance(path: Path, kind: str, raw: bytes, rows: dict) -> dict:
    base = Path(__file__).resolve().parent
    try:
        revision = subprocess.run(["git", "-C", str(base), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        revision = "unavailable"
    code = {"bank_audit.py": _hash(Path(__file__).read_bytes()),
            "exam_import.py": _hash((base / "exam_import.py").read_bytes())}
    cli = base / "scripts" / "audit_question_bank.py"
    if cli.is_file():
        code["scripts/audit_question_bank.py"] = _hash(cli.read_bytes())
    result = {"source_kind": kind, "source_path": str(path.resolve()), "source_sha256": _hash(raw),
              "normalized_rows_sha256": _hash(_json(rows).encode("utf-8")),
              "code_revision": revision, "code_sha256": code, "rule_version": RULE_VERSION,
              "timestamp": datetime.now(timezone.utc).isoformat()}
    wal = Path(str(path) + "-wal")
    if kind == "database" and wal.is_file():
        result["wal_sha256"] = _hash(wal.read_bytes())
    return result


def _audit(rows: dict, provenance: dict, missing_tables: list[str] | None = None) -> dict:
    deterministic: dict[str, dict] = {}
    human: dict[str, dict] = {}

    def add(rule: str, entity: str, message: str, *, review: bool = False, slot: str = "", **fields: Any) -> None:
        # Values, messages, timestamps and triage never participate in identity.
        issue_id = "audit-" + _hash(_json([entity, rule, slot]).encode("utf-8"))[:24]
        finding = {"issue_id": issue_id, "kind": rule, "rule": rule, "entity": entity,
                   "severity": "human_review" if review else "error", "message": message, **fields}
        if slot:
            finding["field"] = slot
        (human if review else deterministic)[issue_id] = finding

    for table in missing_tables or []:
        add("missing_table", "table:" + table, "Required question-bank table is missing", table=table)

    groups: dict[str, list[dict]] = {}
    for name in TABLES:
        values = rows.get(name, [])
        if not isinstance(values, list):
            add("invalid_collection", "collection:" + name, "Collection must be an array")
            values = []
        groups[name] = []
        seen = Counter()
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                add("invalid_row", f"{name}:row:{index}", "Row must be an object")
                continue
            row = dict(value)
            key_field = "sentence_id" if name == "breakdowns" else "id"
            identifier = row.get(key_field)
            if not _nonempty(identifier) and not (name == "events" and _integer(identifier)):
                entity = f"{name}:row:{index}"
                add("invalid_id", entity, "Entity ID is missing or invalid", slot=key_field)
            else:
                entity = name + ":" + str(identifier)
                seen[str(identifier)] += 1
            row["_entity"] = entity
            groups[name].append(row)
        for identifier, count in seen.items():
            if count > 1:
                add("duplicate_id", name + ":" + identifier, "Entity ID is duplicated", actual=count)

    passages, sentences, questions = (groups[k] for k in ("passages", "sentences", "questions"))
    by_pid = {p["id"]: p for p in passages if _nonempty(p.get("id"))}
    by_sid = {s["id"]: s for s in sentences if _nonempty(s.get("id"))}
    qs_by_pid: dict[str, list] = defaultdict(list)
    ss_by_pid: dict[str, list] = defaultdict(list)
    identities: dict[str, list] = defaultdict(list)
    coverage = {k: Counter() for k in ("publication_status", "location_status", "answer_source", "review_status")}

    for collection in ("sentences", "questions", "events"):
        for row in groups[collection]:
            pid = row.get("passage_id")
            passage = by_pid.get(pid) if isinstance(pid, str) else None
            if passage is None:
                add("orphan_passage", row["_entity"], "passage_id does not reference a passage", passage_id=pid)
            elif collection != "events":
                for field in ("year", "exam_type", "text_number"):
                    if row.get(field) != passage.get(field):
                        add("identity_mismatch", row["_entity"], "Child identity disagrees with its passage", slot=field, passage_id=pid)
            if collection in ("sentences", "questions") and isinstance(pid, str):
                (ss_by_pid if collection == "sentences" else qs_by_pid)[pid].append(row)

    for p in passages:
        entity, pid = p["_entity"], p.get("id")
        pid_key = pid if isinstance(pid, str) else ""
        qs, ss = qs_by_pid[pid_key], ss_by_pid[pid_key]
        text = p.get("text")
        tn = p.get("text_number")
        status = p.get("publication_status", "draft")
        coverage["publication_status"][str(status)] += 1
        if not isinstance(status, str) or status not in {"draft", "reviewed", "published", "archived"}:
            add("invalid_publication_status", entity, "Unknown publication status", value=status)
        if not _integer(p.get("year")) or not 1900 <= p["year"] <= 2200:
            add("invalid_year", entity, "Year must be an integer in 1900..2200")
        if p.get("exam_type") not in ("英语一", "英语二"):
            add("invalid_exam_type", entity, "Exam type must be 英语一 or 英语二")
        if not _integer(tn) or tn not in range(1, 5):
            add("invalid_text_number", entity, "Text number must be 1..4")
        identities[_json([p.get("year"), p.get("exam_type"), tn])].append(p)
        numbers = [q.get("number") for q in qs]
        placeholder = pid in {"2023_en1_t1", "2024_en1_t1"} and status == "draft" and sorted(numbers, key=_json) in ([1], [1, 2])
        if not placeholder:
            if len(qs) != 5:
                add("question_count", entity, "Passage must have five original questions", passage_id=pid, actual=len(qs))
            expected = list(range(21 + (tn - 1) * 5, 26 + (tn - 1) * 5)) if _integer(tn) and tn in range(1, 5) else []
            if sorted(numbers, key=_json) != sorted(expected, key=_json):
                add("question_numbers", entity, "Original question numbers are incomplete, invalid or duplicated", passage_id=pid, expected=expected, actual=sorted(numbers, key=_json))
        if not _nonempty(text):
            add("empty_passage", entity, "Passage text must be nonempty", passage_id=pid)
        if not ss:
            add("missing_sentences", entity, "Passage has no sentence records", passage_id=pid)
        if not _nonempty(p.get("source_note")):
            add("missing_source_note", entity, "Human must verify source/provenance", review=True, passage_id=pid)
        add("passage_content_review", entity, "Human must compare passage text and provenance against the original source; machine checks do not approve content", review=True, passage_id=pid, publication_status=status, recorded_reviewed_by=p.get("reviewed_by", ""))

    for identity, ps in identities.items():
        if len(ps) > 1:
            add("duplicate_identity", "identity:" + identity, "Multiple passages occupy the same exam slot", passage_ids=sorted((p.get("id") for p in ps), key=_json))

    for s in sentences:
        entity, pid = s["_entity"], s.get("passage_id")
        p = by_pid.get(pid) if isinstance(pid, str) else None
        start, end, text = s.get("char_start"), s.get("char_end"), s.get("text")
        if not _nonempty(text):
            add("empty_sentence", entity, "Sentence text must be nonempty", sentence_id=s.get("id"))
        if start is None and end is None:
            add("offset_unverified", entity, "Sentence offsets require human verification", review=True, sentence_id=s.get("id"), passage_id=pid)
        elif not (p and isinstance(p.get("text"), str) and _integer(start) and _integer(end) and 0 <= start < end <= len(p["text"]) and p["text"][start:end] == text):
            add("invalid_offset", entity, "Sentence offsets do not reconstruct its original text", sentence_id=s.get("id"), passage_id=pid)
        for field in ("paragraph", "sentence_index"):
            if not _integer(s.get(field)) or s[field] < 1:
                add("invalid_sentence_position", entity, "Sentence position must be a positive integer", slot=field)

    for q in questions:
        entity, pid, number = q["_entity"], q.get("passage_id"), q.get("number")
        common = {"passage_id": pid, "question_number": number, "question_id": q.get("id")}
        if not _integer(number) or number not in range(21, 41):
            add("invalid_question_number", entity, "Original question number must be 21..40", **common)
        if not _nonempty(q.get("content")):
            add("empty_question", entity, "Question stem must be nonempty", **common)
        for field, allowed, rule in (("answer_source", ANSWER_SOURCES, "invalid_answer_source"), ("review_status", REVIEW_STATUSES, "invalid_review_status"), ("location_status", LOCATION_STATUSES, "invalid_location_status")):
            default = {"answer_source": "unknown", "review_status": "pending", "location_status": "unverified"}[field]
            value = q.get(field, default)
            coverage[field][str(value)] += 1
            if not isinstance(value, str) or value not in allowed:
                add(rule, entity, "Invalid " + field, value=value, **common)
        if q.get("correct_answer") not in ("A", "B", "C", "D"):
            add("invalid_answer", entity, "Correct answer must be A/B/C/D", value=q.get("correct_answer"), **common)
        options = _decode(q.get("options_json", q.get("options")))
        if not isinstance(options, dict) or set(options) != set("ABCD") or any(not _nonempty(options.get(k)) for k in "ABCD"):
            add("invalid_options", entity, "Options must contain exactly four nonempty A/B/C/D entries", **common)
        for field, expected_type, fallback in (("analysis_json", dict, "analysis"), ("steps_json", list, "steps")):
            parsed = _decode(q.get(field, q.get(fallback)))
            if not isinstance(parsed, expected_type):
                add("invalid_json", entity, "Invalid JSON structure for " + field, slot=field, **common)
            if not parsed:
                add("analysis_needs_review", entity, "Human must supply/check explanation and reasoning steps", review=True, slot=field, **common)
        sid = q.get("source_sentence_id")
        sentence = by_sid.get(sid) if isinstance(sid, str) else None
        if sid is not None and sid != "" and (not sentence or sentence.get("passage_id") != pid):
            add("orphan_source_sentence", entity, "Evidence sentence does not belong to this passage", source_sentence_id=sid, **common)
        if q.get("location_status") == "exact_quote":
            if not sid:
                add("location_without_sentence", entity, "exact_quote requires a source sentence", **common)
            quote = q.get("source_quote")
            passage = by_pid.get(pid) if isinstance(pid, str) else None
            candidates = [s for s in ss_by_pid.get(pid, []) if _integer(s.get("char_start")) and _integer(s.get("char_end"))] if isinstance(pid, str) else []
            located = locate_quote(quote, passage["text"], candidates) if _nonempty(quote) and passage and isinstance(passage.get("text"), str) else {}
            if not sentence or sentence.get("passage_id") != pid or located.get("location_status") != "exact_quote" or located.get("source_sentence_id") != sid:
                add("invalid_source_quote", entity, "Evidence must uniquely match the full passage (ignoring whitespace) and bind this source sentence", **common)
        else:
            add("location_pending", entity, "Human must verify evidence location", review=True, **common)
        if q.get("answer_source", "unknown") in ("inferred", "unknown"):
            add("answer_needs_review", entity, "Human must compare answer with reliable original answer key", review=True, **common)
        add("question_content_review", entity, "Human must verify stem/options fidelity, answer correctness and explanation quality against original materials; recorded approval is not re-certified", review=True, recorded_review_status=q.get("review_status", "pending"), **common)

    for row in groups["breakdowns"]:
        sid = row.get("sentence_id")
        if not isinstance(sid, str) or sid not in by_sid:
            add("orphan_breakdown", row["_entity"], "Breakdown references a missing sentence", sentence_id=sid)
        if not isinstance(_decode(row.get("data_json")), dict):
            add("invalid_json", row["_entity"], "Breakdown data must be a JSON object", slot="data_json")

    errors = sorted(deterministic.values(), key=lambda i: (i["entity"], i["rule"], i.get("field", "")))
    reviews = sorted(human.values(), key=lambda i: (i["entity"], i["rule"], i.get("field", "")))
    summary = {"passages": len(passages), "questions": len(questions), "sentences": len(sentences),
               "published_passages": sum(p.get("publication_status") == "published" for p in passages),
               "deterministic_issue_count": len(errors), "human_review_item_count": len(reviews)}
    return {"format": REPORT_FORMAT, "database": provenance["source_path"] if provenance["source_kind"] == "database" else None,
            "read_only": True, "provenance": provenance, "summary": summary,
            "coverage": {**{k: dict(sorted(v.items())) for k, v in coverage.items()}, "by_exam": [
                {"year": ps[0].get("year"), "exam_type": ps[0].get("exam_type"), "text_number": ps[0].get("text_number"),
                 "passages": sum(p.get("publication_status") == "published" for p in ps),
                 "questions": sum(len(qs_by_pid.get(p.get("id") if isinstance(p.get("id"), str) else "", [])) for p in ps if p.get("publication_status") == "published")}
                for _, ps in sorted(identities.items()) if any(p.get("publication_status") == "published" for p in ps)]},
            "deterministic_issues": errors, "human_review_items": reviews,
            "review_notice": "Human review items are obligations, not machine approval. Triage never suppresses findings or changes the source."}


def audit_snapshot(path: Path) -> dict:
    path = Path(path)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict) or data.get("format") != "kaoyan-demo-snapshot":
        raise ValueError("Expected kaoyan-demo-snapshot object")
    rows = {}
    for key in TABLES:
        value = data.get(key, None if key in ("passages", "sentences", "questions") else [])
        rows[key] = sorted(value, key=_json) if isinstance(value, list) else value
    # Deliberately no restore helper: publication/review states remain untouched.
    report = _audit(rows, _provenance(path, "snapshot", raw, rows))
    if "counts" in data:
        actual = {k: len(rows[k]) if isinstance(rows[k], list) else 0 for k in ("passages", "sentences", "questions", "breakdowns")}
        if data["counts"] != actual:
            entity, rule = "snapshot:counts", "snapshot_counts"
            report["deterministic_issues"].append({"issue_id": "audit-" + _hash(_json([entity, rule, ""]).encode())[:24], "entity": entity, "kind": rule, "rule": rule, "severity": "error", "message": "Declared snapshot counts differ from rows", "actual": actual})
            report["deterministic_issues"].sort(key=lambda i: (i["entity"], i["rule"], i.get("field", "")))
            report["summary"]["deterministic_issue_count"] += 1
    return report


def audit_database(path: Path) -> dict:
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Database does not exist: {path}")
    before = path.read_bytes()
    wal_path = Path(str(path) + "-wal")
    wal_before = wal_path.read_bytes() if wal_path.is_file() else None
    # mode=ro, NOT immutable=1: committed WAL contents must remain visible.
    # The explicit read transaction below fixes one logical row snapshot. Raw
    # main/WAL hashes are separate file captures, not a SQLite backup image;
    # reject detected concurrent changes and recommend a stable backup.
    conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        conn.execute("BEGIN")
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing = sorted(set(TABLES.values()) - tables)
        rows = {name: [dict(r) for r in conn.execute('SELECT * FROM "' + table + '"')] if table in tables else [] for name, table in TABLES.items()}
        # Canonical row order makes provenance independent of insertion order.
        rows = {key: sorted(value, key=_json) for key, value in rows.items()}
        provenance = _provenance(path, "database", before, rows)
        provenance["source_capture"] = "Raw main/WAL file hashes captured separately; normalized_rows_sha256 identifies the transaction-consistent logical snapshot. Use a quiescent backup for archival byte provenance."
        if wal_before is not None:
            provenance["wal_sha256"] = _hash(wal_before)
        else:
            provenance.pop("wal_sha256", None)
        report = _audit(rows, provenance, missing)
        wal_after = wal_path.read_bytes() if wal_path.is_file() else None
        if path.read_bytes() != before or wal_after != wal_before:
            raise ValueError("Database changed during audit; retry against a stable backup")
        return report
    finally:
        conn.close()


def _findings(report: dict) -> dict[str, dict]:
    if not isinstance(report, dict) or report.get("format") != REPORT_FORMAT:
        raise ValueError("Previous report must be a kaoyan-bank-audit-v1 report")
    result = {}
    for key in ("deterministic_issues", "human_review_items"):
        if not isinstance(report.get(key), list):
            raise ValueError("Report findings must be arrays")
        for item in report[key]:
            if not isinstance(item, dict) or not _nonempty(item.get("issue_id")) or item["issue_id"] in result:
                raise ValueError("Report contains missing/duplicate issue IDs")
            result[item["issue_id"]] = item
    return result


def attach_history(report: dict, previous: dict | None = None, triage: dict | None = None) -> dict:
    """Attach ID-based comparison and validated annotations, never filter findings.

    Triage shape: {"issues": {"audit-...": {"state": "open", "reviewer":
    "person", "note": "reason"}}}. IDs may belong to current or previous reports.
    """
    current = _findings(report)
    old = _findings(previous) if previous is not None else {}
    if previous is not None:
        if not isinstance(previous.get("provenance"), dict) or previous["provenance"].get("rule_version") != RULE_VERSION:
            raise ValueError("Previous report rule version does not match")
        report["diff"] = {"new": sorted(current.keys() - old.keys()), "resolved": sorted(old.keys() - current.keys()), "persistent": sorted(current.keys() & old.keys())}
    if triage is not None:
        if not isinstance(triage, dict) or set(triage) != {"issues"} or not isinstance(triage["issues"], dict):
            raise ValueError("Triage must be an object with an issues mapping")
        annotations = {}
        for issue_id, entry in sorted(triage["issues"].items()):
            if issue_id not in current and issue_id not in old:
                raise ValueError("Unknown triage issue ID: " + issue_id)
            if not isinstance(entry, dict) or set(entry) != {"state", "reviewer", "note"}:
                raise ValueError("Triage entry requires state/reviewer/note")
            if not isinstance(entry["state"], str) or entry["state"] not in TRIAGE_STATES:
                raise ValueError("Unknown triage state: " + str(entry["state"]))
            if not _nonempty(entry["reviewer"]) or not isinstance(entry["note"], str):
                raise ValueError("Triage reviewer must be nonempty and note must be text")
            annotations[issue_id] = dict(entry)
        report["triage"] = annotations
        for issue_id, entry in annotations.items():
            if issue_id in current:
                current[issue_id]["triage"] = dict(entry)
    return report


def markdown_report(report: dict) -> str:
    def safe(value: Any) -> str:
        return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|").replace("`", "'")
    p = report["provenance"]
    lines = ["# Question-bank audit", "", report["review_notice"], "", "## Provenance", ""]
    for key in ("source_kind", "source_path", "source_sha256", "normalized_rows_sha256", "code_revision", "rule_version", "timestamp"):
        lines.append(f"- {key}: {safe(p.get(key, 'unavailable'))}")
    lines += [f"- code_sha256: {safe(_json(p['code_sha256']))}", "", "## Summary", "", "```json", json.dumps(report["summary"], ensure_ascii=False, indent=2), "```", ""]
    if "source_capture" in p:
        lines += ["- source_capture: " + safe(p["source_capture"]), "- wal_sha256: " + safe(p.get("wal_sha256", "none")), ""]
    if "diff" in report:
        lines += ["## Previous-report comparison", ""]
        for state, ids in report["diff"].items():
            lines += [f"### {state} ({len(ids)})", ""] + ["- " + i for i in ids] + [""]
    if "triage" in report:
        lines += ["## Triage annotations (including resolved historical IDs)", "", "```json", json.dumps(report["triage"], ensure_ascii=False, sort_keys=True, indent=2), "```", ""]
    for title, key in (("Deterministic structural findings", "deterministic_issues"), ("Human content review (not approval)", "human_review_items")):
        lines += ["## " + title, "", "| ID | Entity | Rule | Finding | Triage |", "|---|---|---|---|---|"]
        for item in report[key]:
            lines.append("| " + " | ".join(safe(v) for v in (item["issue_id"], item["entity"], item["rule"], item["message"], _json(item.get("triage", {})))) + " |")
        lines += [""]
    return "\n".join(lines) + "\n"
