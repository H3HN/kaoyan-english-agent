#!/usr/bin/env python3
"""Automated exam importer: PDF / URL / text -> DeepSeek -> SQLite.

Examples:
  python scripts/auto_import.py --pdf ~/2024英语一.pdf --year 2024 --text-number 1 --answer-key BCDAB
  python scripts/auto_import.py --url https://example.com/2024.pdf --year 2024 --text-number 1
  python scripts/auto_import.py --text-file passage.txt --year 2024 --text-number 1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx
from pypdf import PdfReader


def extract_pdf(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="public PDF URL")
    source.add_argument("--pdf", type=Path, help="local PDF file")
    source.add_argument("--text-file", type=Path, help="raw text file")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--exam", default="英语一", choices=["英语一", "英语二"])
    parser.add_argument("--text-number", type=int, default=1)
    parser.add_argument("--answer-key", default="", help="e.g. 21-25 BCDAB")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    payload = {
        "year": args.year,
        "exam_type": args.exam,
        "text_number": args.text_number,
        "answer_key": args.answer_key,
    }
    if args.url:
        payload["url"] = args.url
    elif args.pdf:
        payload["text"] = extract_pdf(args.pdf)
    else:
        payload["text"] = args.text_file.read_text(encoding="utf-8")

    try:
        response = httpx.post(
            f"{args.api.rstrip('/')}/api/exams/auto-import",
            json=payload,
            timeout=300,
            trust_env=False,
        )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        print(f"import failed: {exc}", file=sys.stderr)
        if getattr(exc, "response", None) is not None:
            print(exc.response.text[:500], file=sys.stderr)
        return 1

    result = response.json()
    print(
        json.dumps(
            {
                "ok": result["ok"],
                "passage_id": result["passage_id"],
                "question_ids": result["question_ids"],
                "analysis_source": result["analysis_source"],
                "answer_source": result["answer_source"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
