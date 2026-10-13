#!/usr/bin/env python3
"""Local TEST-auth sales ledger. Python standard library only."""
import argparse
import json
from pathlib import Path
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import uuid
from urllib.parse import urlsplit, unquote


class APIError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def connect(path):
    db = sqlite3.connect(path, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def migrate(path):
    db = connect(path)
    try:
        db.execute('BEGIN IMMEDIATE')
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version not in (0, 1, 2):
            raise RuntimeError('Unsupported database version')
        files = ('001_legacy.sql', '002_ledger.sql')
        for name in files[version:]:
            # executescript implicitly commits; execute individual migration statements
            # instead so every pending migration is in one atomic transaction.
            sql = (Path(__file__).parent / 'migrations' / name).read_text()
            for statement in sql.split(';'):
                if statement.strip():
                    db.execute(statement)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def text(value):
    return isinstance(value, str) and bool(value.strip())


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def shape(body, keys):
    if not isinstance(body, dict) or set(body) != set(keys):
        raise APIError(400, 'Invalid body fields')


def public(row, kind):
    keys = ('id', 'title', 'amount_cents', 'currency', 'status', 'version') if kind == 'deals' else (
        'id', 'deal_id', 'request_id', 'net_cents', 'tax_cents', 'total_cents', 'currency', 'status')
    return {key: row[key] for key in keys}


def lookup(db, kind, tenant, identifier):
    # Legacy numeric IDs remain numeric in responses, and addressable as URL text.
    row = db.execute(f'SELECT * FROM {kind} WHERE tenant=? AND CAST(id AS TEXT)=?',
                     (tenant, str(identifier))).fetchone()
    if row is None:
        raise APIError(404, 'Not found')
    return row


def event(db, tenant, action, resource):
    db.execute('INSERT INTO audit(tenant,action,resource_id) VALUES(?,?,?)',
               (tenant, action, resource))


def ledger(db, method, parts, tenant, role, body):
    if method == 'GET':
        if parts == ['audit']:
            return 200, [dict(r) for r in db.execute(
                'SELECT action,resource_id FROM audit WHERE tenant=? ORDER BY seq', (tenant,))]
        if len(parts) in (1, 2) and parts[0] in ('deals', 'invoices'):
            kind = parts[0]
            if len(parts) == 2:
                return 200, public(lookup(db, kind, tenant, parts[1]), kind)
            return 200, [public(r, kind) for r in db.execute(
                f'SELECT * FROM {kind} WHERE tenant=? ORDER BY rowid', (tenant,))]
        raise APIError(404, 'Not found')

    create_deal = method == 'POST' and parts == ['deals']
    patch = method == 'PATCH' and len(parts) == 2 and parts[0] == 'deals'
    issue = method == 'POST' and parts == ['invoices']
    void = method == 'POST' and len(parts) == 3 and parts[0] == 'invoices' and parts[2] == 'void'
    if not any((create_deal, patch, issue, void)):
        raise APIError(404, 'Not found')
    if role == 'viewer' or ((issue or void) and role != 'owner'):
        raise APIError(403, 'Forbidden')
    if create_deal:
        shape(body, ('title', 'amount_cents', 'currency'))
        if not text(body['title']) or not integer(body['amount_cents'], 0, 100000000) or body['currency'] not in ('EUR', 'USD'):
            raise APIError(400, 'Invalid deal')
        identifier = uuid.uuid4().hex
        db.execute('INSERT INTO deals VALUES(?,?,?,?,?,?,?)',
                   (identifier, tenant, body['title'], body['amount_cents'], body['currency'], 'new', 1))
        event(db, tenant, 'deal.created', identifier)
        return 201, public(lookup(db, 'deals', tenant, identifier), 'deals')
    if patch:
        shape(body, ('version', 'status'))
        if type(body['version']) is not int or body['version'] <= 0 or not isinstance(body['status'], str):
            raise APIError(400, 'Invalid transition body')
        deal = lookup(db, 'deals', tenant, parts[1])
        graph = {'new': ('qualified',), 'qualified': ('won', 'lost')}
        if body['version'] != deal['version'] or body['status'] not in graph.get(deal['status'], ()):
            raise APIError(409, 'Transition conflict')
        db.execute('UPDATE deals SET status=?,version=version+1 WHERE tenant=? AND id=?',
                   (body['status'], tenant, deal['id']))
        event(db, tenant, 'deal.transitioned', deal['id'])
        return 200, public(lookup(db, 'deals', tenant, parts[1]), 'deals')
    if issue:
        shape(body, ('deal_id', 'request_id', 'tax_bps'))
        if not (text(body['deal_id']) or type(body['deal_id']) is int) or not text(body['request_id']) or not integer(body['tax_bps'], 0, 10000):
            raise APIError(400, 'Invalid invoice')
        deal = lookup(db, 'deals', tenant, body['deal_id'])
        previous = db.execute('SELECT * FROM invoices WHERE tenant=? AND request_id=?',
                              (tenant, body['request_id'])).fetchone()
        if previous:
            if previous['deal_id'] != deal['id'] or previous['tax_bps'] != body['tax_bps']:
                raise APIError(409, 'Idempotency conflict')
            return 200, public(previous, 'invoices')
        if deal['status'] != 'won' or db.execute('SELECT 1 FROM invoices WHERE tenant=? AND deal_id=?', (tenant, deal['id'])).fetchone():
            raise APIError(409, 'Deal cannot be invoiced')
        identifier = uuid.uuid4().hex
        net = deal['amount_cents']
        tax = (net * body['tax_bps'] + 5000) // 10000
        db.execute('INSERT INTO invoices VALUES(?,?,?,?,?,?,?,?,?,?,NULL)',
                   (identifier, tenant, deal['id'], body['request_id'], body['tax_bps'], net, tax, net + tax, deal['currency'], 'issued'))
        event(db, tenant, 'invoice.issued', identifier)
        return 201, public(lookup(db, 'invoices', tenant, identifier), 'invoices')
    shape(body, ('reason',))
    if not text(body['reason']):
        raise APIError(400, 'Invalid reason')
    invoice = lookup(db, 'invoices', tenant, parts[1])
    if invoice['status'] != 'issued':
        raise APIError(409, 'Invoice already void')
    db.execute("UPDATE invoices SET status='void',void_reason=? WHERE tenant=? AND id=?",
               (body['reason'], tenant, invoice['id']))
    event(db, tenant, 'invoice.voided', invoice['id'])
    return 200, public(lookup(db, 'invoices', tenant, parts[1]), 'invoices')


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


class Server(ThreadingHTTPServer):
    request_queue_size = 64


class Handler(BaseHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        payload = json.dumps({'error': message or 'HTTP error'}).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(payload)

    def log_message(self, *args):
        pass

    def handle_api(self):
        db = None
        try:
            tokens = {f'{role}-{tenant}': (tenant, role) for tenant in ('a', 'b') for role in ('owner', 'editor', 'viewer')}
            identity = tokens.get(self.headers.get('Authorization', '').removeprefix('Bearer ')) if self.headers.get('Authorization', '').startswith('Bearer ') else None
            if identity is None:
                raise APIError(401, 'Unauthorized')
            body = None
            if self.command != 'GET':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 1048576 or self.headers.get('Transfer-Encoding'):
                        raise ValueError('Invalid body length')
                    body = json.loads(self.rfile.read(length).decode('utf-8'), object_pairs_hook=strict_object,
                                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Invalid JSON constant')))
                except (ValueError, UnicodeError):
                    raise APIError(400, 'Invalid JSON')
            parts = [unquote(p) for p in urlsplit(self.path).path.strip('/').split('/')]
            db = connect(self.server.db_path)
            db.execute('BEGIN' if self.command == 'GET' else 'BEGIN IMMEDIATE')
            status, data = ledger(db, self.command, parts, *identity, body)
            db.commit()
        except APIError as error:
            if db:
                db.rollback()
            status, data = error.status, {'error': error.message}
        except Exception:
            if db:
                db.rollback()
            status, data = 500, {'error': 'Internal server error'}
        finally:
            if db:
                db.close()
        payload = json.dumps(data, ensure_ascii=True).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(payload)

    do_GET = do_POST = do_PATCH = do_PUT = do_DELETE = do_OPTIONS = do_HEAD = handle_api


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    serve = sub.add_parser('serve')
    serve.add_argument('--db', required=True)
    serve.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    migrate(args.db)
    server = Server(('127.0.0.1', args.port), Handler)
    server.db_path = args.db
    print(json.dumps({'port': server.server_port}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
