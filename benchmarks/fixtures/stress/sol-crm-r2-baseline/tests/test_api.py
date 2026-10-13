"""Black-box tests: actual CLI processes, loopback HTTP and SQLite persistence."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import selectors
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RunningServer:
    def __init__(self, db):
        self.process = subprocess.Popen(
            [sys.executable, str(ROOT / "app.py"), "serve", "--db", str(db), "--port", "0"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            if not selector.select(10):
                self.stop()
                raise AssertionError("CLI did not announce readiness")
        line = self.process.stdout.readline()
        if not line:
            self.stop()
            raise AssertionError("CLI exited before readiness")
        ready = json.loads(line)
        assert set(ready) == {"port"} and type(ready["port"]) is int
        assert 0 < ready["port"] <= 65535
        self.port = ready["port"]

    def stop(self):
        self.process.terminate()
        try:
            stdout, stderr = self.process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            stdout, stderr = self.process.communicate()
        if stdout:
            raise AssertionError(f"Unexpected extra stdout: {stdout}")
        if stderr:
            raise AssertionError(f"Unexpected server error: {stderr}")

    def request(self, method, path, body=None, token="owner-a", raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        payload = raw if raw is not None else (json.dumps(body) if body is not None else None)
        try:
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            data = response.read()
            assert response.getheader("Content-Type") == "application/json"
            return response.status, json.loads(data)
        finally:
            connection.close()


class APITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".ledger-tests-", dir=ROOT)
        self.db = Path(self.temp.name) / "ledger.sqlite"
        self.server = RunningServer(self.db)

    def tearDown(self):
        try:
            self.server.stop()
        finally:
            self.temp.cleanup()

    def request(self, method, path, body=None, expected=200, token="owner-a", raw=None):
        status, data = self.server.request(method, path, body, token, raw)
        self.assertEqual(status, expected, (method, path, body, data))
        return data

    def create(self, token="owner-a", amount=101, currency="EUR"):
        return self.request("POST", "/deals", {"title": "Synthetic opportunity", "amount_cents": amount,
                                             "currency": currency}, 201, token)

    def won(self, token="owner-a", amount=101, currency="EUR"):
        deal = self.create(token, amount, currency)
        for state in ("qualified", "won"):
            deal = self.request("PATCH", f"/deals/{deal['id']}",
                                {"version": deal["version"], "status": state}, token=token)
        return deal

    def issue(self, deal, request_id="test-request", bps=1900, token="owner-a", expected=201):
        return self.request("POST", "/invoices", {"deal_id": deal["id"], "request_id": request_id,
                                                "tax_bps": bps}, expected, token)

    def counts(self):
        with sqlite3.connect(self.db) as db:
            return tuple(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                         for table in ("deals", "invoices", "audit"))

    def restart(self):
        self.server.stop()
        self.server = RunningServer(self.db)

    def test_cli_persistence_workflow_audit_and_void(self):
        deal = self.won(amount=3, currency="USD")
        self.assertEqual(deal["version"], 3)
        invoice = self.issue(deal, bps=5000)
        self.assertEqual(invoice, {
            "id": invoice["id"], "deal_id": deal["id"], "request_id": "test-request",
            "net_cents": 3, "tax_cents": 2, "total_cents": 5, "currency": "USD", "status": "issued",
        })
        self.assertEqual(self.request("GET", "/invoices"), [invoice])
        self.assertEqual(self.request("GET", f"/invoices/{invoice['id']}"), invoice)
        self.assertEqual(self.issue(deal, bps=5000, expected=200), invoice)
        self.restart()
        self.assertEqual(self.request("GET", "/deals"), [deal])
        self.assertEqual(self.issue(deal, bps=5000, expected=200), invoice)
        void = self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "Synthetic correction"})
        self.assertEqual(void, {**invoice, "status": "void"})
        self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "repeat"}, 409)
        self.issue(deal, request_id="another", expected=409)
        self.assertEqual(self.issue(deal, bps=5000, expected=200), void)
        self.request("PATCH", f"/invoices/{invoice['id']}", {"net_cents": 0}, 404)
        self.request("DELETE", f"/invoices/{invoice['id']}", expected=404)
        events = self.request("GET", "/audit")
        self.assertEqual(events, [
            {"action": "deal.created", "resource_id": deal["id"]},
            {"action": "deal.transitioned", "resource_id": deal["id"]},
            {"action": "deal.transitioned", "resource_id": deal["id"]},
            {"action": "invoice.issued", "resource_id": invoice["id"]},
            {"action": "invoice.voided", "resource_id": invoice["id"]},
        ])
        self.restart()
        self.assertEqual(self.request("GET", "/audit"), events)
        self.assertEqual(self.request("GET", "/invoices"), [void])
        self.assertEqual(self.counts(), (1, 1, 5))
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT void_reason FROM invoices").fetchone()[0],
                             "Synthetic correction")

    def test_missing_unknown_auth_all_business_routes(self):
        routes = (("GET", "/deals", None), ("GET", "/deals/missing", None),
                  ("POST", "/deals", {}), ("PATCH", "/deals/missing", {}),
                  ("GET", "/invoices", None), ("GET", "/invoices/missing", None),
                  ("POST", "/invoices", {}), ("POST", "/invoices/missing/void", {}),
                  ("GET", "/audit", None))
        for token in (None, "unknown", "owner-c", "Owner-a", "owner-a "):
            for method, path, body in routes:
                with self.subTest(token=token, path=path):
                    self.request(method, path, body, 401, token)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_role_matrix_and_tenant_isolation(self):
        for tenant in ("a", "b"):
            owner, editor, viewer = (f"{role}-{tenant}" for role in ("owner", "editor", "viewer"))
            deal = self.create(editor)
            for token in (owner, editor, viewer):
                self.assertEqual(self.request("GET", "/deals", token=token), [deal])
                self.assertEqual(self.request("GET", f"/deals/{deal['id']}", token=token), deal)
                self.request("GET", "/invoices", token=token)
                self.request("GET", "/audit", token=token)
            self.request("POST", "/deals", {}, 403, viewer)
            self.request("PATCH", f"/deals/{deal['id']}", {"version": 1, "status": "qualified"}, 403, viewer)
            for version, state, token in ((1, "qualified", editor), (2, "won", owner)):
                deal = self.request("PATCH", f"/deals/{deal['id']}", {"version": version, "status": state}, token=token)
            for token in (editor, viewer):
                self.issue(deal, token=token, expected=403)
            invoice = self.issue(deal, token=owner)
            for token in (owner, editor, viewer):
                self.assertEqual(self.request("GET", "/invoices", token=token), [invoice])
                self.assertEqual(self.request("GET", f"/invoices/{invoice['id']}", token=token), invoice)
            for token in (editor, viewer):
                self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "test"}, 403, token)
            other = "b" if tenant == "a" else "a"
            for token in (f"owner-{other}", f"editor-{other}", f"viewer-{other}"):
                self.request("GET", f"/deals/{deal['id']}", expected=404, token=token)
                self.request("GET", f"/invoices/{invoice['id']}", expected=404, token=token)
                # A valid write role must still not resolve a foreign object.
                if not token.startswith("viewer"):
                    self.request("PATCH", f"/deals/{deal['id']}", {"version": 3, "status": "lost"}, 404, token)
                if token.startswith("owner"):
                    self.issue(deal, token=token, expected=404)
                    self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "test"}, 404, token)
            self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "test"}, token=owner)
        # Identical request keys are independent, and lists/audit never leak IDs.
        a_deals = self.request("GET", "/deals")
        b_deals = self.request("GET", "/deals", token="viewer-b")
        self.assertTrue(set(d["id"] for d in a_deals).isdisjoint(d["id"] for d in b_deals))
        for token, deals in (("viewer-a", a_deals), ("viewer-b", b_deals)):
            invoices = self.request("GET", "/invoices", token=token)
            allowed = {d["id"] for d in deals} | {i["id"] for i in invoices}
            events = self.request("GET", "/audit", token=token)
            self.assertEqual(len(events), 5)
            self.assertTrue(all(e["resource_id"] in allowed for e in events))

    def test_deal_shape_json_types_and_boundaries(self):
        valid = {"title": "Synthetic", "amount_cents": 1, "currency": "EUR"}
        invalid = [None, [], "x", 1, {}, {**valid, "tenant": "a"}, {**valid, "extra": 1}]
        invalid.extend({k: v for k, v in valid.items() if k != field} for field in valid)
        for field, values in (
            ("title", (None, False, 12, [], {}, "", "  \t\n")),
            ("amount_cents", (None, True, False, 1.0, "1", [], -1, 100000001)),
            ("currency", (None, 1, [], {}, "eur", "GBP", "EUR ")),
        ):
            invalid.extend({**valid, field: value} for value in values)
        for body in invalid:
            with self.subTest(body=body):
                self.request("POST", "/deals", body, 400, raw="null" if body is None else None)
        for raw in ("", "{", '{"title":"x",}', 'null',
                    '{"title":"x","title":"y","amount_cents":1,"currency":"EUR"}',
                    '{"title":"x","amount_cents":NaN,"currency":"EUR"}', b'\xff'):
            with self.subTest(raw=raw):
                self.request("POST", "/deals", expected=400, raw=raw)
        self.assertEqual(self.counts(), (0, 0, 0))
        for amount in (0, 100000000):
            for currency in ("EUR", "USD"):
                deal = self.create(amount=amount, currency=currency)
                self.assertEqual(set(deal), {"id", "title", "amount_cents", "currency", "status", "version"})
                self.assertEqual((deal["amount_cents"], deal["currency"], deal["status"], deal["version"]),
                                 (amount, currency, "new", 1))
        self.assertEqual(self.counts(), (4, 0, 4))

    def test_transition_validation_conflicts_and_missing(self):
        deal = self.create()
        path = f"/deals/{deal['id']}"
        invalid = [None, [], {}, {"version": 1}, {"status": "qualified"},
                   {"version": 1, "status": "qualified", "tenant": "b"}]
        invalid.extend({"version": value, "status": "qualified"}
                       for value in (0, -1, True, 1.0, "1", None, []))
        invalid.extend({"version": 1, "status": value} for value in (None, True, 1, [], {}))
        for body in invalid:
            self.request("PATCH", path, body, 400, raw="null" if body is None else None)
        for state in ("new", "won", "lost", "unknown", ""):
            self.request("PATCH", path, {"version": 1, "status": state}, 409)
        self.request("PATCH", path, {"version": 2, "status": "qualified"}, 409)
        self.assertEqual(self.request("GET", path), deal)
        self.request("PATCH", "/deals/missing", {"version": 1, "status": "qualified"}, 404)
        self.request("GET", "/deals/missing", expected=404)
        qualified = self.request("PATCH", path, {"version": 1, "status": "qualified"})
        self.assertEqual(qualified["version"], 2)
        self.request("PATCH", path, {"version": 1, "status": "won"}, 409)
        self.request("PATCH", path, {"version": 2, "status": "qualified"}, 409)
        lost = self.request("PATCH", path, {"version": 2, "status": "lost"})
        for state in ("new", "qualified", "won", "lost"):
            self.request("PATCH", path, {"version": 3, "status": state}, 409)
        self.assertEqual(self.request("GET", path), lost)
        self.assertEqual(self.counts(), (1, 0, 3))

    def test_invoice_validation_rounding_and_idempotency_conflicts(self):
        deal = self.won(amount=1)
        valid = {"deal_id": deal["id"], "request_id": "rounding", "tax_bps": 5000}
        invalid = [None, [], {}, {**valid, "tenant": "a"}, {**valid, "total_cents": 999}]
        invalid.extend({k: v for k, v in valid.items() if k != field} for field in valid)
        for field, values in (("tax_bps", (None, True, 1.0, "1", -1, 10001, [])),
                              ("request_id", (None, True, 1, [], "", "   ")),
                              ("deal_id", (None, True, 1.0, [], {}, "", "   "))):
            invalid.extend({**valid, field: value} for value in values)
        before = self.counts()
        for body in invalid:
            self.request("POST", "/invoices", body, 400, raw="null" if body is None else None)
        self.request("POST", "/invoices", expected=400, raw="{")
        self.request("POST", "/invoices", {**valid, "deal_id": "missing"}, 404)
        self.request("GET", "/invoices/missing", expected=404)
        self.assertEqual(self.counts(), before)
        for state in ("new", "qualified", "lost"):
            nonwon = self.create()
            if state != "new":
                nonwon = self.request("PATCH", f"/deals/{nonwon['id']}", {"version": 1, "status": "qualified"})
            if state == "lost":
                nonwon = self.request("PATCH", f"/deals/{nonwon['id']}", {"version": 2, "status": "lost"})
            self.issue(nonwon, request_id="never-issued", expected=409)
        invoice = self.issue(deal, request_id="rounding", bps=5000)
        self.assertEqual((invoice["net_cents"], invoice["tax_cents"], invoice["total_cents"]), (1, 1, 2))
        self.assertEqual(self.issue(deal, request_id="rounding", bps=5000, expected=200), invoice)
        before = self.counts()
        self.issue(deal, request_id="rounding", bps=5001, expected=409)
        self.issue(deal, request_id="different", bps=5000, expected=409)
        other = self.won(amount=0)
        count_with_other = self.counts()
        self.issue(other, request_id="rounding", bps=5000, expected=409)
        self.assertEqual(self.counts(), count_with_other)
        zero = self.issue(other, request_id="zero", bps=0)
        self.assertEqual((zero["tax_cents"], zero["total_cents"]), (0, 0))
        maximum = self.issue(self.won(amount=100000000), request_id="max", bps=10000)
        self.assertEqual((maximum["tax_cents"], maximum["total_cents"]), (100000000, 200000000))
        self.restart()
        self.assertEqual(self.issue(deal, request_id="rounding", bps=5000, expected=200), invoice)
        self.issue(deal, request_id="rounding", bps=4999, expected=409)
        self.assertEqual(before[1], 1)

    def test_void_invalid_shapes_and_missing(self):
        invoice = self.issue(self.won())
        path = f"/invoices/{invoice['id']}/void"
        before = self.counts()
        for body in (None, [], {}, {"reason": "x", "tenant": "a"}, {"reason": "x", "extra": 1},
                     {"reason": ""}, {"reason": "  "}, {"reason": None}, {"reason": 1}, {"reason": True}):
            self.request("POST", path, body, 400, raw="null" if body is None else None)
        self.request("POST", path, expected=400, raw="{")
        self.request("POST", "/invoices/missing/void", {"reason": "x"}, 404)
        self.assertEqual(self.request("GET", f"/invoices/{invoice['id']}"), invoice)
        self.assertEqual(self.counts(), before)

    def parallel(self, method, path, bodies):
        barrier = threading.Barrier(len(bodies))
        def call(body):
            barrier.wait(timeout=10)
            return self.server.request(method, path, body)
        with ThreadPoolExecutor(max_workers=len(bodies)) as pool:
            return list(pool.map(call, bodies))

    def test_concurrent_same_version_transitions(self):
        deal = self.create()
        results = self.parallel("PATCH", f"/deals/{deal['id']}",
                                [{"version": 1, "status": "qualified"}] * 8)
        self.assertEqual(sorted(status for status, _ in results), [200] + [409] * 7)
        self.assertEqual(self.request("GET", f"/deals/{deal['id']}")["version"], 2)
        self.assertEqual(self.counts(), (1, 0, 2))
        results = self.parallel("PATCH", f"/deals/{deal['id']}",
                                [{"version": 2, "status": state} for state in ("won", "lost")])
        self.assertEqual(sorted(status for status, _ in results), [200, 409])
        self.assertEqual(self.counts(), (1, 0, 3))

    def test_concurrent_invoice_requests_and_void(self):
        deal = self.won()
        body = {"deal_id": deal["id"], "request_id": "parallel", "tax_bps": 1900}
        results = self.parallel("POST", "/invoices", [body] * 8)
        self.assertEqual(sorted(status for status, _ in results), [200] * 7 + [201])
        invoices = [invoice for _, invoice in results]
        self.assertTrue(all(invoice == invoices[0] for invoice in invoices))
        self.assertEqual(self.counts(), (1, 1, 4))
        invoice = invoices[0]
        results = self.parallel("POST", f"/invoices/{invoice['id']}/void", [{"reason": "test"}] * 4)
        self.assertEqual(sorted(status for status, _ in results), [200, 409, 409, 409])
        self.assertEqual(self.counts(), (1, 1, 5))
        other = self.won()
        results = self.parallel("POST", "/invoices", [
            {"deal_id": other["id"], "request_id": "race-1", "tax_bps": 0},
            {"deal_id": other["id"], "request_id": "race-2", "tax_bps": 0},
        ])
        self.assertEqual(sorted(status for status, _ in results), [201, 409])
        self.assertEqual(self.counts(), (2, 2, 9))

    def test_concurrent_same_request_different_payload(self):
        deals = [self.won(), self.won()]
        before = self.counts()
        results = self.parallel("POST", "/invoices", [
            {"deal_id": deal["id"], "request_id": "shared", "tax_bps": 0} for deal in deals
        ])
        self.assertEqual(sorted(status for status, _ in results), [201, 409])
        self.assertEqual(self.counts(), (before[0], before[1] + 1, before[2] + 1))
        winner = next(invoice for status, invoice in results if status == 201)
        self.assertEqual(self.request("GET", "/invoices"), [winner])

    def test_mutation_and_audit_rollback_on_storage_failure(self):
        # Inject a deterministic failure at the last step of each transaction.
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN "
                       "SELECT RAISE(ABORT, 'synthetic audit failure'); END")
        # Error is observable (500), and there is no partial deal commit.
        status, data = self.server.request("POST", "/deals", {
            "title": "Synthetic", "amount_cents": 1, "currency": "EUR"})
        self.assertEqual(status, 500)
        self.assertEqual(data, {"error": "Internal server error"})
        self.assertEqual(self.counts(), (0, 0, 0))
        # Consume the expected sanitized error log; stop() rejects unexpected logs.
        self.assertEqual(self.server.process.stderr.readline(), "Ledger request failed\n")
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TRIGGER fail_audit")
        transition_candidate = self.create()
        deal = self.won()
        invoice = self.issue(deal)
        issue_candidate = self.won()
        before = self.counts()
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN "
                       "SELECT RAISE(ABORT, 'synthetic audit failure'); END")
        self.request("PATCH", f"/deals/{transition_candidate['id']}",
                     {"version": 1, "status": "qualified"}, 500)
        self.assertEqual(self.server.process.stderr.readline(), "Ledger request failed\n")
        self.issue(issue_candidate, request_id="must-rollback", expected=500)
        self.assertEqual(self.server.process.stderr.readline(), "Ledger request failed\n")
        self.request("POST", f"/invoices/{invoice['id']}/void", {"reason": "test"}, 500)
        self.assertEqual(self.server.process.stderr.readline(), "Ledger request failed\n")
        self.assertEqual(self.request("GET", f"/deals/{transition_candidate['id']}"), transition_candidate)
        self.assertEqual(self.request("GET", f"/invoices/{invoice['id']}"), invoice)
        self.assertEqual(self.counts(), before)
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TRIGGER fail_audit")
        # Failed issuance did not reserve either the key or the deal.
        self.issue(issue_candidate, request_id="must-rollback")
