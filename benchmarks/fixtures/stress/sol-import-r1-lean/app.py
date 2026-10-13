#!/usr/bin/env python3
"""Local inventory batches; all durable decisions are SQLite transactions."""
import argparse
from collections import Counter
from contextlib import contextmanager
import csv
import io
import json
from pathlib import Path
import re
import sqlite3
import sys

VERSION = 1
SEED_HEADER = ['sku', 'warehouse', 'quantity']
APPLY_HEADER = ['group_id', 'transfer_id', 'sku', 'from_warehouse', 'to_warehouse', 'quantity']
SCHEMA = [
    'CREATE TABLE tenants (tenant TEXT PRIMARY KEY, seeded INTEGER NOT NULL DEFAULT 0)',
    '''CREATE TABLE stock (tenant TEXT NOT NULL REFERENCES tenants(tenant), sku TEXT NOT NULL,
       warehouse TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity >= 0),
       PRIMARY KEY(tenant, sku, warehouse))''',
    '''CREATE TABLE runs (tenant TEXT NOT NULL REFERENCES tenants(tenant), run_id TEXT NOT NULL,
       input BLOB NOT NULL, status TEXT NOT NULL CHECK(status IN ('interrupted','completed')),
       PRIMARY KEY(tenant, run_id))''',
    '''CREATE TABLE decisions (tenant TEXT NOT NULL, run_id TEXT NOT NULL, position INTEGER NOT NULL,
       group_id TEXT NOT NULL, applied_rows INTEGER NOT NULL, reason TEXT,
       PRIMARY KEY(tenant, run_id, position), UNIQUE(tenant, run_id, group_id),
       FOREIGN KEY(tenant,run_id) REFERENCES runs(tenant,run_id))''',
    '''CREATE TABLE ledger (tenant TEXT NOT NULL, run_id TEXT NOT NULL, transfer_id TEXT NOT NULL,
       group_id TEXT NOT NULL, sku TEXT NOT NULL, source TEXT NOT NULL, destination TEXT NOT NULL,
       quantity INTEGER NOT NULL CHECK(quantity > 0), PRIMARY KEY(tenant,run_id,transfer_id),
       FOREIGN KEY(tenant,run_id,group_id) REFERENCES decisions(tenant,run_id,group_id))''',
]


class Failure(Exception):
    def __init__(self, kind, reason):
        self.kind, self.reason = kind, reason
        super().__init__(reason)


def invalid(reason):
    raise Failure('invalid_input', reason)


def name(value, label):
    if not value.strip():
        invalid(label + ' must be nonblank')
    return value


def quantity(value, positive=False):
    if not re.fullmatch(r'[0-9]+', value) or len(value.lstrip('0')) > 7:
        invalid('quantity must be a base-10 integer in range')
    number = int(value.lstrip('0') or '0')
    if number > 1000000 or number < int(positive):
        invalid('quantity out of range')
    return number


def load_csv(path, header):
    raw = Path(path).read_bytes()
    try:
        reader = csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True)
        if next(reader, None) != header:
            invalid('incorrect CSV header')
        rows = list(reader)
    except (UnicodeError, csv.Error) as exc:
        invalid('malformed CSV: ' + str(exc))
    return raw, rows


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK')
        raise


