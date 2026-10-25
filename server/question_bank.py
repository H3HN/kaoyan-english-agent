"""Team-only question-bank operations. No HTTP routes; students read published data.

One passage is the atomic unit. Updates withdraw it and require review again.
All externally generated analysis must be completed before a write transaction.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from exam_import import (ImportValidationError, LETTERS, QUESTION_TYPES,
                         locate_quote, normalize_passage, split_passage, validate_extraction)


class BankError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def setup_history(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS bank_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        passage_id TEXT NOT NULL,
        revision INTEGER NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        created_at TEXT NOT NULL,
        snapshot_json TEXT NOT NULL
    )""")


def _snapshot(conn, passage_id):
    p = conn.execute("SELECT * FROM exam_passages WHERE id=?", (passage_id,)).fetchone()
    if not p:
        raise BankError("文章不存在")
    return {"passage": dict(p), "questions": [dict(r) for r in conn.execute(
        "SELECT * FROM exam_questions WHERE passage_id=? ORDER BY number", (passage_id,))],
        "sentences": [dict(r) for r in conn.execute(
        "SELECT * FROM exam_sentences WHERE passage_id=? ORDER BY paragraph,sentence_index", (passage_id,))]}


def _event(conn, passage_id, action, actor):
    snap = _snapshot(conn, passage_id)
    conn.execute("INSERT INTO bank_events (passage_id,revision,action,actor,created_at,snapshot_json) VALUES (?,?,?,?,?,?)",
                 (passage_id, snap["passage"]["revision"], action, actor, _now(),
                  json.dumps(snap, ensure_ascii=False)))


def _actor(actor):
    if not isinstance(actor, str) or not actor.strip() or len(actor.strip()) > 100:
        raise BankError("必须填写 1—100 字符的操作人")
    return actor.strip()


def _load(conn, passage_id, expected_revision):
    row = conn.execute("SELECT * FROM exam_passages WHERE id=?", (passage_id,)).fetchone()
    if not row:
        raise BankError("文章不存在")
    if type(expected_revision) is not int or row["revision"] != expected_revision:
        raise BankError(f"版本冲突，当前 revision={row['revision']}，请重新查看")
    return row


def _analysis(raw, correct):
    if not isinstance(raw, dict) or set(raw) != set(LETTERS):
        raise BankError("analysis 必须完整包含 A/B/C/D")
    result = {}
    for key in LETTERS:
        item = raw[key]
        if not isinstance(item, dict):
            raise BankError("每个选项分析必须是对象")
        trap, explanation = item.get("trapType"), item.get("explanation")
        if not isinstance(trap, str) or not trap.strip() or not isinstance(explanation, str) or not explanation.strip():
            raise BankError("每个选项须有非空 trapType 和 explanation")
        if (trap.strip() == "正确") != (key == correct):
            raise BankError("analysis 中的正确标签必须仅与当前答案一致")
        result[key] = {"trapType": trap.strip(), "explanation": explanation.strip()}
    return result


def _steps(raw):
    if not isinstance(raw, list) or not raw or any(not isinstance(s, str) or not s.strip() for s in raw):
        raise BankError("steps 必须是非空文本列表")
    return [s.strip() for s in raw]


