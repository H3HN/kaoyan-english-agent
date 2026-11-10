"""First-install restoration safety, using only isolated temporary databases."""
import copy
from contextlib import closing, redirect_stdout
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

import db

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import setup_team
import load_demo
from snapshot_validation import SnapshotValidationError, validate_snapshot


class SetupTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = json.loads(setup_team.SNAPSHOT.read_text(encoding='utf-8'))

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.target = self.root / 'team.db'
        self.snapshot = self.root / 'snapshot.json'
        self.original = db.DB_PATH, db.DATA_DIR, load_demo.DB_PATH, sys.argv
        # Include the two slots init_db seeds, so snapshot counts cover all rows.
        self.data = copy.deepcopy(self.real)
        self.data['passages'] = [p for p in self.data['passages']
                                 if (p['year'], p['exam_type'], p['text_number'])
                                 in ((2024, '英语一', 1), (2023, '英语一', 1))]
        pids = {p['id'] for p in self.data['passages']}
        self.data['sentences'] = [s for s in self.data['sentences'] if s['passage_id'] in pids]
        self.data['questions'] = [q for q in self.data['questions'] if q['passage_id'] in pids]
        sids = {s['id'] for s in self.data['sentences']}
        self.data['breakdowns'] = [b for b in self.data['breakdowns'] if b['sentence_id'] in sids]
        self.recount()

    def recount(self):
        self.data['counts'] = {key: len(self.data[key]) for key in setup_team.TABLES}

    def restore(self, data=None):
        self.snapshot.write_text(json.dumps(data if data is not None else self.data, ensure_ascii=False), encoding='utf-8')
        with redirect_stdout(io.StringIO()):
            return setup_team.restore_snapshot(self.target, self.snapshot, 'test installer')

    def assert_clean(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.root.glob('.team.db.*')), [])
        self.assertEqual((db.DB_PATH, db.DATA_DIR, load_demo.DB_PATH, sys.argv), self.original)

    def test_real_expanded_snapshot_restores_all_counts_and_practice_status(self):
        self.assertGreater(self.real['counts']['passages'], 68)
        result = self.restore(self.real)
        self.assertEqual(result['published_passages'], self.real['counts']['passages'])
        self.assertEqual(result['available_questions'], self.real['counts']['questions'])
        with closing(sqlite3.connect(self.target)) as conn:
            for key, table in setup_team.TABLES.items():
                self.assertEqual(conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0], self.real['counts'][key])
            self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(conn.execute("SELECT DISTINCT review_status FROM exam_questions").fetchall(), [('practice',)])
            self.assertEqual(conn.execute("SELECT DISTINCT publication_status FROM exam_passages").fetchall(), [('published',)])
            self.assertEqual(conn.execute('PRAGMA journal_mode').fetchone()[0], 'delete')
        self.assertEqual(list(self.root.glob('.team.db.*')), [])
        self.assertEqual((db.DB_PATH, db.DATA_DIR, load_demo.DB_PATH, sys.argv), self.original)

    def test_manifest_mismatches_and_invalid_types_fail_before_loading(self):
        for key in setup_team.TABLES:
            for value in (-1, True, self.data['counts'][key] + 1):
                with self.subTest(key=key, value=value):
                    broken = copy.deepcopy(self.data)
                    broken['counts'][key] = value
                    with patch.object(load_demo, 'main') as loader:
                        with self.assertRaises(SnapshotValidationError):
                            self.restore(broken)
                        loader.assert_not_called()
                    self.assert_clean()

    def test_duplicate_ids_slots_and_bad_references_are_rejected(self):
        cases = []
        broken = copy.deepcopy(self.data)
        broken['questions'][1]['id'] = broken['questions'][0]['id']
        cases.append(broken)
        broken = copy.deepcopy(self.data)
        broken['passages'][1].update({k: broken['passages'][0][k] for k in ('year', 'exam_type', 'text_number')})
        cases.append(broken)
        for collection, key, value in [('sentences', 'passage_id', 'missing'),
                                       ('questions', 'source_sentence_id', 'missing'),
                                       ('questions', 'passage_id', 'missing'),
                                       ('questions', 'year', 2099)]:
            broken = copy.deepcopy(self.data)
            broken[collection][0][key] = value
            cases.append(broken)
        broken = copy.deepcopy(self.data)
        broken['questions'][0]['source_sentence_id'] = next(
            s['id'] for s in broken['sentences'] if s['passage_id'] != broken['questions'][0]['passage_id'])
        cases.append(broken)
        broken = copy.deepcopy(self.data)
        broken['breakdowns'] = [{'sentence_id': 'missing', 'data_json': '{}', 'llm_used': 0, 'created_at': ''}]
        broken['counts']['breakdowns'] = 1
        cases.append(broken)
        for i, broken in enumerate(cases):
            with self.subTest(case=i), self.assertRaises(SnapshotValidationError):
                self.restore(broken)
            self.assert_clean()

    def test_bad_question_structure_is_rejected_before_database_creation(self):
        for key, value in [('options_json', '{'), ('options_json', '{"A":"only"}'),
                           ('correct_answer', 'E'), ('number', 99),
                           ('analysis_json', '[]'), ('steps_json', '{}'),
                           ('content', ''), ('answer_source', 'inferred')]:
            with self.subTest(key=key, value=value):
                broken = copy.deepcopy(self.data)
                broken['questions'][0][key] = value
                with self.assertRaises(SnapshotValidationError):
                    self.restore(broken)
                self.assert_clean()

    def test_existing_database_is_byte_for_byte_unchanged(self):
        self.target.write_bytes(b'existing database and learning records')
        original = self.target.read_bytes()
        with patch.object(load_demo, 'main') as loader, self.assertRaises(FileExistsError):
            self.restore()
        loader.assert_not_called()
        self.assertEqual(self.target.read_bytes(), original)

    def test_failures_after_writes_leave_no_partial_target_or_sidecars(self):
        import question_bank
        for name, replacement in [('practice_readiness', lambda *args: ['not ready']),
                                  ('transition', None)]:
            with self.subTest(stage=name):
                kwargs = {'side_effect': RuntimeError('injected failure')} if replacement is None else {'side_effect': replacement}
                with patch.object(question_bank, name, **kwargs), self.assertRaises(RuntimeError):
                    self.restore()
                self.assert_clean()
        with patch.object(setup_team, '_check_database', side_effect=RuntimeError('bad restored counts')), self.assertRaises(RuntimeError):
            self.restore()
        self.assert_clean()

    def test_partial_publication_and_corrupt_integrity_never_publish_target(self):
        import question_bank
        transition = question_bank.transition
        calls = []
        def fail_second(*args):
            calls.append(args[1])
            if len(calls) == 2:
                raise RuntimeError('failed after first passage was published')
            return transition(*args)
        with patch.object(question_bank, 'transition', side_effect=fail_second), self.assertRaises(RuntimeError):
            self.restore()
        self.assertEqual(len(calls), 2)
        self.assert_clean()
        with closing(sqlite3.connect(':memory:')) as conn:
            conn.row_factory = sqlite3.Row
            conn.executescript(db.SCHEMA)
            conn.execute('PRAGMA foreign_keys=OFF')
            conn.execute("INSERT INTO sentence_breakdowns VALUES ('missing', '{}', 0, '')")
            with self.assertRaisesRegex(RuntimeError, 'foreign_key_check'):
                setup_team._check_database(conn, self.data['counts'])

    def test_loader_system_exit_restores_globals_and_cleans_up(self):
        def fail():
            self.assertNotEqual(db.DB_PATH, self.original[0])
            db.init_db()
            raise SystemExit('injected loader failure')
        with patch.object(load_demo, 'main', side_effect=fail), self.assertRaises(SystemExit):
            self.restore()
        self.assert_clean()

    def test_concurrent_destination_creation_is_never_overwritten(self):
        link = os.link
        def raced_link(source, target):
            Path(target).write_bytes(b'concurrent installer')
            return link(source, target)
        with patch.object(setup_team.os, 'link', side_effect=raced_link), self.assertRaises(FileExistsError):
            self.restore()
        self.assertEqual(self.target.read_bytes(), b'concurrent installer')
        self.assertEqual(list(self.root.glob('.team.db.*')), [])

    def test_unsupported_atomic_publish_fails_closed(self):
        with patch.object(setup_team.os, 'link', side_effect=OSError('hard links unavailable')), self.assertRaises(OSError):
            self.restore()
        self.assert_clean()

    def test_default_database_functions_are_scoped_to_temporary_database(self):
        sentinel = self.root / 'default.db'
        sentinel.write_bytes(b'never touch default database')
        with patch.object(db, 'DB_PATH', sentinel), patch.object(load_demo, 'DB_PATH', sentinel):
            result = self.restore()
            self.assertEqual(db.DB_PATH, sentinel)
            self.assertEqual(load_demo.DB_PATH, sentinel)
        self.assertEqual(sentinel.read_bytes(), b'never touch default database')
        self.assertEqual(result['published_passages'], self.data['counts']['passages'])


if __name__ == '__main__':
    unittest.main()
