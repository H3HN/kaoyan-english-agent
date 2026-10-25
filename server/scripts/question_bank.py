#!/usr/bin/env python3
"""Offline team CLI. Run from server: python scripts/question_bank.py --help."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from db import DB_PATH, SCHEMA, migrate_schema
from question_bank import (BankError, export_entry, generate_analysis, import_batch,
                           readiness, transition, validate_entry)


def template():
    passage = ["This is a synthetic demonstration paragraph for testing the question bank. It is not an authentic examination passage and must not be released as a real examination.",
               "A second paragraph demonstrates how paragraph boundaries are stored. The team must replace all example content with reviewed material before publishing."]
    return {"format": "kaoyan-question-bank-v1", "passages": [{
        "year": 2025, "exam_type": "英语一", "text_number": 1,
        "source_note": "", "paragraphs": passage,
        "questions": [{"number": n, "question_type": "细节题", "content": f"Synthetic example question {n}: replace before use.",
                       "options": {"A": "Example A", "B": "Example B", "C": "Example C", "D": "Example D"},
                       "correct_answer": "A", "answer_source": "unknown", "answer_source_note": "",
                       "source_quote": "", "evidence_note": ""} for n in range(21,26)]}]}


def _write(data, output):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        # Do not silently overwrite a teammate's edits.
        with Path(output).open("x", encoding="utf-8") as f:
            f.write(text + "\n")
        print(json.dumps({"output": str(Path(output).resolve())}, ensure_ascii=False))
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="团队题库管理：JSON → 草稿 → 解析 → 人工审核 → 发布；学生无管理入口")
    parser.add_argument("--database", type=Path, default=DB_PATH, help="默认使用 server/data/app.db；请先备份")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("template", help="输出明确标记为合成内容的 JSON 格式模板")
    p.add_argument("--output")
    p = sub.add_parser("validate", help="仅校验 JSON，不连接数据库")
    p.add_argument("file", type=Path)
    p = sub.add_parser("import", help="批量导入；每篇独立事务并返回成功/失败清单")
    p.add_argument("file", type=Path)
    p.add_argument("--actor", required=True)
    p.add_argument("--update", action="store_true", help="更正现有文章，须提供 passage_id 和 expected_revision；撤回学生访问")
    p = sub.add_parser("list")
    p.add_argument("--status", choices=["draft","reviewed","published"])
    for cmd in ("show", "export", "history"):
        p = sub.add_parser(cmd)
        p.add_argument("passage_id")
        if cmd == "export": p.add_argument("--output")
    for cmd in ("analyze", "review", "publish", "publish-practice", "withdraw"):
        p = sub.add_parser(cmd)
        p.add_argument("passage_id")
        p.add_argument("--revision", type=int, required=True)
        p.add_argument("--actor", required=True)
        if cmd == "review":
            p.add_argument("--confirm-checked", action="store_true", help="确认已逐题核对原文、选项、可靠答案、证据和解析")
    p = sub.add_parser("prepare-pdf", help="可选：本地文字版 PDF 经模型提取为草稿 JSON，不直接入库")
    p.add_argument("pdf", type=Path)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--exam", choices=["英语一","英语二"], required=True)
    p.add_argument("--text-number", type=int, choices=range(1,5), required=True)
    p.add_argument("--answer-key", default="")
    p.add_argument("--source-note", default="")
    p.add_argument("--answer-source-note", default="")
    p.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "template":
            _write(template(), args.output)
            return 0
        if args.command == "prepare-pdf":
            from pypdf import PdfReader
            from llm import extract_exam_text
            from exam_import import expected_numbers, parse_answer_key, validate_extraction
            parse_answer_key(args.answer_key, expected_numbers(args.text_number))
            if args.pdf.stat().st_size > 30*1024*1024:
                raise BankError("PDF 超过 30MB")
            raw = "\n\n".join(p.extract_text() or "" for p in PdfReader(args.pdf).pages)
            if not raw.strip(): raise BankError("PDF 无可提取文本，扫描件需先 OCR")
            # Reuse established Text slicing, with the known original-layout limitations.
            from app import _slice_text
            sliced = _slice_text(raw,args.text_number)
            if len(sliced) > 50000:
                raise BankError("目标 Text 超过 50000 字符，请先分离文章和五题，避免截断")
            extracted = extract_exam_text(sliced,args.year,args.exam,args.text_number,args.answer_key)
            valid = validate_extraction(extracted,args.text_number,args.answer_key)
            questions = valid["questions"]
            for q in questions:
                q.update(answer_source=valid["answer_source"], answer_source_note=args.answer_source_note, evidence_note="")
            _write({"format":"kaoyan-question-bank-v1", "passages":[{
                "year":args.year,"exam_type":args.exam,"text_number":args.text_number,
                "source_note":args.source_note,"paragraphs":valid["passage"].split("\n\n"),"questions":questions}]}, args.output)
            return 0
        if args.command in ("validate", "import"):
            if args.file.stat().st_size > 10*1024*1024: raise BankError("JSON 文件超过 10MB")
            doc = json.loads(args.file.read_text(encoding="utf-8-sig"))
            if args.command == "validate":
                if not isinstance(doc,dict) or doc.get("format") != "kaoyan-question-bank-v1": raise BankError("format 无效")
                entries=doc.get("passages")
                if not isinstance(entries,list) or not 1 <= len(entries) <= 100: raise BankError("passages 须含 1—100 篇")
                results=[]
                for i,entry in enumerate(entries,1):
                    try:
                        valid=validate_entry(entry)
                        results.append({"index":i,"valid":True,"year":valid["year"],"text_number":valid["text_number"]})
                    except BankError as exc: results.append({"index":i,"valid":False,"error":str(exc)})
                _write({"results":results},None)
                return 0 if all(r["valid"] for r in results) else 1
        # Team owns filesystem access; no unauthenticated HTTP management API is added.
        args.database.parent.mkdir(parents=True, exist_ok=True)
        conn=sqlite3.connect(args.database)
        conn.row_factory=sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            conn.executescript(SCHEMA)
            migrate_schema(conn)
            conn.commit()
            if args.command == "import":
                result=import_batch(conn,doc,args.actor,update=args.update)
                _write(result,None)
                return 0 if result["ok"] else 1
            if args.command == "list":
                sql="SELECT id,year,exam_type,text_number,publication_status,revision,reviewed_by,source_note FROM exam_passages"
                rows=conn.execute(sql+(" WHERE publication_status=?" if args.status else "")+" ORDER BY year DESC,text_number",(args.status,) if args.status else ()).fetchall()
                _write({"items":[dict(r) for r in rows]},None)
            elif args.command == "export": _write(export_entry(conn,args.passage_id),args.output)
            elif args.command == "show":
                result=export_entry(conn,args.passage_id)
                p=conn.execute("SELECT publication_status,revision,reviewed_by,reviewed_at,published_at FROM exam_passages WHERE id=?",(args.passage_id,)).fetchone()
                _write({"state":dict(p),"review_issues":readiness(conn,args.passage_id),"document":result},None)
            elif args.command == "history":
                rows=conn.execute("SELECT * FROM bank_events WHERE passage_id=? ORDER BY id",(args.passage_id,)).fetchall()
                _write({"events":[{**dict(r),"snapshot_json":json.loads(r["snapshot_json"])} for r in rows]},None)
            elif args.command == "analyze":
                from llm import analyze_imported_questions_batch
                _write(generate_analysis(conn,args.passage_id,args.revision,args.actor,analyze_imported_questions_batch),None)
            else:
                if args.command == "review" and not args.confirm_checked: raise BankError("审核须填写 --confirm-checked，确认已人工核对")
                _write(transition(conn,args.passage_id,args.revision,args.command,args.actor),None)
        finally: conn.close()
        return 0
    except (BankError, ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"ok":False,"error":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