def validate_entry(entry):
    if not isinstance(entry, dict):
        raise BankError("每篇文章必须是对象")
    year, exam, text_number = entry.get("year"), entry.get("exam_type"), entry.get("text_number")
    if type(year) is not int or not 2000 <= year <= 2100 or exam not in ("英语一", "英语二"):
        raise BankError("year 须为 2000—2100 整数，exam_type 须为英语一/英语二")
    if type(text_number) is not int:
        raise BankError("text_number 须为整数")
    paragraphs = entry.get("paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
        raise BankError("paragraphs 必须是非空段落文本列表")
    # An element represents exactly one paragraph; reject ambiguous embedded blank lines.
    if any("\n\n" in p.replace("\r\n", "\n") for p in paragraphs):
        raise BankError("paragraphs 每项只放一段，请拆开内含空行的段落")
    source = entry.get("source_note", "")
    if not isinstance(source, str) or len(source) > 2000:
        raise BankError("source_note 须为不超过 2000 字符的文本")
    try:
        valid = validate_extraction({"passage": "\n\n".join(normalize_passage(p) for p in paragraphs),
                                     "questions": entry.get("questions")}, text_number)
    except ImportValidationError as exc:
        raise BankError(str(exc)) from exc
    by_number = {int(q["number"]): q for q in entry["questions"]}
    for q in valid["questions"]:
        raw = by_number[q["number"]]
        source_type = raw.get("answer_source", "unknown")
        if source_type not in ("provided", "inferred", "manual", "unknown"):
            raise BankError("answer_source 无效")
        note = raw.get("answer_source_note", "")
        evidence = raw.get("evidence_note", "")
        if not isinstance(note, str) or not isinstance(evidence, str) or max(len(note), len(evidence)) > 2000:
            raise BankError("答案来源和证据备注须为不超过 2000 字符的文本")
        q.update(answer_source=source_type, answer_source_note=note.strip(), evidence_note=evidence.strip())
        q["analysis"] = _analysis(raw["analysis"], q["correct_answer"]) if "analysis" in raw else {}
        q["steps"] = _steps(raw["steps"]) if "steps" in raw else []
    return {"year": year, "exam_type": exam, "text_number": text_number,
            "passage": valid["passage"], "questions": valid["questions"], "source_note": source.strip()}


def import_batch(conn, document, actor, *, update=False):
    actor = _actor(actor)
    if not isinstance(document, dict) or document.get("format") != "kaoyan-question-bank-v1":
        raise BankError("format 必须为 kaoyan-question-bank-v1")
    entries = document.get("passages")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 100:
        raise BankError("passages 须包含 1—100 篇文章")
    results, seen = [], set()
    for index, entry in enumerate(entries, 1):
        try:
            data = validate_entry(entry)
            key = (data["year"], data["exam_type"], data["text_number"])
            if key in seen:
                raise BankError("同批次年度/考试类型/Text 重复")
            seen.add(key)
            result = _save(conn, data, entry, actor, update)
            results.append({"index": index, "ok": True, **result})
        except (BankError, sqlite3.Error) as exc:
            results.append({"index": index, "ok": False, "error": str(exc)})
    return {"ok": all(r["ok"] for r in results), "succeeded": sum(r["ok"] for r in results),
            "failed": sum(not r["ok"] for r in results), "results": results}


def _save(conn, data, raw, actor, update):
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute("SELECT * FROM exam_passages WHERE year=? AND exam_type=? AND text_number=?",
                                (data["year"], data["exam_type"], data["text_number"])).fetchall()
        # The two shipped partial demos use real year/Text labels but local
        # question numbers. Keep their records; do not let them reserve a real Text.
        placeholders = {"2024_en1_t1", "2023_en1_t1"}
        existing = [r for r in existing if not (
            r["id"] in placeholders and r["publication_status"] == "draft"
            and {q[0] for q in conn.execute("SELECT number FROM exam_questions WHERE passage_id=?", (r["id"],))}
            in ({1}, {1, 2})
        )]
        if existing and not update:
            raise BankError("该 Text 已存在；更正须使用 --update、passage_id 和 expected_revision")
        if update:
            pid = raw.get("passage_id")
            row = _load(conn, pid, raw.get("expected_revision"))
            if (row["year"], row["exam_type"], row["text_number"]) != (data["year"], data["exam_type"], data["text_number"]):
                raise BankError("更正不能改变年度/考试类型/Text")
            if len(existing) != 1:
                raise BankError("同一 Text 存在多份历史数据，须先人工处理，不能自动覆盖")
            revision = row["revision"] + 1
            _event(conn, pid, "before_update", actor)
        else:
            pid = f"bank_{data['year']}_{1 if data['exam_type']=='英语一' else 2}_{data['text_number']}"
            revision = 1
            conn.execute("INSERT INTO exam_passages (id,year,exam_type,text_number,text) VALUES (?,?,?,?,?)",
                         (pid, data["year"], data["exam_type"], data["text_number"], data["passage"]))
        # Preserve IDs for original question numbers; reject uncertain manual/partial mappings.
        old_questions = {r["number"]: r["id"] for r in conn.execute("SELECT id,number FROM exam_questions WHERE passage_id=?", (pid,))}
        if update and old_questions and set(old_questions) != {q["number"] for q in data["questions"]}:
            raise BankError("旧题号与新题号不一致，无法安全保留学习记录；请先人工迁移")
        conn.execute("UPDATE exam_questions SET source_sentence_id=NULL WHERE passage_id=?", (pid,))
        conn.execute("DELETE FROM sentence_breakdowns WHERE sentence_id IN (SELECT id FROM exam_sentences WHERE passage_id=?)", (pid,))
        conn.execute("DELETE FROM exam_sentences WHERE passage_id=?", (pid,))
        conn.execute("UPDATE exam_passages SET text=?,publication_status='draft',revision=?,reviewed_by='',reviewed_at='',published_at='',source_note=? WHERE id=?",
                     (data["passage"], revision, data["source_note"], pid))
        rows = split_passage(data["passage"])
        for i, row in enumerate(rows, 1):
            row["id"] = f"{pid}_r{revision}_s{i}"
            source = f"{data['year']} {data['exam_type']} Text {data['text_number']} · 第{row['paragraph']}段第{row['sentence_index']}句"
            conn.execute("INSERT INTO exam_sentences (id,passage_id,year,exam_type,text_number,paragraph,sentence_index,text,grammar_tags,source_label,char_start,char_end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (row["id"],pid,data["year"],data["exam_type"],data["text_number"],row["paragraph"],row["sentence_index"],row["text"],"[]",source,row["char_start"],row["char_end"]))
        for q in data["questions"]:
            location = locate_quote(q["source_quote"], data["passage"], rows)
            qid = old_questions.get(q["number"], f"{pid}_q{q['number']}")
            values = (qid,pid,data["year"],data["exam_type"],data["text_number"],q["number"],q["question_type"],q["content"],json.dumps(q["options"],ensure_ascii=False),q["correct_answer"],json.dumps(q["analysis"],ensure_ascii=False),json.dumps(q["steps"],ensure_ascii=False),location["source_sentence_id"],q["answer_source"],q["answer_source_note"],"pending",q["source_quote"],location["location_status"],q["evidence_note"])
            conn.execute("""INSERT INTO exam_questions (id,passage_id,year,exam_type,text_number,number,question_type,content,options_json,correct_answer,analysis_json,steps_json,source_sentence_id,answer_source,answer_source_note,review_status,source_quote,location_status,evidence_note)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET question_type=excluded.question_type,content=excluded.content,
                options_json=excluded.options_json,correct_answer=excluded.correct_answer,analysis_json=excluded.analysis_json,
                steps_json=excluded.steps_json,source_sentence_id=excluded.source_sentence_id,answer_source=excluded.answer_source,
                answer_source_note=excluded.answer_source_note,review_status=excluded.review_status,source_quote=excluded.source_quote,
                location_status=excluded.location_status,evidence_note=excluded.evidence_note""", values)
        _event(conn, pid, "updated" if update else "imported", actor)
    return {"passage_id": pid, "revision": revision, "publication_status": "draft"}


def export_entry(conn, passage_id):
    snap = _snapshot(conn, passage_id)
    p = snap["passage"]
    return {"format": "kaoyan-question-bank-v1", "passages": [{
        "passage_id": p["id"], "expected_revision": p["revision"], "year": p["year"],
        "exam_type": p["exam_type"], "text_number": p["text_number"],
        "source_note": p["source_note"], "paragraphs": p["text"].split("\n\n"),
        "questions": [{"number": q["number"], "question_type": q["question_type"], "content": q["content"],
                       "options": json.loads(q["options_json"]), "correct_answer": q["correct_answer"],
                       "answer_source": q["answer_source"], "answer_source_note": q["answer_source_note"],
                       "source_quote": q["source_quote"], "evidence_note": q["evidence_note"],
                       **({"analysis": json.loads(q["analysis_json"])} if json.loads(q["analysis_json"]) else {}),
                       **({"steps": json.loads(q["steps_json"])} if json.loads(q["steps_json"]) else {})}
                      for q in snap["questions"]]}]}


def readiness(conn, passage_id):
    entry = export_entry(conn, passage_id)["passages"][0]
    issues = []
    try:
        data = validate_entry(entry)
    except BankError as exc:
        return [str(exc)]
    if not data["source_note"]:
        issues.append("文章来源 source_note 未填写")
    for q in data["questions"]:
        n = q["number"]
        if q["answer_source"] not in ("provided", "manual") or not q["answer_source_note"]:
            issues.append(f"第 {n} 题须人工核对答案并记录可靠来源（不能只标模型推断）")
        if not q["analysis"] or not q["steps"]:
            issues.append(f"第 {n} 题缺完整解析/步骤")
        # Human reviewer can document multi-sentence/full-passage evidence instead of fake binding.
        row = conn.execute("SELECT location_status FROM exam_questions WHERE passage_id=? AND number=?", (passage_id,n)).fetchone()
        if row["location_status"] != "exact_quote" and not q["evidence_note"]:
            issues.append(f"第 {n} 题无唯一单句引文，请填写 evidence_note 说明跨句/全文证据")
    return issues


def practice_readiness(conn, passage_id):
    """Basic practice requires complete text/options and a supplied answer key, not analysis."""
    entry = export_entry(conn, passage_id)["passages"][0]
    try:
        data = validate_entry(entry)
    except BankError as exc:
        return [str(exc)]
    issues = []
    if not data["source_note"]:
        issues.append("文章来源 source_note 未填写")
    for q in data["questions"]:
        if q["answer_source"] not in ("provided", "manual") or not q["answer_source_note"]:
            issues.append(f"第 {q['number']} 题缺提供的答案及来源说明")
    if not conn.execute("SELECT 1 FROM exam_sentences WHERE passage_id=? LIMIT 1", (passage_id,)).fetchone():
        issues.append("文章尚未切句")
    return issues


def transition(conn, passage_id, expected_revision, action, actor):
    actor = _actor(actor)
    if action not in ("review", "publish", "publish-practice", "withdraw"):
        raise BankError("未知状态操作")
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        row = _load(conn, passage_id, expected_revision)
        if action == "publish-practice":
            if row["publication_status"] != "draft":
                raise BankError("只有草稿可开放基础练习")
            issues = practice_readiness(conn, passage_id)
            if issues:
                raise BankError("不能开放基础练习：" + "；".join(issues))
            conn.execute("UPDATE exam_passages SET publication_status='published',published_at=? WHERE id=?", (_now(), passage_id))
            # Publishing usable exercises does not claim their explanations were reviewed.
            conn.execute("UPDATE exam_questions SET review_status='practice' WHERE passage_id=?", (passage_id,))
        elif action == "review":
            if row["publication_status"] != "draft":
                raise BankError("只有草稿可审核")
            issues = readiness(conn, passage_id)
            if issues:
                raise BankError("不能审核：" + "；".join(issues))
            conn.execute("UPDATE exam_passages SET publication_status='reviewed',reviewed_by=?,reviewed_at=? WHERE id=?", (actor,_now(),passage_id))
            conn.execute("UPDATE exam_questions SET review_status='approved' WHERE passage_id=?", (passage_id,))
        elif action == "publish":
            if row["publication_status"] != "reviewed" or not row["reviewed_by"]:
                raise BankError("须先人工审核，再发布")
            issues = readiness(conn, passage_id)
            if issues:
                raise BankError("不能发布：" + "；".join(issues))
            conn.execute("UPDATE exam_passages SET publication_status='published',published_at=? WHERE id=?", (_now(),passage_id))
        else:
            conn.execute("UPDATE exam_passages SET publication_status='draft',reviewed_by='',reviewed_at='',published_at='' WHERE id=?", (passage_id,))
            conn.execute("UPDATE exam_questions SET review_status='pending' WHERE passage_id=?", (passage_id,))
        conn.execute("UPDATE exam_passages SET revision=revision+1 WHERE id=?", (passage_id,))
        _event(conn, passage_id, action, actor)
    return dict(conn.execute("SELECT id,publication_status,revision,reviewed_by,reviewed_at,published_at FROM exam_passages WHERE id=?", (passage_id,)).fetchone())


def generate_analysis(conn, passage_id, expected_revision, actor, analyzer):
    actor = _actor(actor)
    row = _load(conn, passage_id, expected_revision)
    if row["publication_status"] != "draft":
        raise BankError("只有草稿可生成解析；已发布内容须先撤回")
    entry = export_entry(conn, passage_id)["passages"][0]
    data = validate_entry(entry)
    # Calls happen before write lock; all five must be complete or nothing changes.
    generated = analyzer(data["passage"], data["questions"])
    if not isinstance(generated, dict):
        raise BankError("模型没有返回完整解析，未保存")
    prepared = []
    for q in data["questions"]:
        item = generated.get(q["number"], {})
        if not isinstance(item, dict):
            raise BankError(f"第 {q['number']} 题解析格式无效，未保存")
        prepared.append((q["number"], _analysis(item.get("analysis"), q["correct_answer"]), _steps(item.get("steps"))))
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        current = _load(conn, passage_id, expected_revision)
        if current["publication_status"] != "draft":
            raise BankError("状态已变更，请重新查看")
        for number, analysis, steps in prepared:
            conn.execute("UPDATE exam_questions SET analysis_json=?,steps_json=?,review_status='pending' WHERE passage_id=? AND number=?",
                         (json.dumps(analysis,ensure_ascii=False),json.dumps(steps,ensure_ascii=False),passage_id,number))
        conn.execute("UPDATE exam_passages SET revision=revision+1 WHERE id=?", (passage_id,))
        _event(conn, passage_id, "analysis_generated", actor)
    return {"passage_id": passage_id, "revision": expected_revision+1, "publication_status": "draft"}
