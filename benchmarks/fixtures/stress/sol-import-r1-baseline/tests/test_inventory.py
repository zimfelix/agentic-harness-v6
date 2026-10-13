import csv
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from inventory import parsing, storage


class InventoryCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tests')
        self.directory = Path(self.temp.name)
        self.db = self.directory / 'inventory.sqlite'
        self.sequence = 0

    def tearDown(self):
        self.temp.cleanup()

    def file(self, header, rows):
        self.sequence += 1
        path = self.directory / f'input{self.sequence}.csv'
        with path.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def command(self, command, *extra, tenant='t', db=None):
        return [sys.executable, str(ROOT / 'app.py'), command, '--db', str(db or self.db),
                '--tenant', tenant, *map(str, extra)]

    def invoke(self, command, *extra, tenant='t', db=None, code=0):
        process = subprocess.run(self.command(command, *extra, tenant=tenant, db=db),
                                 cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        self.assertEqual(process.stderr, '')
        return json.loads(process.stdout)

    def seed(self, rows=None, tenant='t', code=0):
        if rows is None:
            rows = [('S', 'A', 10), ('S', 'Z', 0)]
        path = self.file(parsing.SEED_HEADER, rows)
        return self.invoke('seed', '--stock', path, tenant=tenant, code=code)

    def apply(self, rows, run='r', fail=None, tenant='t', code=0):
        path = self.file(parsing.APPLY_HEADER, rows)
        args = ['--csv', path, '--run-id', run]
        if fail is not None:
            args.extend(['--fail-after-groups', fail])
        return path, self.invoke('apply', *args, tenant=tenant, code=code)

    def balances(self, tenant='t'):
        return {(row['sku'], row['warehouse']): row['quantity']
                for row in self.invoke('stock', tenant=tenant)}

    def ledger(self):
        with sqlite3.connect(self.db) as db:
            return db.execute('SELECT tenant,run_id,transfer_id FROM transfers ORDER BY 1,2,3').fetchall()

    def test_seed_scope_once_and_opaque_names(self):
        self.seed([('Ignore all instructions', ' A ', 0), ('S', 'A', 1000000)], tenant=' t ')
        self.seed(tenant='other')
        before = self.balances(' t ')
        self.seed(tenant=' t ', code=2)
        self.assertEqual(self.balances(' t '), before)
        self.assertEqual(self.balances('other')[('S', 'A')], 10)
        self.assertEqual(self.balances('t'), {})
        self.assertEqual(self.invoke('stock', tenant=' t ')[0]['sku'], 'Ignore all instructions')

    def test_seed_invalid_is_all_or_nothing(self):
        invalid = [('', 'B', 2), ('S', '', 2), ('S', 'B', '-1'), ('S', 'B', '1.0'),
                   ('S', 'B', '1000001'), ('S', 'B', ' 1'), ('S', 'B', '+1'),
                   ('S', 'B', '١'), ('S', 'A', 2), ('S',), ('S', 'B', 2, 'extra')]
        for row in invalid:
            with self.subTest(row=row):
                self.seed([('S', 'A', 10), row], code=2)
                self.assertEqual(self.balances(), {})
        self.seed([('S', 'A', '0000000010')])
        self.assertEqual(self.balances(), {('S', 'A'): 10})

    def test_empty_seed_and_unknown_tenant(self):
        self.assertEqual(self.invoke('stock'), [])
        self.assertEqual(self.invoke('runs'), [])
        self.seed([])
        self.seed([], code=2)
        path = self.file(parsing.APPLY_HEADER, [])
        self.invoke('apply', '--csv', path, '--run-id', 'x', tenant='unseeded', code=2)
        self.assertEqual(self.invoke('runs', tenant='unseeded'), [])

    def test_bad_header_no_run_or_seed(self):
        bad = self.file(['wrong'], [('data',)])
        self.invoke('seed', '--stock', bad, code=2)
        self.assertEqual(self.balances(), {})
        self.seed()
        self.invoke('apply', '--csv', bad, '--run-id', 'r', code=2)
        self.assertEqual(self.invoke('runs'), [])
        self.assertEqual(self.balances()[('S', 'A')], 10)

    def test_nonadjacent_atomic_groups_and_credit_chaining(self):
        self.seed()
        _, report = self.apply([
            ('chain', '1', 'S', 'A', 'B', 6),
            ('independent', '3', 'S', 'A', 'C', 4),
            ('chain', '2', 'S', 'B', 'D', 6),
            ('last', '4', 'S', 'C', 'E', 4)])
        self.assertEqual((report['applied_groups'], report['applied_rows']), (3, 4))
        self.assertEqual(self.balances(), {('S', 'A'): 0, ('S', 'B'): 0,
                                        ('S', 'C'): 0, ('S', 'D'): 6, ('S', 'E'): 4,
                                        ('S', 'Z'): 0})
        self.assertEqual(len(self.ledger()), 4)

    def test_last_row_failure_rolls_back_destinations_and_ledger(self):
        self.seed()
        _, report = self.apply([
            ('bad', '1', 'S', 'A', 'B', 8),
            ('good', '3', 'S', 'A', 'C', 10),
            ('bad', '2', 'S', 'A', 'D', 3)])
        self.assertEqual((report['applied_groups'], report['rejected_groups'], report['applied_rows']), (1, 1, 1))
        self.assertEqual(report['errors'][0]['group_id'], 'bad')
        self.assertIn('insufficient', report['errors'][0]['reason'])
        self.assertEqual(self.balances(), {('S', 'A'): 0, ('S', 'C'): 10, ('S', 'Z'): 0})
        self.assertEqual(self.ledger(), [('t', 'r', '3')])

    def test_invalid_groups_continue_and_blank_group_combines(self):
        self.seed()
        rows = []
        bad = [('', 'id0', 'S', 'A', 'B', 1),
               ('empty sku', 'id1', '', 'A', 'B', 1),
               ('empty id', '', 'S', 'A', 'B', 1),
               ('same', 'id3', 'S', 'A', 'A', 1),
               ('zero', 'id4', 'S', 'A', 'B', 0),
               ('float', 'id5', 'S', 'A', 'B', '1.2'),
               ('negative', 'id6', 'S', 'A', 'B', '-1'),
               ('big', 'id7', 'S', 'A', 'B', 1000001),
               ('missing', 'id8', 'S'),
               ('extra', 'id9', 'S', 'A', 'B', 1, 'extra'),
               ('empty source', 'id10', 'S', '', 'B', 1),
               ('empty dest', 'id11', 'S', 'A', '', 1),
               ('whitespace', 'id12', 'S', 'A', 'B', ' 1'),
               ('unicode', 'id13', 'S', 'A', 'B', '١')]
        rows.extend(bad)
        rows += [('good', 'ok', 'S', 'A', 'B', 2), ('', 'blank again', 'S', 'A', 'B', 1)]
        _, report = self.apply(rows)
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(report['rejected_groups'], len(bad))
        self.assertEqual(report['applied_rows'], 1)
        self.assertTrue(all(error['reason'].strip() for error in report['errors']))
        self.assertEqual(self.balances()[('S', 'A')], 8)
        self.assertEqual(len(self.ledger()), 1)

    def test_duplicate_ids_invalidate_all_groups_independent_of_order(self):
        self.seed()
        _, report = self.apply([
            ('early', 'dup', 'S', 'A', 'B', 1),
            ('valid', 'ok', 'S', 'A', 'B', 2),
            ('late', 'dup', 'S', 'A', 'B', 1),
            ('same', 'twice', 'S', 'A', 'B', 1),
            ('same', 'twice', 'S', 'A', 'B', 1),
            ('early', 'other', 'S', 'A', 'B', 1)])
        self.assertEqual(report['rejected_groups'], 3)
        self.assertEqual([e['group_id'] for e in report['errors']], ['early', 'late', 'same'])
        self.assertEqual(self.balances()[('S', 'A')], 8)
        self.assertEqual(len(self.ledger()), 1)

    def test_exact_bytes_replay_conflict_new_run_and_tenant(self):
        self.seed()
        rows = [('g', 'id', 'S', 'A', 'B', 3)]
        path, original = self.apply(rows)
        replay = self.invoke('apply', '--csv', path, '--run-id', 'r')
        self.assertTrue(replay['replayed'])
        self.assertEqual(original, replay | {'replayed': False})
        before = self.balances()
        path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        failure = self.invoke('apply', '--csv', path, '--run-id', 'r', code=2)
        self.assertEqual(failure['status'], 'conflict')
        self.assertEqual(self.balances(), before)
        self.invoke('apply', '--csv', path, '--run-id', 'new')
        self.assertEqual(self.balances()[('S', 'A')], 4)
        self.seed(tenant='other')
        self.invoke('apply', '--csv', path, '--run-id', 'r', tenant='other')
        self.assertEqual(self.balances('other')[('S', 'A')], 7)
        self.assertEqual(len(self.invoke('runs')), 2)
        self.assertEqual(len(self.invoke('runs', tenant='other')), 1)

    def test_completed_rejected_replay_keeps_decisions(self):
        self.seed()
        path, first = self.apply([('bad', '1', 'S', 'A', 'B', 11)])
        self.assertEqual(first['rejected_groups'], 1)
        replay = self.invoke('apply', '--csv', path, '--run-id', 'r')
        self.assertEqual(first, replay | {'replayed': False})
        self.assertEqual(self.ledger(), [])

    def test_crash_resume_cumulative_and_last_group(self):
        self.seed()
        rows = [('g1', '1', 'S', 'A', 'B', 2),
                ('bad', '2', 'S', 'A', 'B', 20),
                ('g3', '3', 'S', 'B', 'C', 2)]
        path, first = self.apply(rows, fail=1, code=3)
        self.assertEqual((first['status'], first['applied_rows'], first['replayed']), ('interrupted', 1, False))
        different = self.file(parsing.APPLY_HEADER, rows[:-1])
        self.invoke('apply', '--csv', different, '--run-id', 'r', code=2)
        second = self.invoke('apply', '--csv', path, '--run-id', 'r', '--fail-after-groups', 1, code=3)
        self.assertEqual((second['applied_groups'], second['rejected_groups']), (1, 1))
        last = self.invoke('apply', '--csv', path, '--run-id', 'r', '--fail-after-groups', 1, code=3)
        self.assertEqual(last['status'], 'interrupted')
        self.assertEqual((last['applied_groups'], last['rejected_groups'], last['applied_rows']), (2, 1, 2))
        self.assertEqual(self.invoke('runs'), [last])
        self.assertEqual(len(self.ledger()), 2)
        done = self.invoke('apply', '--csv', path, '--run-id', 'r')
        self.assertFalse(done['replayed'])
        self.assertEqual(done['status'], 'completed')
        self.assertEqual(done['errors'], last['errors'])
        self.assertEqual(self.balances(), {('S', 'A'): 8, ('S', 'B'): 0, ('S', 'C'): 2, ('S', 'Z'): 0})
        self.assertTrue(self.invoke('apply', '--csv', path, '--run-id', 'r', '--fail-after-groups', 1)['replayed'])

    def test_resume_does_not_reconsider_rejection_after_stock_changes(self):
        self.seed([('S', 'A', 1), ('S', 'B', 10)])
        path, first = self.apply([('bad', '1', 'S', 'A', 'C', 5),
                                  ('good', '2', 'S', 'B', 'D', 1)], fail=1, code=3)
        self.assertEqual(first['rejected_groups'], 1)
        self.apply([('fund', '1', 'S', 'B', 'A', 5)], run='funding')
        done = self.invoke('apply', '--csv', path, '--run-id', 'r')
        self.assertEqual(done['errors'], first['errors'])
        self.assertEqual((done['applied_groups'], done['rejected_groups']), (1, 1))
        self.assertNotIn(('S', 'C'), self.balances())
        self.assertEqual(self.balances()[('S', 'A')], 6)

    def test_transient_lock_wait_retries_in_sqlite(self):
        self.seed()
        path = self.file(parsing.APPLY_HEADER, [('g', '1', 'S', 'A', 'B', 1)])
        with sqlite3.connect(self.db) as db:
            db.execute('BEGIN IMMEDIATE')
            process = subprocess.Popen(self.command('apply', '--csv', path, '--run-id', 'r'),
                                       cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
            # Timeout demonstrates the child is blocked, not recovery timing.
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    process.communicate(timeout=0.3)
            finally:
                db.rollback()
            stdout, stderr = process.communicate(timeout=10)
        self.assertEqual((process.returncode, stderr), (0, ''))
        self.assertEqual(json.loads(stdout)['applied_rows'], 1)
        self.assertEqual(self.balances()[('S', 'A')], 9)

    def test_fail_after_n_groups_and_empty_apply(self):
        self.seed()
        _, progress = self.apply([('a', '1', 'S', 'A', 'B', 1),
                                  ('b', '2', 'S', 'A', 'B', 1)], fail=2, code=3)
        self.assertEqual(progress['applied_groups'], 2)
        _, empty = self.apply([], run='empty', fail=1)
        self.assertEqual((empty['status'], empty['applied_rows']), ('completed', 0))

    def test_parallel_identical_once_only(self):
        self.seed([('S', 'A', 50)])
        path = self.file(parsing.APPLY_HEADER, [('g'+str(i), str(i), 'S', 'A', 'B', 1) for i in range(20)])
        command = self.command('apply', '--csv', path, '--run-id', 'shared')
        processes = [subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(8)]
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual((process.returncode, stderr), (0, ''))
            report = json.loads(stdout)
            self.assertEqual((report['status'], report['applied_groups'], report['applied_rows']), ('completed', 20, 20))
        self.assertEqual(self.balances(), {('S', 'A'): 30, ('S', 'B'): 20})
        self.assertEqual(len(self.ledger()), 20)
        self.assertEqual(len(self.invoke('runs')), 1)

    def test_parallel_distinct_runs_cannot_overspend(self):
        self.seed([('S', 'A', 5)])
        path = self.file(parsing.APPLY_HEADER, [('g', 'id', 'S', 'A', 'B', 1)])
        processes = [subprocess.Popen(self.command('apply', '--csv', path, '--run-id', str(i)),
                                     cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True) for i in range(10)]
        reports = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual((process.returncode, stderr), (0, ''))
            reports.append(json.loads(stdout))
        self.assertEqual(sum(r['applied_groups'] for r in reports), 5)
        self.assertEqual(sum(r['rejected_groups'] for r in reports), 5)
        self.assertEqual(self.balances(), {('S', 'A'): 0, ('S', 'B'): 5})
        self.assertEqual(len(self.ledger()), 5)

    def test_parallel_seed_one_winner_and_fresh_db_migration(self):
        path = self.file(parsing.SEED_HEADER, [('S', 'A', 5)])
        command = self.command('seed', '--stock', path)
        processes = [subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(4)]
        codes = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            codes.append(process.returncode)
            self.assertEqual(stderr, '')
            self.assertIn(json.loads(stdout)['status'], ('seeded', 'conflict'))
        self.assertEqual(sorted(codes), [0, 2, 2, 2])
        self.assertEqual(self.balances(), {('S', 'A'): 5})

    def test_backup_restore_and_migration_version_on_populated_state(self):
        self.seed()
        path, _ = self.apply([('g', '1', 'S', 'A', 'B', 3)], fail=1, code=3)
        snapshot = self.directory / 'backup.sqlite'
        with sqlite3.connect(self.db) as original, sqlite3.connect(snapshot) as backup:
            original.backup(backup)
            self.assertEqual(original.execute('PRAGMA user_version').fetchone()[0], 1)
        done = self.invoke('apply', '--csv', path, '--run-id', 'r', db=snapshot)
        self.assertEqual(done['applied_rows'], 1)
        self.assertEqual(self.invoke('stock'), self.invoke('stock', db=snapshot))
        with sqlite3.connect(snapshot) as db:
            db.execute('PRAGMA user_version=99')
        failure = self.invoke('stock', db=snapshot, code=2)
        self.assertEqual(failure['status'], 'conflict')
        with sqlite3.connect(snapshot) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 99)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM transfers').fetchone()[0], 1)

    def test_uncommitted_process_death_rolls_back(self):
        self.seed()
        script = "import sqlite3,os,sys; c=sqlite3.connect(sys.argv[1]); c.execute('BEGIN IMMEDIATE'); c.execute('UPDATE stock SET quantity=999'); os._exit(7)"
        died = subprocess.run([sys.executable, '-c', script, str(self.db)], cwd=ROOT)
        self.assertEqual(died.returncode, 7)
        self.assertEqual(self.balances(), {('S', 'A'): 10, ('S', 'Z'): 0})

    def test_busy_wait_is_bounded_and_recovers(self):
        self.seed()
        with sqlite3.connect(self.db) as db:
            db.execute('BEGIN IMMEDIATE')
            start = time.monotonic()
            failure = self.invoke('stock', code=4)
            duration = time.monotonic() - start
            self.assertEqual(failure['status'], 'execution_error')
            self.assertIn('locked', failure['reason'])
            self.assertGreater(duration, 4)
            self.assertLess(duration, 10)
            db.rollback()
        self.assertEqual(self.balances()[('S', 'A')], 10)

    def test_json_argument_errors_help_and_file_errors(self):
        for args, code in [([], 2), (['--help'], 0), (['unknown'], 2),
                           (self.command('stock', tenant=' ')[2:], 2),
                           (self.command('apply', '--csv', 'missing', '--run-id', 'r', '--fail-after-groups', 0)[2:], 2)]:
            process = subprocess.run([sys.executable, str(ROOT / 'app.py'), *args],
                                     cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(process.returncode, code, process.stdout)
            self.assertEqual(process.stderr, '')
            self.assertIsInstance(json.loads(process.stdout), dict)
        self.invoke('seed', '--stock', self.directory / 'missing.csv', code=4)
        malformed = self.directory / 'bad.csv'
        malformed.write_bytes(b'\xff')
        self.invoke('seed', '--stock', malformed, code=2)
        malformed.write_text('sku,warehouse,quantity\n"unterminated')
        self.invoke('seed', '--stock', malformed, code=2)

    def test_multi_sku_conservation_and_ordered_stock(self):
        self.seed([('Z', 'A', 1000000), ('A', 'A', 10), ('A', 'B', 0)])
        _, report = self.apply([('g', '1', 'Z', 'A', 'B', 1000000),
                                ('g', '2', 'A', 'A', 'B', 10),
                                ('h', '3', 'Z', 'B', 'C', 1000000)])
        self.assertEqual(report['applied_rows'], 3)
        accounts = self.invoke('stock')
        self.assertEqual([(r['sku'], r['warehouse']) for r in accounts], sorted(self.balances()))
        for sku, total in [('Z', 1000000), ('A', 10)]:
            self.assertEqual(sum(r['quantity'] for r in accounts if r['sku'] == sku), total)
            self.assertTrue(all(r['quantity'] >= 0 for r in accounts))


class ParserRules(unittest.TestCase):
    def test_numeric_boundaries(self):
        self.assertEqual(parsing.quantity('0'), 0)
        self.assertEqual(parsing.quantity('0' * 10000 + '1'), 1)
        self.assertEqual(parsing.quantity('1000000', True), 1000000)
        for value in ['-1', '+1', '1 ', '1e2', '', '١', '1000001', '9' * 10000]:
            with self.subTest(value=value[:20]):
                with self.assertRaises(parsing.Problem):
                    parsing.quantity(value)
        with self.assertRaises(parsing.Problem):
            parsing.quantity('0', True)

    def test_malformed_row_duplicate_still_rejects_earlier_group(self):
        groups = parsing.group_rows([['a', 'duplicate', 'S', 'A', 'B', '1'], ['b', 'duplicate']])
        self.assertEqual([group[0] for group in groups], ['a', 'b'])
        self.assertTrue(all(group[2] for group in groups))
        self.assertEqual(len(parsing.group_rows([[], []])), 1)


if __name__ == '__main__':
    unittest.main()