def connect(path):
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with transaction(db):
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version == 0:
                if db.execute("SELECT 1 FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchone():
                    raise Failure('storage_error', 'unversioned nonempty database; migration required')
                for statement in SCHEMA:
                    db.execute(statement)
                db.execute('PRAGMA user_version=1')
            elif version != VERSION:
                raise Failure('storage_error', 'unsupported schema version; migration required')
    except BaseException:
        db.close()
        raise
    return db


def seed_accounts(rows):
    accounts = {}
    for row in rows:
        if len(row) != 3:
            invalid('seed row must have three cells')
        sku, warehouse = name(row[0], 'sku'), name(row[1], 'warehouse')
        key = (sku, warehouse)
        if key in accounts:
            invalid('duplicate SKU/warehouse')
        accounts[key] = quantity(row[2])
    return accounts


def seed(db, tenant, accounts):
    with transaction(db):
        existing = db.execute('SELECT seeded FROM tenants WHERE tenant=?', (tenant,)).fetchone()
        if existing and existing[0]:
            raise Failure('conflict', 'tenant has already been seeded')
        db.execute('INSERT OR IGNORE INTO tenants(tenant) VALUES (?)', (tenant,))
        # Preserve any accounts created by earlier transfers; seed is initial inventory only.
        if db.execute('SELECT 1 FROM stock WHERE tenant=? LIMIT 1', (tenant,)).fetchone():
            raise Failure('conflict', 'tenant already has inventory')
        db.executemany('INSERT INTO stock VALUES (?,?,?,?)',
                       [(tenant, sku, wh, qty) for (sku, wh), qty in accounts.items()])
        db.execute('UPDATE tenants SET seeded=1 WHERE tenant=?', (tenant,))
    return {'status': 'seeded', 'tenant': tenant, 'accounts': len(accounts)}


def groups_from(rows):
    groups = {}
    ids = Counter(row[1] for row in rows if len(row) >= 2)
    for row in rows:
        group = row[0] if row else ''
        groups.setdefault(group, []).append(row)
    duplicates = {key for key, count in ids.items() if count > 1}
    return list(groups.items()), duplicates


def decide(db, tenant, run_id, position, group, rows, duplicates):
    """Caller holds writer lock. Stage balances in memory; reject without any writes."""
    balances, transfers = {}, []
    reason = None
    try:
        name(group, 'group_id')
        for row in rows:
            if len(row) != 6:
                invalid('transfer row must have six cells')
            _, tid, sku, source, destination, value = row
            for field, label in [(tid, 'transfer_id'), (sku, 'sku'),
                                 (source, 'from_warehouse'), (destination, 'to_warehouse')]:
                name(field, label)
            if tid in duplicates:
                invalid('duplicate transfer_id: ' + tid)
            if source == destination:
                invalid('source and destination must differ')
            amount = quantity(value, positive=True)
            for warehouse in (source, destination):
                key = (sku, warehouse)
                if key not in balances:
                    account = db.execute('SELECT quantity FROM stock WHERE tenant=? AND sku=? AND warehouse=?',
                                         (tenant, sku, warehouse)).fetchone()
                    balances[key] = account[0] if account else 0
            if balances[(sku, source)] < amount:
                invalid('insufficient stock for ' + sku + ' at ' + source)
            balances[(sku, source)] -= amount
            balances[(sku, destination)] += amount
            transfers.append((tenant, run_id, tid, group, sku, source, destination, amount))
    except Failure as exc:
        reason = exc.reason
    db.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?)',
               (tenant, run_id, position, group, len(rows) if reason is None else 0, reason))
    if reason is None:
        db.executemany('''INSERT INTO stock VALUES (?,?,?,?) ON CONFLICT(tenant,sku,warehouse)
                          DO UPDATE SET quantity=excluded.quantity''',
                       [(tenant, sku, wh, qty) for (sku, wh), qty in balances.items()])
        db.executemany('INSERT INTO ledger VALUES (?,?,?,?,?,?,?,?)', transfers)


def report(db, tenant, run_id, replayed=False):
    status = db.execute('SELECT status FROM runs WHERE tenant=? AND run_id=?', (tenant, run_id)).fetchone()[0]
    decisions = db.execute('SELECT * FROM decisions WHERE tenant=? AND run_id=? ORDER BY position',
                           (tenant, run_id)).fetchall()
    errors = [{'group_id': row['group_id'], 'reason': row['reason']}
              for row in decisions if row['reason'] is not None]
    return {'run_id': run_id, 'status': status, 'applied_groups': len(decisions) - len(errors),
            'rejected_groups': len(errors), 'applied_rows': sum(row['applied_rows'] for row in decisions),
            'replayed': replayed, 'errors': errors}


