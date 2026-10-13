"""SQLite persistence: short serializable writer transactions and schema versions."""
import sqlite3
from contextlib import contextmanager

from .parsing import Problem

SCHEMA_VERSION = 1
MIGRATIONS = {1: [
    '''CREATE TABLE tenants (tenant TEXT PRIMARY KEY)''',
    '''CREATE TABLE stock (
        tenant TEXT NOT NULL REFERENCES tenants(tenant), sku TEXT NOT NULL,
        warehouse TEXT NOT NULL, quantity INTEGER NOT NULL
        CHECK(typeof(quantity)='integer' AND quantity>=0),
        PRIMARY KEY(tenant,sku,warehouse))''',
    '''CREATE TABLE runs (
        tenant TEXT NOT NULL REFERENCES tenants(tenant), run_id TEXT NOT NULL,
        input BLOB NOT NULL, status TEXT NOT NULL CHECK(status IN ('interrupted','completed')),
        next_group INTEGER NOT NULL DEFAULT 0, applied_groups INTEGER NOT NULL DEFAULT 0,
        rejected_groups INTEGER NOT NULL DEFAULT 0, applied_rows INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(tenant,run_id))''',
    '''CREATE TABLE decisions (
        tenant TEXT NOT NULL, run_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
        group_id TEXT NOT NULL, reason TEXT,
        PRIMARY KEY(tenant,run_id,ordinal), UNIQUE(tenant,run_id,group_id),
        FOREIGN KEY(tenant,run_id) REFERENCES runs(tenant,run_id))''',
    '''CREATE TABLE transfers (
        tenant TEXT NOT NULL, run_id TEXT NOT NULL, transfer_id TEXT NOT NULL,
        ordinal INTEGER NOT NULL, row_number INTEGER NOT NULL, sku TEXT NOT NULL,
        from_warehouse TEXT NOT NULL, to_warehouse TEXT NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity>0 AND quantity<=1000000),
        PRIMARY KEY(tenant,run_id,transfer_id),
        FOREIGN KEY(tenant,run_id,ordinal) REFERENCES decisions(tenant,run_id,ordinal))'''
]}


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except BaseException:
        if db.in_transaction:
            db.execute('ROLLBACK')
        raise


def connect(path):
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        with transaction(db):
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version > SCHEMA_VERSION:
                raise Problem('conflict', 'database schema is newer than this application')
            for target in range(version + 1, SCHEMA_VERSION + 1):
                for statement in MIGRATIONS[target]:
                    db.execute(statement)
                db.execute(f'PRAGMA user_version={target}')
        return db
    except BaseException:
        db.close()
        raise


def report(db, tenant, run_id, replayed=False):
    row = db.execute('SELECT * FROM runs WHERE tenant=? AND run_id=?',
                     (tenant, run_id)).fetchone()
    errors = [dict(item) for item in db.execute(
        '''SELECT group_id,reason FROM decisions WHERE tenant=? AND run_id=?
           AND reason IS NOT NULL ORDER BY ordinal''', (tenant, run_id))]
    return {key: row[key] for key in
            ('run_id', 'status', 'applied_groups', 'rejected_groups', 'applied_rows')} | {
                'replayed': replayed, 'errors': errors}


def stock(db, tenant):
    return [dict(row) for row in db.execute(
        'SELECT sku,warehouse,quantity FROM stock WHERE tenant=? ORDER BY sku,warehouse',
        (tenant,))]


def runs(db, tenant):
    # Snapshot includes both aggregate counters and the matching errors.
    db.execute('BEGIN')
    try:
        result = [report(db, tenant, row[0]) for row in db.execute(
            'SELECT run_id FROM runs WHERE tenant=? ORDER BY run_id', (tenant,))]
        db.execute('COMMIT')
        return result
    except BaseException:
        db.execute('ROLLBACK')
        raise
