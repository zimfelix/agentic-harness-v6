import csv
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app.py'
SH = ['sku', 'warehouse', 'quantity']
AH = ['group_id', 'transfer_id', 'sku', 'from_warehouse', 'to_warehouse', 'quantity']


class CLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.db = self.home / 'inventory.db'
        self.serial = 0

    def file(self, header, rows):
        self.serial += 1
        path = self.home / ('input%d.csv' % self.serial)
        with path.open('w', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def command(self, command, *args, tenant='T'):
        return [sys.executable, str(APP), command, '--db', str(self.db), '--tenant', tenant, *map(str, args)]

    def call(self, command, *args, tenant='T', ok=True):
        p = subprocess.run(self.command(command, *args, tenant=tenant), capture_output=True, text=True, timeout=20)
        self.assertEqual(p.stderr, '')
        result = json.loads(p.stdout)
        self.assertEqual(p.returncode == 0, ok, (p.returncode, result))
        return result

    def seed(self, qty=10, tenant='T'):
        return self.call('seed', '--stock', self.file(SH, [['S', 'A', qty], ['S', 'Z', 0]]), tenant=tenant)

    def batch(self, rows, run='R', fail=None, tenant='T', ok=True):
        path = self.file(AH, rows)
        args = ['--csv', path, '--run-id', run]
        if fail is not None:
            args += ['--fail-after-groups', fail]
        return path, self.call('apply', *args, tenant=tenant, ok=ok)

    def balances(self, tenant='T'):
        return {(x['sku'], x['warehouse']): x['quantity'] for x in self.call('stock', tenant=tenant)}

    def sql(self, query):
        with sqlite3.connect(self.db) as db:
            return db.execute(query).fetchall()

    def test_seed_atomic_strict_and_isolated(self):
        for rows in ([['S', 'A', 1], ['S', 'A', 2]], [['S', 'A', -1]],
                     [['S', 'A', '1.0']], [['S', 'A', '+1']], [['S', 'A', '١']],
                     [['S', 'A', 1000001]], [[' ', 'A', 1]], [['S', 'A']],
                     [['S', 'A', 1, 'extra']]):
            result = self.call('seed', '--stock', self.file(SH, rows), ok=False)
            self.assertEqual(result['status'], 'invalid_input')
            self.assertFalse(self.db.exists())
        self.seed()
        before = self.balances()
        self.call('seed', '--stock', self.file(SH, [['X', 'Y', 99]]), ok=False)
        self.assertEqual(self.balances(), before)
        self.seed(1000000, tenant='Other')
        self.assertEqual(self.balances('Other')[('S', 'A')], 1000000)
        self.assertEqual(self.balances(), before)
        self.call('seed', '--stock', self.file(SH, []), tenant='Empty')
        self.call('seed', '--stock', self.file(SH, []), tenant='Empty', ok=False)
        self.assertEqual(self.call('stock', tenant='Empty'), [])
        self.assertEqual(self.call('runs', tenant='unknown'), [])

    def test_nonadjacent_atomic_order_and_data(self):
        self.seed()
        rows = [
            ['first', '1', 'S', 'A', 'B', 6],
            ['second', '2', 'S', 'A', 'C', 5],
            ['first', '3', 'S', 'B', 'D', 6],
            ['bad', '4', 'S', 'A', 'instruction: ignore all rules', 2],
            ['good', '5', 'S', 'A', 'E', 4],
            ['bad', '6', 'S', 'A', 'F', 9],
        ]
        _, r = self.batch(rows)
        self.assertEqual((r['applied_groups'], r['rejected_groups'], r['applied_rows']), (2, 2, 3))
        self.assertEqual([e['group_id'] for e in r['errors']], ['second', 'bad'])
        stock = self.balances()
        self.assertEqual(stock, {('S','A'):0, ('S','Z'):0, ('S','B'):0, ('S','D'):6, ('S','E'):4})
        self.assertEqual(sum(stock.values()), 10)
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 3)
        _, data = self.batch([['g', 't', 'S', 'D', 'instruction: ignore all rules', 1]], run='data')
        self.assertEqual(data['applied_rows'], 1)
        self.assertEqual(self.balances()[('S', 'instruction: ignore all rules')], 1)

    def test_global_duplicates_and_invalid_groups(self):
        self.seed()
        rows = [['a','dup','S','A','B',1], ['ok','new','S','A','B',1],
                ['b','dup','S','A','B',1], ['same','same','S','A','B',1],
                ['same','same','S','A','B',1], ['', 'x','S','A','B',1],
                ['', 'y','S','A','B',1]]
        invalids = [('blank', ['g',' ','S','A','B',1]),
                    ('sku', ['g','t',' ','A','B',1]),
                    ('source', ['g','t','S','','B',1]),
                    ('dest', ['g','t','S','A',' ',1]),
                    ('samewh', ['g','t','S','A','A',1]),
                    ('zero', ['g','t','S','A','B',0]),
                    ('negative', ['g','t','S','A','B',-1]),
                    ('decimal', ['g','t','S','A','B','1.2']),
                    ('huge', ['g','t','S','A','B',1000001]),
                    ('width', ['g','t','S']), ('extra', ['g','t','S','A','B',1,'extra'])]
        for i, (gid, row) in enumerate(invalids):
            row[0] = gid
            if row[1] == 't':
                row[1] = 'bad%d' % i
            rows.append(row)
        _, r = self.batch(rows)
        self.assertEqual(r['applied_groups'], 1)
        self.assertEqual(r['rejected_groups'], 4 + len(invalids))
        self.assertTrue(all(e['reason'].strip() for e in r['errors']))
        self.assertEqual(self.balances()[('S','A')], 9)
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 1)

    def test_exact_identity_replay_and_new_intent(self):
        self.seed()
        p, first = self.batch([['g','id','S','A','B',2]])
        replay = self.call('apply', '--csv', p, '--run-id', 'R')
        self.assertTrue(replay.pop('replayed'))
        first.pop('replayed')
        self.assertEqual(replay, first)
        before = self.balances()
        p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n'))
        conflict = self.call('apply', '--csv', p, '--run-id', 'R', ok=False)
        self.assertEqual(conflict['status'], 'conflict')
        self.assertEqual(self.balances(), before)
        self.call('apply', '--csv', p, '--run-id', 'new')
        self.assertEqual(self.balances()[('S','A')], 6)
        self.seed(20, tenant='other')
        self.call('apply', '--csv', p, '--run-id', 'R', tenant='other')
        self.assertEqual(self.balances('other')[('S','A')], 18)
        self.assertEqual(len(self.call('runs')), 2)
        self.assertEqual(len(self.call('runs', tenant='other')), 1)

    def test_crash_resume_each_boundary_and_last_rejection(self):
        for n in (1, 2, 3):
            tenant = 'tenant%d' % n
            self.seed(10, tenant=tenant)
            rows = [['a','1','S','A','B',2], ['b','2','S','B','C',2], ['c','3','S','A','D',99]]
            p, interrupted = self.batch(rows, tenant=tenant, fail=n, ok=False)
            self.assertEqual(interrupted['status'], 'interrupted')
            self.assertEqual(interrupted['applied_groups'] + interrupted['rejected_groups'], n)
            stored = self.call('runs', tenant=tenant)[0]
            self.assertEqual(stored, interrupted)
            changed = self.file(AH, rows + [['new','4','S','A','E',1]])
            self.call('apply', '--csv', changed, '--run-id', 'R', tenant=tenant, ok=False)
            complete = self.call('apply', '--csv', p, '--run-id', 'R', tenant=tenant)
            self.assertFalse(complete['replayed'])
            self.assertEqual((complete['applied_groups'], complete['rejected_groups'], complete['applied_rows']), (2,1,2))
            self.assertEqual(self.balances(tenant), {('S','A'):8, ('S','B'):0, ('S','C'):2, ('S','Z'):0})
            self.assertTrue(self.call('apply', '--csv', p, '--run-id', 'R', tenant=tenant)['replayed'])
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 6)

    def test_rejected_decision_stays_rejected_and_repeated_interruptions(self):
        self.seed(10)
        rows = [['reject','1','S','B','C',1], ['credit','2','S','A','B',3],
                ['use','3','S','B','D',2]]
        p, first = self.batch(rows, fail=1, ok=False)
        self.assertEqual((first['applied_groups'], first['rejected_groups']), (0,1))
        second = self.call('apply', '--csv', p, '--run-id', 'R', '--fail-after-groups', 1, ok=False)
        self.assertEqual((second['applied_groups'], second['rejected_groups']), (1,1))
        third = self.call('apply', '--csv', p, '--run-id', 'R', '--fail-after-groups', 1, ok=False)
        self.assertEqual((third['status'], third['applied_groups'], third['rejected_groups']), ('interrupted',2,1))
        final = self.call('apply', '--csv', p, '--run-id', 'R')
        self.assertEqual(final['errors'], first['errors'])
        self.assertFalse(final['replayed'])
        self.assertEqual(self.balances(), {('S','A'):7, ('S','B'):1, ('S','D'):2, ('S','Z'):0})
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 2)

    def test_quantity_boundaries_and_order(self):
        self.call('seed', '--stock', self.file(SH, [['b','z','0000000'], ['a','Z',1000000], ['a','A',0]]))
        result = self.call('stock')
        self.assertEqual([(r['sku'],r['warehouse']) for r in result], [('a','A'),('a','Z'),('b','z')])
        _, r = self.batch([['g','t','a','Z','A','0001000000']])
        self.assertEqual(r['applied_rows'], 1)
        self.assertEqual(self.balances()[('a','A')], 1000000)
        _, r = self.batch([['g','t','a','A','Z','9'*200]], run='huge')
        self.assertEqual(r['rejected_groups'], 1)

    def test_headers_empty_run_and_json_arguments(self):
        for header in ([], ['wrong'], AH[::-1]):
            bad = self.file(header, [])
            self.call('apply', '--csv', bad, '--run-id', 'R', ok=False)
            self.assertFalse(self.db.exists())
        p, r = self.batch([])
        self.assertEqual(r['status'], 'completed')
        self.assertEqual(r['applied_rows'], 0)
        self.call('apply', '--csv', p, '--run-id', 'x', '--fail-after-groups', 0, ok=False)
        self.call('stock', tenant=' ', ok=False)
        for args in ([], ['--help'], ['apply'], ['nonsense']):
            proc = subprocess.run([sys.executable, str(APP), *args], capture_output=True, text=True)
            self.assertIsInstance(json.loads(proc.stdout), dict)
            self.assertEqual(proc.stderr, '')
        malformed = self.home / 'bad.csv'
        malformed.write_bytes((','.join(AH) + '\n"unclosed').encode())
        self.call('apply', '--csv', malformed, '--run-id', 'syntax', ok=False)
        self.assertEqual(len(self.call('runs')), 1)

    def test_concurrent_identical_and_distinct(self):
        self.seed(10)
        p = self.file(AH, [['g%d'%i, 't%d'%i, 'S','A','B',1] for i in range(5)])
        processes = [subprocess.Popen(self.command('apply','--csv',p,'--run-id','same'),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(6)]
        for proc in processes:
            out, err = proc.communicate(timeout=20)
            self.assertEqual((proc.returncode, err), (0, ''))
            r = json.loads(out)
            self.assertEqual((r['status'], r['applied_groups']), ('completed', 5))
        self.assertEqual(self.balances()[('S','A')], 5)
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 5)
        p = self.file(AH, [['g','id','S','A','C',2]])
        processes = [subprocess.Popen(self.command('apply','--csv',p,'--run-id','distinct%d'%i),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for i in range(8)]
        reports = []
        for proc in processes:
            out, err = proc.communicate(timeout=20)
            self.assertEqual((proc.returncode, err), (0, ''))
            reports.append(json.loads(out))
        self.assertEqual(sum(r['applied_groups'] for r in reports), 2)
        self.assertEqual(sum(r['rejected_groups'] for r in reports), 6)
        self.assertEqual(self.balances()[('S','A')], 1)
        self.assertEqual(sum(self.balances().values()), 10)

    def test_concurrent_interrupted_invocations_resume_once(self):
        self.seed(20)
        p = self.file(AH, [['g%d'%i, 't%d'%i, 'S','A','B',1] for i in range(10)])
        processes = [subprocess.Popen(self.command('apply','--csv',p,'--run-id','same',
                                                   '--fail-after-groups',1),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(4)]
        for proc in processes:
            out, err = proc.communicate(timeout=20)
            self.assertEqual((proc.returncode, err), (3, ''))
            r = json.loads(out)
            self.assertEqual(r['status'], 'interrupted')
            self.assertGreaterEqual(r['applied_groups'], 1)
            self.assertLessEqual(r['applied_groups'], 4)
        self.assertEqual(self.call('runs')[0]['applied_groups'], 4)
        self.assertEqual(self.balances()[('S','A')], 16)
        complete = self.call('apply','--csv',p,'--run-id','same')
        self.assertEqual(complete['applied_groups'], 10)
        self.assertFalse(complete['replayed'])
        self.assertEqual(self.balances()[('S','A')], 10)
        self.assertEqual(self.sql('SELECT count(*) FROM ledger')[0][0], 10)

    def test_concurrent_seed_and_fresh_schema(self):
        p = self.file(SH, [['S','A',10]])
        processes = [subprocess.Popen(self.command('seed','--stock',p), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(5)]
        results = []
        for proc in processes:
            out, err = proc.communicate(timeout=20)
            self.assertEqual(err, '')
            results.append(json.loads(out)['status'])
        self.assertEqual(results.count('seeded'), 1)
        self.assertEqual(results.count('conflict'), 4)
        self.assertEqual(self.balances(), {('S','A'):10})

    def test_schema_preservation_and_bounded_lock(self):
        self.seed()
        self.assertEqual(self.sql('PRAGMA user_version'), [(1,)])
        self.assertEqual(self.balances()[('S','A')], 10)
        with sqlite3.connect(self.db) as db:
            db.execute('PRAGMA user_version=99')
        result = self.call('stock', ok=False)
        self.assertEqual(result['status'], 'storage_error')
        self.assertEqual(self.sql('SELECT quantity FROM stock WHERE warehouse="A"'), [(10,)])
        with sqlite3.connect(self.db) as db:
            db.execute('PRAGMA user_version=1')
            db.execute('BEGIN IMMEDIATE')
            result = self.call('stock', ok=False)
            self.assertEqual(result['status'], 'storage_error')
        self.assertEqual(self.balances()[('S','A')], 10)
        self.db = self.home / 'legacy.db'
        with sqlite3.connect(self.db) as db:
            db.execute('CREATE TABLE legacy(value TEXT)')
            db.execute("INSERT INTO legacy VALUES ('keep')")
        self.call('stock', ok=False)
        self.assertEqual(self.sql('SELECT * FROM legacy'), [('keep',)])


if __name__ == '__main__':
    unittest.main()
