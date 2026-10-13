import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from test_api import ROOT, RunningServer
sys.path.insert(0, str(ROOT / "src"))
from ledger.db import migrate


V1 = """CREATE TABLE deals(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL,
    title TEXT NOT NULL, amount_cents INTEGER NOT NULL, currency TEXT NOT NULL,
    status TEXT NOT NULL)"""


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".ledger-migration-", dir=ROOT)
        self.db = Path(self.temp.name) / "legacy.sqlite"

    def tearDown(self):
        self.temp.cleanup()

    def seed(self):
        rows = [(7, "a", "Synthetic legacy won", 3, "USD", "won"),
                (19, "a", "Synthetic legacy new", 0, "EUR", "new"),
                (88, "b", "Synthetic foreign", 999, "EUR", "qualified")]
        with sqlite3.connect(self.db) as db:
            db.execute(V1)
            db.executemany("INSERT INTO deals VALUES(?,?,?,?,?,?)", rows)
            db.execute("PRAGMA user_version=1")
        return rows

    def test_legacy_migration_http_ids_isolation_and_restarts(self):
        original = self.seed()
        invoice = None
        for restart in range(3):
            server = RunningServer(self.db)
            try:
                status, deals = server.request("GET", "/deals", token="viewer-a")
                self.assertEqual(status, 200)
                self.assertEqual([deal["id"] for deal in deals], [7, 19])
                self.assertEqual([deal["version"] for deal in deals], [1, 1])
                self.assertEqual(server.request("GET", "/deals/88")[0], 404)
                self.assertEqual(server.request("GET", "/deals/7", token="viewer-b")[0], 404)
                self.assertEqual(server.request("POST", "/invoices", {
                    "deal_id": 88, "request_id": "foreign", "tax_bps": 0})[0], 404)
                status, got = server.request("POST", "/invoices", {
                    "deal_id": 7 if restart == 0 else "7", "request_id": "legacy", "tax_bps": 5000})
                self.assertEqual(status, 201 if restart == 0 else 200)
                if invoice is None:
                    invoice = got
                self.assertEqual(got, invoice)
                self.assertEqual((got["deal_id"], got["tax_cents"], got["total_cents"]), (7, 2, 5))
                self.assertEqual(server.request("GET", "/audit")[1],
                                 [{"action": "invoice.issued", "resource_id": invoice["id"]}])
                self.assertEqual(server.request("GET", "/audit", token="viewer-b")[1], [])
            finally:
                server.stop()
            with sqlite3.connect(self.db) as db:
                self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 2)
                self.assertEqual(db.execute("SELECT id,tenant,title,amount_cents,currency,status "
                                            "FROM deals ORDER BY id").fetchall(), original)
                self.assertEqual(db.execute("SELECT version FROM deals").fetchall(), [(1,), (1,), (1,)])
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        # New opaque IDs coexist with preserved integer IDs and legacy transitions.
        server = RunningServer(self.db)
        try:
            status, new = server.request("POST", "/deals", {
                "title": "Synthetic new", "amount_cents": 1, "currency": "EUR"})
            self.assertEqual(status, 201)
            self.assertIsInstance(new["id"], str)
            self.assertEqual(server.request("PATCH", "/deals/19", {"version": 1, "status": "qualified"})[0], 200)
        finally:
            server.stop()

    def test_fresh_repeated_migration_and_database_constraints(self):
        migrate(self.db)
        migrate(self.db)
        with sqlite3.connect(self.db) as db:
            db.execute("PRAGMA foreign_keys=ON")
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 2)
            db.execute("INSERT INTO deals VALUES('d','a','Synthetic',1,'EUR','won',1)")
            sql = ("INSERT INTO invoices(id,tenant,deal_id,request_id,tax_bps,net_cents,tax_cents,"
                   "total_cents,currency,status) VALUES(?,?,?,?,0,1,0,1,'EUR','issued')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(sql, ("bad", "b", "d", "test"))
            db.execute(sql, ("good", "a", "d", "test"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(sql, ("duplicate", "a", "d", "another"))
            db.execute("INSERT INTO deals VALUES('d2','a','Synthetic',1,'EUR','won',1)")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(sql, ("duplicate-request", "a", "d2", "test"))

    def test_migration_failure_rolls_back_schema_and_version(self):
        self.seed()
        # An unexpected preexisting table forces the second migration to fail.
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TABLE invoices(unexpected TEXT)")
        with self.assertRaises(sqlite3.OperationalError):
            migrate(self.db)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertEqual([row[1] for row in db.execute("PRAGMA table_info(deals)")],
                             ["id", "tenant", "title", "amount_cents", "currency", "status"])
            self.assertEqual(db.execute("SELECT count(*) FROM deals").fetchone()[0], 3)
            self.assertEqual(db.execute("SELECT name FROM sqlite_master WHERE name='deals_v1'").fetchall(), [])

    def test_future_schema_rejected_without_mutation(self):
        with sqlite3.connect(self.db) as db:
            db.execute("PRAGMA user_version=99")
        with self.assertRaisesRegex(RuntimeError, "Unsupported database version"):
            migrate(self.db)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 99)
            self.assertEqual(db.execute("SELECT name FROM sqlite_master").fetchall(), [])
