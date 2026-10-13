import concurrent.futures
from contextlib import closing
import http.client
import json
from pathlib import Path
import select
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.db = Path(self.temp.name) / 'ledger.sqlite'
        self.process = None
        self.start()

    def start(self):
        self.process = subprocess.Popen([sys.executable, str(ROOT / 'app.py'), 'serve', '--db', str(self.db), '--port', '0'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if not select.select([self.process.stdout], [], [], 10)[0]:
            self.fail('Server readiness timed out')
        line = self.process.stdout.readline()
        self.assertTrue(line, 'Server exited before readiness')
        ready = json.loads(line)
        self.assertEqual(set(ready), {'port'})
        self.port = ready['port']
        self.assertGreater(self.port, 0)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=10)
            self.process.stdout.close()
            self.process.stderr.close()
            self.process = None

    def tearDown(self):
        self.stop()
        self.temp.cleanup()

    def request(self, method, path, body=None, token='owner-a', raw=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=15)
        headers = {'Content-Type': 'application/json'}
        if token is not None:
            headers['Authorization'] = 'Bearer ' + token
        data = raw if raw is not None else (json.dumps(body) if body is not None else None)
        connection.request(method, path, data, headers)
        response = connection.getresponse()
        self.assertEqual(response.getheader('Content-Type'), 'application/json')
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def ok(self, method, path, body=None, expected=200, token='owner-a', raw=None):
        code, result = self.request(method, path, body, token, raw)
        self.assertEqual(code, expected, result)
        return result

    def create(self, token='owner-a', amount=101, currency='EUR'):
        return self.ok('POST', '/deals', {'title': 'Synthetic sale', 'amount_cents': amount, 'currency': currency}, 201, token)

    def won(self, token='owner-a', amount=101, currency='EUR'):
        deal = self.create(token, amount, currency)
        for status in ('qualified', 'won'):
            deal = self.ok('PATCH', '/deals/' + str(deal['id']), {'version': deal['version'], 'status': status}, token=token)
        return deal

    def invoice(self, deal, key='request-1', rate=5000, token='owner-a', expected=201):
        return self.ok('POST', '/invoices', {'deal_id': deal['id'], 'request_id': key, 'tax_bps': rate}, expected, token)

    def test_roles_tenants_and_related_lookup(self):
        a = self.won('editor-a')
        inv = self.invoice(a)
        b = self.won('editor-b')
        inv_b = self.invoice(b, token='owner-b')
        for token in ('owner-a', 'editor-a', 'viewer-a'):
            self.assertEqual(self.ok('GET', '/deals', token=token), [a])
            self.assertEqual(self.ok('GET', '/invoices', token=token), [inv])
            self.assertEqual(self.ok('GET', '/deals/' + a['id'], token=token), a)
            self.assertEqual(self.ok('GET', '/invoices/' + inv['id'], token=token), inv)
            self.assertEqual(len(self.ok('GET', '/audit', token=token)), 4)
        for token in ('owner-b', 'editor-b', 'viewer-b'):
            self.assertEqual(self.ok('GET', '/deals', token=token), [b])
            self.assertEqual(self.ok('GET', '/invoices', token=token), [inv_b])
            for kind, identifier in (('deals', a['id']), ('invoices', inv['id'])):
                self.ok('GET', '/' + kind + '/' + identifier, expected=404, token=token)
        for identifier in (a['id'], 'missing'):
            self.ok('PATCH', '/deals/' + identifier, {'version': 3, 'status': 'lost'}, 404, 'editor-b')
            self.ok('POST', '/invoices', {'deal_id': identifier, 'request_id': 'other', 'tax_bps': 0}, 404, 'owner-b')
        for identifier in (inv['id'], 'missing'):
            self.ok('POST', '/invoices/' + identifier + '/void', {'reason': 'Synthetic'}, 404, 'owner-b')
        writes = [('POST', '/deals', {'title': 'X', 'amount_cents': 0, 'currency': 'USD'}),
                  ('PATCH', '/deals/' + a['id'], {'version': 3, 'status': 'lost'}),
                  ('POST', '/invoices', {'deal_id': a['id'], 'request_id': 'x', 'tax_bps': 0}),
                  ('POST', '/invoices/' + inv['id'] + '/void', {'reason': 'X'})]
        for method, path, body in writes:
            self.ok(method, path, body, 403, 'viewer-a')
        for method, path, body in writes[2:]:
            self.ok(method, path, body, 403, 'editor-a')
        for token in (None, 'unknown', 'owner-c'):
            for method, path, body in writes + [('GET', '/deals', None), ('GET', '/invoices', None), ('GET', '/audit', None), ('GET', '/deals/' + a['id'], None), ('GET', '/invoices/' + inv['id'], None)]:
                self.ok(method, path, body, 401, token)
        self.assertEqual(len(self.ok('GET', '/audit')), 4)

    def test_strict_validation_and_no_mutation(self):
        valid = {'title': 'X', 'amount_cents': 1, 'currency': 'EUR'}
        invalid = [None, [], 'string', 42, {}, {**valid, 'tenant': 'b'}, {**valid, 'extra': 1}]
        for key in valid:
            invalid.append({k: v for k, v in valid.items() if k != key})
        for title in ('', '  ', None, False, 3, []):
            invalid.append({**valid, 'title': title})
        for amount in (-1, 100000001, True, False, 1.0, '1', None, []):
            invalid.append({**valid, 'amount_cents': amount})
        for currency in ('eur', 'GBP', None, 1, [], {}):
            invalid.append({**valid, 'currency': currency})
        for body in invalid:
            self.ok('POST', '/deals', body, 400)
        for raw in ('{', '', 'null', '{"title":"X","title":"Y","amount_cents":1,"currency":"EUR"}', '{"title":"X","amount_cents":NaN,"currency":"EUR"}'):
            self.ok('POST', '/deals', expected=400, raw=raw)
        self.assertEqual(self.ok('GET', '/deals'), [])
        self.assertEqual(self.ok('GET', '/audit'), [])
        deal = self.create(amount=0, currency='USD')
        self.assertEqual((deal['status'], deal['version']), ('new', 1))
        self.create(amount=100000000)
        path = '/deals/' + deal['id']
        for body in ({}, {'version': 1}, {'version': 1, 'status': 'qualified', 'tenant': 'b'}, {'version': 0, 'status': 'qualified'}, {'version': -1, 'status': 'qualified'}, {'version': True, 'status': 'qualified'}, {'version': 1.0, 'status': 'qualified'}, {'version': '1', 'status': 'qualified'}, {'version': 1, 'status': None}):
            self.ok('PATCH', path, body, 400)
        for status in ('new', 'won', 'lost', 'bogus'):
            self.ok('PATCH', path, {'version': 1, 'status': status}, 409)
        self.assertEqual(self.ok('GET', path), deal)
        self.assertEqual(len(self.ok('GET', '/audit')), 2)

    def test_transition_concurrency_and_terminals(self):
        deal = self.create()
        path = '/deals/' + deal['id']
        self.invoice(deal, expected=409)
        barrier = threading.Barrier(8)
        def transition(_):
            barrier.wait(timeout=10)
            return self.request('PATCH', path, {'version': 1, 'status': 'qualified'})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(transition, range(8)))
        self.assertEqual(sorted(code for code, _ in results), [200] + [409] * 7)
        self.invoice(deal, expected=409)
        self.ok('PATCH', path, {'version': 1, 'status': 'won'}, 409)
        lost = self.ok('PATCH', path, {'version': 2, 'status': 'lost'})
        self.assertEqual(lost['version'], 3)
        for status in ('lost', 'new', 'qualified', 'won'):
            self.ok('PATCH', path, {'version': 3, 'status': status}, 409)
        self.invoice(lost, expected=409)
        self.assertEqual([x['action'] for x in self.ok('GET', '/audit')], ['deal.created', 'deal.transitioned', 'deal.transitioned'])

    def test_invoice_race_replay_void_restart_audit(self):
        deal = self.won()
        payload = {'deal_id': deal['id'], 'request_id': 'same-key', 'tax_bps': 5000}
        for status in ('won', 'lost', 'new', 'qualified'):
            self.ok('PATCH', '/deals/' + deal['id'], {'version': 3, 'status': status}, 409)
        barrier = threading.Barrier(8)
        def issue(_):
            barrier.wait(timeout=10)
            return self.request('POST', '/invoices', payload)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(issue, range(8)))
        self.assertEqual(sorted(code for code, _ in results), [200] * 7 + [201])
        self.assertEqual(len({data['id'] for _, data in results}), 1)
        invoice = results[0][1]
        self.assertEqual((invoice['net_cents'], invoice['tax_cents'], invoice['total_cents'], invoice['currency']), (101, 51, 152, 'EUR'))
        self.assertEqual(self.ok('POST', '/invoices', dict(reversed(list(payload.items())))), invoice)
        self.invoice(deal, 'same-key', 0, expected=409)
        self.invoice(deal, 'different', expected=409)
        other = self.won()
        self.invoice(other, 'same-key', expected=409)
        foreign = self.won('owner-b')
        foreign_invoice = self.invoice(foreign, 'same-key', token='owner-b')
        self.assertNotEqual(foreign_invoice['id'], invoice['id'])
        before = self.ok('GET', '/audit')
        self.stop()
        self.start()
        self.assertEqual(self.ok('POST', '/invoices', payload), invoice)
        self.assertEqual(self.ok('GET', '/audit'), before)
        void = self.ok('POST', '/invoices/' + invoice['id'] + '/void', {'reason': 'Synthetic correction'})
        self.assertEqual(void, {**invoice, 'status': 'void'})
        self.ok('POST', '/invoices/' + invoice['id'] + '/void', {'reason': 'Again'}, 409)
        self.invoice(deal, 'after-void', expected=409)
        self.assertEqual(self.ok('POST', '/invoices', payload), void)
        self.ok('PATCH', '/invoices/' + invoice['id'], {'net_cents': 0}, 404)
        expected = [{'action': 'deal.created', 'resource_id': deal['id']}, {'action': 'deal.transitioned', 'resource_id': deal['id']}, {'action': 'deal.transitioned', 'resource_id': deal['id']}, {'action': 'invoice.issued', 'resource_id': invoice['id']}]
        expected += [{'action': a, 'resource_id': other['id']} for a in ('deal.created', 'deal.transitioned', 'deal.transitioned')]
        expected += [{'action': 'invoice.voided', 'resource_id': invoice['id']}]
        self.assertEqual(self.ok('GET', '/audit'), expected)
        self.stop()
        self.start()
        self.assertEqual(self.ok('GET', '/invoices/' + invoice['id']), void)
        self.assertEqual(self.ok('GET', '/deals/' + deal['id']), deal)
        self.assertEqual(self.ok('GET', '/audit'), expected)

    def test_invoice_validation_and_money_edges(self):
        deal = self.won()
        valid = {'deal_id': deal['id'], 'request_id': 'valid', 'tax_bps': 0}
        invalid = [{}, [], {**valid, 'tenant': 'b'}, {**valid, 'extra': 0}]
        for key in valid:
            invalid.append({k: v for k, v in valid.items() if k != key})
        for rate in (-1, 10001, True, 1.0, '1', None):
            invalid.append({**valid, 'tax_bps': rate})
        for key in ('request_id', 'deal_id'):
            for value in ('', '  ', None, [], False, 1.5):
                invalid.append({**valid, key: value})
        for body in invalid:
            self.ok('POST', '/invoices', body, 400)
        self.assertEqual(self.ok('GET', '/invoices'), [])
        invoice = self.invoice(deal, rate=0)
        for body in ({}, {'reason': ''}, {'reason': '  '}, {'reason': True}, {'reason': 'X', 'tenant': 'a'}, {'reason': 'X', 'extra': 0}):
            self.ok('POST', '/invoices/' + invoice['id'] + '/void', body, 400)
        self.assertEqual(self.ok('GET', '/invoices/' + invoice['id']), invoice)
        self.assertEqual(len(self.ok('GET', '/audit')), 4)
        for i, (amount, rate, tax) in enumerate(((0, 10000, 0), (100000000, 10000, 100000000), (1, 4999, 0), (1, 5000, 1), (1, 5001, 1))):
            d = self.won(amount=amount, currency='USD')
            inv = self.invoice(d, 'edge-' + str(i), rate)
            self.assertEqual((inv['net_cents'], inv['tax_cents'], inv['total_cents'], inv['currency']), (amount, tax, amount + tax, 'USD'))

    def test_audit_storage_failure_rolls_back_mutation(self):
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
        self.ok('POST', '/deals', {'title': 'Synthetic rollback', 'amount_cents': 1, 'currency': 'EUR'}, 500)
        self.assertEqual(self.ok('GET', '/deals'), [])
        self.assertEqual(self.ok('GET', '/audit'), [])
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('DROP TRIGGER fail_audit')
        deal = self.won()
        invoice = self.invoice(deal)
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
        self.ok('POST', '/invoices/' + invoice['id'] + '/void', {'reason': 'Synthetic'}, 500)
        self.assertEqual(self.ok('GET', '/invoices/' + invoice['id']), invoice)
        self.assertEqual(len(self.ok('GET', '/audit')), 4)

    def test_failed_migration_is_atomic(self):
        self.stop()
        broken = Path(self.temp.name) / 'broken.sqlite'
        with closing(sqlite3.connect(broken)) as db, db:
            db.executescript((ROOT / 'migrations/001_legacy.sql').read_text())
            db.execute("INSERT INTO deals VALUES(9,'a','Synthetic',1,'EUR','new')")
            # An unexpected table makes migration fail after it has rebuilt deals.
            db.execute('CREATE TABLE invoices(id TEXT)')
        result = subprocess.run([sys.executable, str(ROOT / 'app.py'), 'serve', '--db', str(broken), '--port', '0'], cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        with closing(sqlite3.connect(broken)) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT * FROM deals').fetchall(), [(9, 'a', 'Synthetic', 1, 'EUR', 'new')])
            self.assertEqual([r[1] for r in db.execute('PRAGMA table_info(deals)')], ['id', 'tenant', 'title', 'amount_cents', 'currency', 'status'])
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='legacy_deals'").fetchone())

    def test_v1_migration_and_restarts(self):
        self.stop()
        # A separate synthetic legacy file, not the fresh DB.
        self.db = Path(self.temp.name) / 'legacy.sqlite'
        with closing(sqlite3.connect(self.db)) as db, db:
            db.executescript((ROOT / 'migrations/001_legacy.sql').read_text())
            db.executemany('INSERT INTO deals VALUES(?,?,?,?,?,?)', [(7, 'a', 'Legacy A', 301, 'EUR', 'won'), (12, 'b', 'Legacy B', 500, 'USD', 'new')])
        self.start()
        a = self.ok('GET', '/deals/7')
        self.assertEqual(a, {'id': 7, 'title': 'Legacy A', 'amount_cents': 301, 'currency': 'EUR', 'status': 'won', 'version': 1})
        self.assertEqual(self.ok('GET', '/deals'), [a])
        self.ok('GET', '/deals/12', expected=404)
        b = self.ok('GET', '/deals/12', token='viewer-b')
        self.assertEqual(b['id'], 12)
        self.assertEqual(b['version'], 1)
        self.assertEqual(self.ok('GET', '/audit'), [])
        invoice = self.invoice(a, rate=5000)
        self.assertEqual(invoice['deal_id'], 7)
        self.assertEqual(invoice['tax_cents'], 151)
        self.ok('PATCH', '/deals/12', {'version': 1, 'status': 'qualified'}, token='editor-b')
        created = self.create()
        for _ in range(2):
            self.stop()
            self.start()
            self.assertEqual(self.ok('GET', '/deals/7'), a)
            self.assertEqual(self.invoice(a, rate=5000, expected=200), invoice)
            self.assertEqual(self.ok('GET', '/deals/' + created['id']), created)
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 2)
            self.assertEqual(db.execute('SELECT version FROM deals WHERE id=12').fetchone()[0], 2)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')


if __name__ == '__main__':
    unittest.main()