def apply(db, tenant, run_id, raw, rows, fail_after):
    groups, duplicates = groups_from(rows)
    with transaction(db):
        existing = db.execute('SELECT input,status FROM runs WHERE tenant=? AND run_id=?',
                              (tenant, run_id)).fetchone()
        if existing:
            if existing['input'] != raw:
                raise Failure('conflict', 'run identity already exists with different input bytes')
            if existing['status'] == 'completed':
                return report(db, tenant, run_id, True), 0
        else:
            db.execute('INSERT OR IGNORE INTO tenants(tenant) VALUES (?)', (tenant,))
            db.execute('INSERT INTO runs VALUES (?,?,?,?)', (tenant, run_id, raw, 'interrupted'))
    decided_here = 0
    for position, (group, group_rows) in enumerate(groups):
        with transaction(db):
            if db.execute('SELECT 1 FROM decisions WHERE tenant=? AND run_id=? AND position=?',
                          (tenant, run_id, position)).fetchone():
                continue
            decide(db, tenant, run_id, position, group, group_rows, duplicates)
            decided_here += 1
            if fail_after is not None and decided_here == fail_after:
                # Capture exactly the committed crash boundary while still holding the lock.
                result = report(db, tenant, run_id)
        if fail_after is not None and decided_here == fail_after:
            return result, 3
    with transaction(db):
        db.execute("UPDATE runs SET status='completed' WHERE tenant=? AND run_id=?", (tenant, run_id))
        return report(db, tenant, run_id), 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        invalid(message)

    def exit(self, status=0, message=None):
        # Help is JSON too, rather than argparse's plain-text stdout.
        if status:
            invalid(message or 'argument error')
        raise Failure('help', self.format_help())

    def print_help(self, file=None):
        pass


def main(argv=None):
    db = None
    try:
        parser = Parser(description=__doc__)
        sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
        for command in ('seed', 'apply', 'stock', 'runs'):
            child = sub.add_parser(command)
            child.add_argument('--db', required=True)
            child.add_argument('--tenant', required=True)
            if command == 'seed':
                child.add_argument('--stock', required=True)
            if command == 'apply':
                child.add_argument('--csv', required=True)
                child.add_argument('--run-id', required=True)
                child.add_argument('--fail-after-groups', type=int)
        args = parser.parse_args(argv)
        name(args.tenant, 'tenant')
        if args.command == 'apply':
            name(args.run_id, 'run-id')
            if args.fail_after_groups is not None and args.fail_after_groups < 1:
                invalid('fail-after-groups must be >= 1')
            raw, rows = load_csv(args.csv, APPLY_HEADER)
        elif args.command == 'seed':
            _, rows = load_csv(args.stock, SEED_HEADER)
            accounts = seed_accounts(rows)
        db = connect(args.db)
        code = 0
        if args.command == 'seed':
            result = seed(db, args.tenant, accounts)
        elif args.command == 'apply':
            result, code = apply(db, args.tenant, args.run_id, raw, rows, args.fail_after_groups)
        elif args.command == 'stock':
            result = [dict(row) for row in db.execute(
                'SELECT sku,warehouse,quantity FROM stock WHERE tenant=? ORDER BY sku,warehouse', (args.tenant,))]
        else:
            # A single snapshot prevents mixed status/counts during concurrent updates.
            with transaction(db):
                result = [report(db, args.tenant, row[0]) for row in db.execute(
                    'SELECT run_id FROM runs WHERE tenant=? ORDER BY run_id', (args.tenant,)).fetchall()]
    except Failure as exc:
        result = {'status': exc.kind, 'reason': exc.reason}
        code = 0 if exc.kind == 'help' else 2
    except ValueError as exc:
        result = {'status': 'invalid_input', 'reason': str(exc)}
        code = 2
    except (OSError, sqlite3.Error) as exc:
        result = {'status': 'storage_error', 'reason': str(exc)}
        code = 2
    finally:
        if db is not None:
            db.close()
    print(json.dumps(result, ensure_ascii=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
