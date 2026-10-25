#!/usr/bin/env python3
"""Retired HTTP importer; use the offline team question-bank CLI."""
import sys


def main():
    print("旧 HTTP 自动导入入口已停用（410）。\n"
          "团队请改用：\n"
          "  python scripts/question_bank.py prepare-pdf --help\n"
          "  python scripts/question_bank.py validate bank.json\n"
          "  python scripts/question_bank.py import bank.json --actor 操作人\n"
          "草稿经人工审核、发布后才对学生可见。详见 docs/题库建库与发布操作说明.md。",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
