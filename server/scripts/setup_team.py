#!/usr/bin/env python3
"""Restore the bundled bank and explicitly open basic practice in a NEW database."""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import db


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=db.DB_PATH)
    parser.add_argument('--actor', default='团队首次安装')
    args = parser.parse_args()
    target = args.database.resolve()
    if target.exists():
        parser.error('数据库已经存在，为保护题库和学习记录不覆盖。首次安装请使用全新数据库；已有环境请先备份并按建库操作说明迁移。')
    snapshot = BASE / 'data' / 'demo_snapshot.json'
    data = json.loads(snapshot.read_text(encoding='utf-8'))
    if data.get('format') != 'kaoyan-demo-snapshot' or len(data['questions']) != 340 or len(data['passages']) != 68:
        parser.error('随附题库快照不完整，未创建数据库')
    target.parent.mkdir(parents=True, exist_ok=True)
    db.DB_PATH = target
    import load_demo
    from question_bank import practice_readiness, transition
    load_demo.DB_PATH = target
    # Use the existing restore implementation, which resets approvals to draft.
    original_argv = sys.argv
    try:
        sys.argv = ['load_demo.py', '--snapshot', str(snapshot)]
        load_demo.main()
    finally:
        sys.argv = original_argv
    conn = db.connect()
    try:
        # Check the entire bank before explicitly opening any passage.
        for row in data['passages']:
            issues = practice_readiness(conn, row['id'])
            if issues:
                raise RuntimeError(f"{row['id']}: {'; '.join(issues)}")
        for row in data['passages']:
            revision = conn.execute('SELECT revision FROM exam_passages WHERE id=?', (row['id'],)).fetchone()[0]
            transition(conn, row['id'], revision, 'publish-practice', args.actor)
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
        published = conn.execute("SELECT count(*) FROM exam_passages WHERE publication_status='published'").fetchone()[0]
        questions = conn.execute("SELECT count(*) FROM exam_questions q JOIN exam_passages p ON p.id=q.passage_id WHERE p.publication_status='published'").fetchone()[0]
        if (published, questions) != (68, 340):
            raise RuntimeError(f'题库数量不符: {published}/{questions}')
        print(json.dumps({'published_passages': published, 'available_questions': questions, 'database': str(target)}, ensure_ascii=False))
        print('已开放基础练习，不等于全部解析经过人工审核；个人历史、密钥与原始PDF未共享。')
    finally:
        conn.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
