#!/usr/bin/env python3
"""Restore the bundled bank and explicitly open basic practice in a NEW database."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import db
from snapshot_validation import validate_snapshot

SNAPSHOT = BASE / 'data' / 'demo_snapshot.json'
TABLES = {'passages': 'exam_passages', 'sentences': 'exam_sentences',
          'questions': 'exam_questions', 'breakdowns': 'sentence_breakdowns'}


@contextmanager
def _restore_database_path(path):
    """Scope every load_demo alias; imported connect/init_db use db's globals.

    This CLI is single-threaded. Always restore module globals/argv even when
    load_demo raises SystemExit, so embedded callers cannot hit the temp DB.
    """
    import load_demo
    # seed imports DATA_DIR for bundled read-only vocabulary assets. Import it
    # before narrowing db.DATA_DIR to the private database directory.
    import seed  # noqa: F401
    original = db.DB_PATH, db.DATA_DIR, load_demo.DB_PATH, sys.argv
    try:
        db.DB_PATH = load_demo.DB_PATH = path
        db.DATA_DIR = path.parent
        yield load_demo
    finally:
        db.DB_PATH, db.DATA_DIR, load_demo.DB_PATH, sys.argv = original


def _check_database(conn, counts):
    if [row[0] for row in conn.execute('PRAGMA integrity_check')] != ['ok']:
        raise RuntimeError('restored database failed integrity_check')
    if conn.execute('PRAGMA foreign_key_check').fetchall():
        raise RuntimeError('restored database failed foreign_key_check')
    actual = {key: conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
              for key, table in TABLES.items()}
    if actual != counts:
        raise RuntimeError(f'restored count mismatch: {actual!r} != {counts!r}')


def restore_snapshot(target, snapshot=SNAPSHOT, actor='团队首次安装'):
    """Validate first, restore privately, then atomically publish without overwrite.

    A sibling hard link is an atomic create-if-absent on both Windows and POSIX;
    unlike replace/rename it never clobbers a concurrently created destination.
    Unsupported filesystems fail closed, without an unsafe copy fallback.
    """
    target = Path(target).absolute()
    # Resolve the directory, not a potentially dangling destination symlink.
    target = target.parent.resolve() / target.name
    if os.path.lexists(target):
        raise FileExistsError('数据库已经存在，为保护题库和学习记录不覆盖。')
    snapshot = Path(snapshot)
    data = json.loads(snapshot.read_text(encoding='utf-8'))
    counts = validate_snapshot(data)
    if not isinstance(actor, str) or not 1 <= len(actor.strip()) <= 100:
        raise ValueError('必须填写 1—100 字符的操作人')
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{target.name}.restore-', suffix='.db', dir=target.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        from question_bank import practice_readiness, transition
        with _restore_database_path(temporary) as load_demo:
            # Feed exactly the already validated bytes, not a reread of a mutable
            # source path. This private file also disappears on every exit path.
            with tempfile.TemporaryDirectory(prefix=f'.{target.name}.snapshot-', dir=target.parent) as folder:
                validated = Path(folder) / 'snapshot.json'
                validated.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
                sys.argv = ['load_demo.py', '--snapshot', str(validated)]
                if load_demo.main() != 0:
                    raise RuntimeError('snapshot loader failed')
            conn = db.connect()
            try:
                _check_database(conn, counts)
                for row in data['passages']:
                    issues = practice_readiness(conn, row['id'])
                    if issues:
                        raise RuntimeError(f"{row['id']}: {'; '.join(issues)}")
                for row in data['passages']:
                    revision = conn.execute('SELECT revision FROM exam_passages WHERE id=?', (row['id'],)).fetchone()[0]
                    transition(conn, row['id'], revision, 'publish-practice', actor)
                _check_database(conn, counts)
                published = conn.execute("SELECT count(*) FROM exam_passages WHERE publication_status='published'").fetchone()[0]
                questions = conn.execute("SELECT count(*) FROM exam_questions q JOIN exam_passages p ON p.id=q.passage_id WHERE p.publication_status='published' AND q.review_status='practice'").fetchone()[0]
                if (published, questions) != (counts['passages'], counts['questions']):
                    raise RuntimeError(f'题库数量不符: {published}/{questions}')
                # Make the main file self-contained before linking it under a
                # different name. No WAL pages may be stranded at the temp name.
                checkpoint = conn.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
                if checkpoint[0] != 0:
                    raise RuntimeError('could not checkpoint restored database')
                if conn.execute('PRAGMA journal_mode=DELETE').fetchone()[0] != 'delete':
                    raise RuntimeError('could not finalize restored database journal')
            finally:
                conn.close()
        with temporary.open('r+b') as stream:
            os.fsync(stream.fileno())
        os.link(temporary, target)
        return {'published_passages': published, 'available_questions': questions, 'database': str(target)}
    finally:
        for path in (temporary, Path(f'{temporary}-wal'), Path(f'{temporary}-shm'), Path(f'{temporary}-journal')):
            path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=db.DB_PATH)
    parser.add_argument('--actor', default='团队首次安装')
    args = parser.parse_args()
    try:
        result = restore_snapshot(args.database, actor=args.actor)
    except (ValueError, OSError, sqlite3.Error, RuntimeError) as exc:
        parser.error(f'未创建数据库：{exc}')
    print(json.dumps(result, ensure_ascii=False))
    print('已开放基础练习，不等于全部解析经过人工审核；个人历史、密钥与原始PDF未共享。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
