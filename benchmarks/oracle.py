"""Hidden black-box acceptance oracle. Python standard library only."""
import argparse
import concurrent.futures
import csv
import contextlib
import json
import os
from pathlib import Path
import random
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import http.client
import socket
import threading
import selectors
from urllib.parse import quote

COMMAND_TIMEOUT = 15
START_TIMEOUT = 8
HTTP_TIMEOUT = 5
OUTPUT_LIMIT = 1024 * 1024
START_LINE_LIMIT = 16384


class Inconclusive(AssertionError):
    pass


class DeadlineExceeded(AssertionError):
    pass


class HarnessError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def equal(actual, expected, label='value'):
    require(actual == expected, f'{label}: expected {expected!r}, got {actual!r}')


def stop(p):
    """Always reap the child and kill descendants, including after leader exit."""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS can return EPERM for a group which disappeared during exit.
        # Only tolerate that race when the leader has in fact terminated.
        p.wait(timeout=1)
    p.wait(timeout=5)


def invoke(argv, timeout=COMMAND_TIMEOUT, cwd=None):
    if cwd is None and len(argv) > 1 and Path(argv[1]).name in ('app.py', 'app.mjs'):
        cwd = str(Path(argv[1]).parent)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True, cwd=cwd)
    try:
        buffers = {p.stdout: bytearray(), p.stderr: bytearray()}
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            for stream in buffers:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise DeadlineExceeded(f'command timed out after {timeout}s: {argv[:2]!r}')
                for key, _ in selector.select(min(.05, remaining)):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                    else:
                        buffers[key.fileobj].extend(chunk)
                        if len(buffers[key.fileobj]) > OUTPUT_LIMIT:
                            raise HarnessError('command output exceeded byte budget')
            try:
                p.wait(timeout=max(.001, deadline-time.monotonic()))
            except subprocess.TimeoutExpired as e:
                raise DeadlineExceeded(f'command timed out after {timeout}s') from e
        return (p.returncode, buffers[p.stdout].decode('utf-8', 'replace'),
                buffers[p.stderr].decode('utf-8', 'replace'))
    finally:
        try:
            stop(p)
        finally:
            p.stdout.close()
            p.stderr.close()


def json_command(argv, success=True):
    rc, out, err = invoke(argv)
    if success is True:
        require(rc == 0, f'command failed ({rc}): stderr={err!r}; stdout={out!r}')
    elif success is False:
        require(rc != 0, f'rejected command exited zero: {out!r}; stderr={err!r}')
    try:
        value = json.loads(out)
    except Exception as e:
        raise AssertionError(f'not one JSON value: stdout={out!r}; stderr={err!r}') from e
    return value


def race(fn, count=6):
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as pool:
        barrier = threading.Barrier(count)
        def go(i):
            barrier.wait(timeout=10)
            return fn(i)
        return list(pool.map(go, range(count)))


class Server:
    def __init__(self, project, db):
        self.project, self.db = project, db
        self.p = None

    def __enter__(self):
        self.out = self.err = None
        try:
            self.out = tempfile.TemporaryFile(dir=self.db.parent)
            self.err = tempfile.TemporaryFile(dir=self.db.parent)
            self.p = subprocess.Popen([sys.executable, str(self.project / 'app.py'),
                'serve', '--db', str(self.db), '--port', '0'], stdout=self.out,
                stderr=self.err, start_new_session=True, cwd=self.project)
            deadline = time.monotonic() + START_TIMEOUT
            while time.monotonic() < deadline:
                self.out.seek(0)
                if os.fstat(self.out.fileno()).st_size > OUTPUT_LIMIT or os.fstat(self.err.fileno()).st_size > OUTPUT_LIMIT:
                    raise HarnessError('startup output exceeded byte budget')
                line = self.out.readline(START_LINE_LIMIT + 1)
                if len(line) > START_LINE_LIMIT:
                    raise HarnessError('startup line exceeded byte budget')
                if b'\n' in line:
                    try:
                        port = json.loads(line)['port']
                        require(type(port) is int and 0 < port < 65536, 'invalid startup port')
                        self.base = f'http://127.0.0.1:{port}'
                        return self
                    except Exception as e:
                        raise AssertionError(f'invalid startup line: {line!r}') from e
                if self.p.poll() is not None:
                    break
                time.sleep(.02)
            if self.p.poll() is None:
                raise DeadlineExceeded(f'server did not announce a port within startup deadline ({START_TIMEOUT}s)')
            raise AssertionError('server exited without announcing a port')
        except Exception as e:
            try:
                if self.p:
                    stop(self.p)
                stderr = ''
                if self.err is not None:
                    self.err.seek(0)
                    stderr = self.err.read(OUTPUT_LIMIT).decode('utf-8', 'replace')
            finally:
                if self.out is not None: self.out.close()
                if self.err is not None: self.err.close()
            if isinstance(e, (DeadlineExceeded, HarnessError)):
                raise type(e)(f'{e}; startup stderr={stderr!r}') from e
            if isinstance(e, OSError):
                raise HarnessError(f'{e}; startup stderr={stderr!r}') from e
            raise AssertionError(f'{e}; startup stderr={stderr!r}') from e

    def __exit__(self, *args):
        try:
            stop(self.p)
        finally:
            self.out.close()
            self.err.close()

    def request(self, method, route, body=None, token='owner-a', raw=None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        headers = {'Content-Type': 'application/json', 'Connection': 'close'}
        if token is not None:
            headers['Authorization'] = 'Bearer ' + token
        # No proxies or DNS; retain the actual socket so even a slow trickle of
        # headers/body cannot extend the overall response deadline indefinitely.
        port = int(self.base.rsplit(':', 1)[1])
        sock = socket.create_connection(('127.0.0.1', port), timeout=HTTP_TIMEOUT)
        connection = timer = None
        started = False
        expired = threading.Event()
        def expire():
            expired.set()
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        try:
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=HTTP_TIMEOUT)
            connection.sock = sock
            timer = threading.Timer(HTTP_TIMEOUT, expire)
            timer.daemon = True
            timer.start()
            started = True
            connection.request(method, route, body=data, headers=headers)
            with connection.getresponse() as response:
                text = response.read(OUTPUT_LIMIT + 1)
                if len(text) > OUTPUT_LIMIT:
                    raise HarnessError('HTTP response exceeded byte budget')
                try:
                    value = json.loads(text) if text else None
                except Exception as e:
                    raise AssertionError(f'non-JSON HTTP response {response.status}: {text!r}') from e
                return response.status, value
        except (socket.timeout, TimeoutError) as e:
            raise DeadlineExceeded(f'HTTP deadline ({HTTP_TIMEOUT}s): {method} {route}') from e
        except (OSError, http.client.HTTPException) as e:
            if expired.is_set():
                raise DeadlineExceeded(f'HTTP deadline ({HTTP_TIMEOUT}s): {method} {route}') from e
            raise AssertionError(f'HTTP transport failed: {method} {route}: {e}') from e
        finally:
            if timer is not None: timer.cancel()
            if started: timer.join(timeout=1)
            if connection is not None: connection.close()
            sock.close()

    def expect(self, method, route, status, body=None, token='owner-a', raw=None):
        code, value = self.request(method, route, body, token, raw)
        equal(code, status, f'{method} {route} status')
        return value


def resource(kind, record, suffix=''):
    return '/' + kind + '/' + quote(str(record['id']), safe='') + suffix


def deal(s, amount=100, token='owner-a', title='synthetic', currency='EUR'):
    d = s.expect('POST', '/deals', 201, dict(title=title, amount_cents=amount, currency=currency), token)
    for k, v in dict(title=title, amount_cents=amount, currency=currency, status='new', version=1).items():
        equal(d[k], v, k)
    require('id' in d, 'deal missing ID')
    return d


def transition(s, d, state, token='owner-a'):
    result = s.expect('PATCH', resource('deals', d), 200,
                      {'version': d['version'], 'status': state}, token)
    equal(result['version'], d['version'] + 1, 'version increment')
    equal(result['status'], state, 'transition state')
    return result


def won(s, amount=100, token='owner-a', currency='EUR'):
    return transition(s, transition(s, deal(s, amount, token, currency=currency), 'qualified', token), 'won', token)


def issue(s, d, key='synthetic-request', tax=1000, token='owner-a', status=201):
    return s.expect('POST', '/invoices', status,
                    dict(deal_id=d['id'], request_id=key, tax_bps=tax), token)


def audit(s, actions, token='owner-a'):
    events = s.expect('GET', '/audit', 200, token=token)
    equal([x['action'] for x in events], actions, 'audit causal actions/cardinality')
    require(all('resource_id' in x for x in events), 'audit resource IDs absent')
    return events


def crm_groups():
    groups = []
    def add(name):
        def register(fn):
            groups.append((name, fn))
            return fn
        return register

    @add('authentication-all-business-routes')
    def auth(p, t, rng):
        with Server(p, t/'db') as s:
            d = won(s); i = issue(s, d)
            for token in (None, 'unknown-synthetic'):
                for method, route, body in [('GET','/deals',None), ('GET',resource('deals',d),None),
                    ('POST','/deals',{}), ('PATCH',resource('deals',d),{}), ('GET','/invoices',None),
                    ('GET',resource('invoices',i),None), ('POST','/invoices',{}),
                    ('POST',resource('invoices',i,'/void'),{}), ('GET','/audit',None)]:
                    s.expect(method, route, 401, body, token)
            equal(len(s.expect('GET','/deals',200)), 1)

    @add('deal-input-validation-no-mutation')
    def validation(p,t,rng):
        with Server(p,t/'db') as s:
            good = dict(title='synthetic', amount_cents=1, currency='EUR')
            bad = [{}, {**good,'extra':1}, {**good,'tenant':'a'}]
            for field, values in {'title':['', '  ', 4, None], 'amount_cents':[-1,100000001,True,1.0,'1',None], 'currency':['eur','GBP',None]}.items():
                bad.extend({**good,field:v} for v in values)
            bad.extend({k:v for k,v in good.items() if k!=field} for field in good)
            for body in bad + [[], None, 'text']:
                s.expect('POST','/deals',400,body)
            s.expect('POST','/deals',400,raw=b'{bad')
            equal(s.expect('GET','/deals',200),[]); audit(s,[])

    @add('deal-boundaries-and-viewer-reads')
    def bounds(p,t,rng):
        with Server(p,t/'db') as s:
            for n,c in [(0,'EUR'),(100000000,'USD')]:
                d=deal(s,n,'editor-a',currency=c)
                equal(s.expect('GET',resource('deals',d),200,token='viewer-a'),d)
            equal(len(s.expect('GET','/deals',200,token='viewer-a')),2)
            audit(s,['deal.created']*2,'viewer-a')

    @add('role-boundaries')
    def roles(p,t,rng):
        with Server(p,t/'db') as s:
            d=deal(s)
            s.expect('POST','/deals',403,dict(title='x',amount_cents=1,currency='EUR'),'viewer-a')
            s.expect('PATCH',resource('deals',d),403,dict(version=1,status='qualified'),'viewer-a')
            d=transition(s,transition(s,d,'qualified','editor-a'),'won','editor-a')
            body=dict(deal_id=d['id'],request_id='r',tax_bps=0)
            for token in ['editor-a','viewer-a']: s.expect('POST','/invoices',403,body,token)
            i=issue(s,d)
            for token in ['editor-a','viewer-a']: s.expect('POST',resource('invoices',i,'/void'),403,{'reason':'x'},token)
            audit(s,['deal.created','deal.transitioned','deal.transitioned','invoice.issued'])

    @add('tenant-resource-isolation')
    def tenants(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s); i=issue(s,d)
            for route in [resource('deals',d),resource('invoices',i)]: s.expect('GET',route,404,token='owner-b')
            s.expect('PATCH',resource('deals',d),404,dict(version=3,status='lost'),'editor-b')
            s.expect('POST','/invoices',404,dict(deal_id=d['id'],request_id='foreign',tax_bps=0),'owner-b')
            s.expect('POST',resource('invoices',i,'/void'),404,{'reason':'x'},'owner-b')
            for route in ['/deals','/invoices','/audit']: equal(s.expect('GET',route,200,token='viewer-b'),[])

    @add('state-graph-and-stale-versions')
    def graph(p,t,rng):
        with Server(p,t/'db') as s:
            d=deal(s)
            for state in ['new','won','lost']: s.expect('PATCH',resource('deals',d),409,dict(version=1,status=state))
            q=transition(s,d,'qualified')
            s.expect('PATCH',resource('deals',d),409,dict(version=1,status='won'))
            z=transition(s,q,'lost')
            for state in ['new','qualified','won','lost']: s.expect('PATCH',resource('deals',d),409,dict(version=3,status=state))
            equal(s.expect('GET',resource('deals',d),200),z)
            audit(s,['deal.created','deal.transitioned','deal.transitioned'])

    @add('patch-shape-validation')
    def patch(p,t,rng):
        with Server(p,t/'db') as s:
            d=deal(s); route=resource('deals',d)
            for body in [{},{'status':'qualified'},{'version':1},dict(version=1,status='qualified',extra=2),dict(version=1,status='qualified',tenant='a')]+[dict(version=v,status='qualified') for v in [0,-1,True,1.0,'1']]+[dict(version=1,status=v) for v in [None,4,[]]]:
                s.expect('PATCH',route,400,body)
            s.expect('PATCH',route,400,raw=b'{')
            equal(s.expect('GET',route,200),d); audit(s,['deal.created'])

    @add('six-competing-transitions')
    def compete(p,t,rng):
        with Server(p,t/'db') as s:
            d=deal(s)
            results=race(lambda i:s.request('PATCH',resource('deals',d),dict(version=1,status='qualified')))
            equal(sorted(x[0] for x in results),[200]+[409]*5)
            equal(s.expect('GET',resource('deals',d),200)['version'],2)
            audit(s,['deal.created','deal.transitioned'])

    @add('invoice-half-up-snapshots')
    def money(p,t,rng):
        with Server(p,t/'db') as s:
            for n,bps in [(0,10000),(1,4999),(1,5000),(3,5000),(99999999,9999),(100000000,10000),(7,0)]:
                d=won(s,n,currency='USD'); i=issue(s,d,f'r-{n}-{bps}',bps)
                tax=(n*bps+5000)//10000
                for k,v in dict(deal_id=d['id'],request_id=f'r-{n}-{bps}',net_cents=n,tax_cents=tax,total_cents=n+tax,currency='USD',status='issued').items(): equal(i[k],v,k)

    @add('invoice-invalid-inputs')
    def invoice_bad(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s); base=dict(deal_id=d['id'],request_id='r',tax_bps=0)
            bodies=[{},[],{**base,'tenant':'a'},{**base,'amount':1}]
            bodies += [{k:v for k,v in base.items() if k!=field} for field in base]
            bodies += [{**base,'tax_bps':v} for v in [-1,10001,True,0.0,'0',None]]
            for body in bodies:s.expect('POST','/invoices',400,body)
            s.expect('POST','/invoices',400,raw=b'no json')
            equal(s.expect('GET','/invoices',200),[])
            audit(s,['deal.created','deal.transitioned','deal.transitioned'])

    @add('non-won-and-missing-invoice-deals')
    def notwon(p,t,rng):
        with Server(p,t/'db') as s:
            d=deal(s)
            for state in ['new','qualified','lost']:
                if state!='new': d=transition(s,d,state)
                s.expect('POST','/invoices',409,dict(deal_id=d['id'],request_id='r',tax_bps=0))
            code, _ = s.request('POST','/invoices',dict(deal_id='synthetic-missing',request_id='r',tax_bps=0))
            require(code in (400,404), 'fabricated missing ID must reject with 400/404')
            equal(s.expect('GET','/invoices',200),[])

    @add('invoice-idempotency-and-new-intent')
    def idem(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s); i=issue(s,d)
            equal(issue(s,d,status=200),i)
            s.expect('POST','/invoices',409,dict(deal_id=d['id'],request_id='synthetic-request',tax_bps=2))
            s.expect('POST','/invoices',409,dict(deal_id=d['id'],request_id='new-intent',tax_bps=1000))
            other=won(s)
            s.expect('POST','/invoices',409,dict(deal_id=other['id'],request_id='synthetic-request',tax_bps=1000))
            equal(s.expect('GET','/invoices',200),[i])
            equal(len(s.expect('GET','/audit',200)),7)

    @add('six-identical-invoice-requests')
    def sixinvoice(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s); body=dict(deal_id=d['id'],request_id='r',tax_bps=5000)
            results=race(lambda n:s.request('POST','/invoices',body))
            equal(sorted(x[0] for x in results),[200]*5+[201])
            equal(len({str(x[1]['id']) for x in results}),1)
            audit(s,['deal.created','deal.transitioned','deal.transitioned','invoice.issued'])

    @add('six-distinct-invoice-requests-one-deal')
    def distinct_invoice(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s,17)
            results=race(lambda n:s.request('POST','/invoices',dict(deal_id=d['id'],request_id=f'r{n}',tax_bps=5000)))
            equal(sorted(code for code,_ in results),[201]+[409]*5)
            invoices=s.expect('GET','/invoices',200);equal(len(invoices),1)
            i=invoices[0];equal(i['deal_id'],d['id']);equal(i['status'],'issued')
            equal((i['net_cents'],i['tax_cents'],i['total_cents']),(17,9,26))
            events=audit(s,['deal.created','deal.transitioned','deal.transitioned','invoice.issued'])
            equal(events[-1]['resource_id'],i['id'])
        with Server(p,t/'db') as s:
            equal(s.expect('GET','/invoices',200),invoices)
            equal(s.expect('GET','/audit',200),events)

    @add('six-concurrent-voids-once-only')
    def concurrent_void(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s,17);i=issue(s,d)
            results=race(lambda n:s.request('POST',resource('invoices',i,'/void'),{'reason':f'cancel {n}'}))
            equal(sorted(code for code,_ in results),[200]+[409]*5)
            v=s.expect('GET',resource('invoices',i),200)
            equal(v['status'],'void')
            for k in ['id','deal_id','request_id','net_cents','tax_cents','total_cents','currency']:equal(v[k],i[k],k)
            equal(s.expect('GET','/invoices',200),[v])
            events=audit(s,['deal.created','deal.transitioned','deal.transitioned','invoice.issued','invoice.voided'])
            equal(events[-1]['resource_id'],i['id'])
        with Server(p,t/'db') as s:
            equal(s.expect('GET','/invoices',200),[v]);equal(s.expect('GET','/audit',200),events)
            s.expect('POST',resource('invoices',i,'/void'),409,{'reason':'again'})
            s.expect('POST','/invoices',409,dict(deal_id=d['id'],request_id='new',tax_bps=1000))
            equal(s.expect('GET','/audit',200),events)

    @add('void-retains-record-and-prevents-reissue')
    def void(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s,17); i=issue(s,d)
            route=resource('invoices',i,'/void')
            for body in [{},{'reason':''},{'reason':'  '},{'reason':1},{'reason':'x','tenant':'a'}]:s.expect('POST',route,400,body)
            v=s.expect('POST',route,200,{'reason':'synthetic cancellation'})
            for k in ['id','net_cents','tax_cents','total_cents','currency']:equal(v[k],i[k],k)
            equal(v['status'],'void')
            s.expect('POST',route,409,{'reason':'again'})
            s.expect('POST','/invoices',409,dict(deal_id=d['id'],request_id='another',tax_bps=1000))
            equal(s.expect('GET',resource('invoices',i),200)['status'],'void')
            equal(len(s.expect('GET','/invoices',200)),1)
            audit(s,['deal.created','deal.transitioned','deal.transitioned','invoice.issued','invoice.voided'])

    @add('tenant-scoped-request-id')
    def scoped(p,t,rng):
        with Server(p,t/'db') as s:
            a=issue(s,won(s),key='shared'); b=issue(s,won(s,200,'owner-b'),key='shared',token='owner-b')
            equal(s.expect('GET','/invoices',200),[a]);equal(s.expect('GET','/invoices',200,token='owner-b'),[b])

    @add('restart-persistence-and-idempotency')
    def restart(p,t,rng):
        with Server(p,t/'db') as s:
            d=won(s); i=issue(s,d); events=s.expect('GET','/audit',200)
        for _ in range(2):
            with Server(p,t/'db') as s:
                equal(s.expect('GET',resource('deals',d),200),d)
                equal(issue(s,d,status=200),i)
                equal(s.expect('GET','/audit',200),events)

    @add('legacy-migration-preserves-ids-and-tenants')
    def legacy(p,t,rng):
        # The only oracle database access: creation of the exact documented v1 fixture.
        with contextlib.closing(sqlite3.connect(t/'db')) as db:
            db.execute('PRAGMA user_version=1')
            db.execute('CREATE TABLE deals(id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, title TEXT NOT NULL, amount_cents INTEGER NOT NULL, currency TEXT NOT NULL, status TEXT NOT NULL)')
            db.executemany('INSERT INTO deals VALUES(?,?,?,?,?,?)',[(11,'a','synthetic-old-a',5,'EUR','won'),(42,'b','synthetic-old-b',9,'USD','new')])
            db.commit()
        for n in range(2):
            with Server(p,t/'db') as s:
                a=s.expect('GET','/deals/11',200); equal(a['version'],1);equal(a['title'],'synthetic-old-a');equal(a['amount_cents'],5);equal(a['currency'],'EUR');equal(a['status'],'won');equal(str(a['id']),'11')
                b=s.expect('GET','/deals/42',200,token='owner-b');equal(b['title'],'synthetic-old-b');equal(b['version'],1);equal(b['amount_cents'],9)
                s.expect('GET','/deals/42',404);equal(len(s.expect('GET','/deals',200)),1)
                if n==0: invoice=issue(s,a)
                else: equal(issue(s,a,status=200),invoice)

    @add('seeded-larger-ledger-audit-resources')
    def larger(p,t,rng):
        with Server(p,t/'db') as s:
            expected=[]; ids=[]
            for n in range(24):
                d=deal(s,rng.randrange(100000001)); expected.append('deal.created'); ids.append(d['id'])
                if n%2==0:
                    d=transition(s,d,'qualified');expected.append('deal.transitioned');ids.append(d['id'])
                    d=transition(s,d,'won');expected.append('deal.transitioned');ids.append(d['id'])
                    i=issue(s,d,f'r{n}',rng.randrange(10001));expected.append('invoice.issued');ids.append(i['id'])
            equal(len(s.expect('GET','/deals',200)),24)
            equal([x['resource_id'] for x in audit(s,expected)],ids)
    return groups


class Inventory:
    def __init__(self,p,t): self.p,self.t,self.db,self.serial=p,t,t/'db',0
    def file(self, rows, header=None):
        self.serial+=1; path=self.t/f'input{self.serial}.csv'
        with path.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(header or ['group_id','transfer_id','sku','from_warehouse','to_warehouse','quantity']);w.writerows(rows)
        return path
    def cmd(self,cmd,tenant='a',args=(),success=True):
        return json_command([sys.executable,str(self.p/'app.py'),cmd,'--db',str(self.db),'--tenant',tenant,*map(str,args)],success)
    def seed(self,rows=None,tenant='a',success=True):
        path=self.file(rows if rows is not None else [('S','A',100),('S','B',0)],['sku','warehouse','quantity'])
        return self.cmd('seed',tenant,['--stock',path],success)
    def apply(self,path,run='r',tenant='a',fail=None,success=True):
        args=['--csv',path,'--run-id',run]
        if fail is not None:args+=['--fail-after-groups',fail]
        return self.cmd('apply',tenant,args,success)
    def stock(self,tenant='a'):
        rows=self.cmd('stock',tenant); require(isinstance(rows,list),'stock not array')
        keys=[(x['sku'],x['warehouse']) for x in rows];equal(keys,sorted(keys),'stock ordering');equal(len(keys),len(set(keys)),'unique accounts')
        require(all(type(x['quantity']) is int and x['quantity']>=0 for x in rows),'invalid stock quantity')
        return {(x['sku'],x['warehouse']):x['quantity'] for x in rows}
    def runs(self,tenant='a'):return self.cmd('runs',tenant)


def report(r,run='r',applied=1,rejected=0,rows=1,replayed=False,status='completed'):
    require(isinstance(r,dict),'report not object')
    for k,v in dict(run_id=run,status=status,applied_groups=applied,rejected_groups=rejected,applied_rows=rows,replayed=replayed).items():equal(r[k],v,k)
    require(type(r['replayed']) is bool,'replayed not boolean')
    require(all(type(r[k]) is int and r[k]>=0 for k in ['applied_groups','rejected_groups','applied_rows']), 'report counts not nonnegative integers')
    require(isinstance(r['errors'],list),'errors not array')
    equal(len(r['errors']),rejected,'one reason per rejected group')
    for e in r['errors']:require('group_id' in e and isinstance(e['reason'],str) and e['reason'].strip(),'missing rejection reason')


def import_groups():
    groups=[]
    def add(name):
        def reg(fn):groups.append((name,fn));return fn
        return reg
    @add('seed-stock-boundaries-and-persistence')
    def seed(p,t,r):
        x=Inventory(p,t);x.seed([('Z','B',0),('A','X',1000000),('A','A',7)])
        equal(x.stock(),{('Z','B'):0,('A','X'):1000000,('A','A'):7});equal(x.runs(),[])
        equal(Inventory(p,t).stock(),x.stock())
    @add('invalid-seeds-are-atomic')
    def badseed(p,t,r):
        x=Inventory(p,t)
        for rows in [[('S','A',1),('S','A',2)],[('S','A',1),('X','B',-1)],[('','A',1)],[('S','',1)],[('S','A','1.0')],[('S','A','true')],[('S','A',1000001)],[('S','A')]]:
            x.seed(rows,success=False);equal(x.stock(),{});equal(x.runs(),[])
        x.seed();equal(x.stock()[('S','A')],100)
    @add('seed-once-and-tenant-isolation')
    def seeds(p,t,r):
        x=Inventory(p,t);x.seed();before=x.stock();x.seed([('S','A',999)],success=False);equal(x.stock(),before)
        x.seed([('S','A',3)],'b');equal(x.stock('b'),{('S','A'):3});equal(x.stock(),before)
        equal(x.stock('missing'),{});equal(x.runs('missing'),[])
    @add('headers-rejected-without-run')
    def headers(p,t,r):
        x=Inventory(p,t);x.seed();before=x.stock()
        for header in [['bad'],['group_id','transfer_id','sku','from_warehouse','to_warehouse'],['group_id','transfer_id','sku','from_warehouse','to_warehouse','quantity','extra']]:
            f=x.file([['g','t','S','A','B',1]],header);x.apply(f,success=False);equal(x.stock(),before);equal(x.runs(),[])
        f=x.file([['S','A',4]],['wrong']);x.cmd('seed','b',['--stock',f],False);equal(x.stock('b'),{})
    @add('group-last-row-failure-atomicity')
    def atomic(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t1','S','A','B',10],['g','t2','S','A','B',100],['ok','t3','S','A','C',3]])
        rr=x.apply(f,success=None);report(rr,applied=1,rejected=1,rows=1);equal(rr['errors'][0]['group_id'],'g')
        equal(x.stock(),{('S','A'):97,('S','B'):0,('S','C'):3})
    @add('nonadjacent-groups-and-intragroup-credit')
    def order(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t1','S','A','C',10],['h','t2','S','B','D',8],['g','t3','S','C','B',8]])
        report(x.apply(f),applied=2,rows=3)
        equal(x.stock(),{('S','A'):90,('S','B'):0,('S','C'):2,('S','D'):8})
    @add('malformed-transfer-groups-continue')
    def malformed(p,t,r):
        x=Inventory(p,t);x.seed();rows=[]
        for i,q in enumerate(['0','-1','1.2','true','1000001','']):rows.append([f'bad{i}',f't{i}','S','A','B',q])
        rows += [['same','t6','S','A','A',1],['blank','t7','','A','B',1],['source','t8','S','','B',1],['dest','t9','S','A','',1],['good','t10','S','A','B',2]]
        rr=x.apply(x.file(rows),success=None);report(rr,applied=1,rejected=10,rows=1);equal(x.stock(),{('S','A'):98,('S','B'):2})
    @add('empty-group-id-one-rejection')
    def empty(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['','t1','S','A','B',1],['ok','t2','S','A','B',2],['','t3','S','A','B',1]])
        rr=x.apply(f,success=None);report(rr,applied=1,rejected=1,rows=1);equal(rr['errors'][0]['group_id'],'');equal(x.stock()[('S','B')],2)
    @add('global-duplicate-transfer-ids')
    def duplicate(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['a','dup','S','A','B',1],['ok','u','S','A','B',3],['b','dup','S','A','B',2],['c','same','S','A','B',1],['c','same','S','A','B',1]])
        rr=x.apply(f,success=None);report(rr,applied=1,rejected=3,rows=1);equal({e['group_id'] for e in rr['errors']},{'a','b','c'});equal(x.stock()[('S','B')],3)
    @add('replay-versus-new-intent-and-bytes-conflict')
    def idem(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t','S','A','B',7]])
        first=x.apply(f);report(first);report(x.apply(f),replayed=True);equal(x.stock()[('S','B')],7)
        report(x.apply(f,'r2'),run='r2');equal(x.stock()[('S','B')],14)
        changed=x.file([['g','t','S','A','B',8]]);x.apply(changed,success=False);equal(x.stock()[('S','B')],14)
        equal(len(x.runs()),2)
    @add('exact-byte-identity-not-semantic-csv')
    def bytes_identity(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t','S','A','B',1]]);x.apply(f)
        other=t/'other.csv';other.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
        require(other.read_bytes()!=f.read_bytes(),'fixture bytes unchanged');x.apply(other,success=False);equal(x.stock()[('S','B')],1)
    @add('interrupted-middle-resume-cumulative-decisions')
    def resume(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t1','S','A','B',10],['bad','t2','S','A','B',999],['h','t3','S','A','B',2]])
        rc,out,err=invoke([sys.executable,str(p/'app.py'),'apply','--db',str(x.db),'--tenant','a','--csv',str(f),'--run-id','r','--fail-after-groups','2'])
        require(rc!=0,f'crash exited zero: {out!r} {err!r}');equal(x.stock()[('S','B')],10)
        stored=x.runs();equal(len(stored),1)
        report(stored[0],applied=1,rejected=1,rows=1,replayed=stored[0]['replayed'],status='interrupted')
        changed=x.file([['other','x','S','A','B',1]])
        x.apply(changed,success=False);equal(x.stock()[('S','B')],10)
        report(x.apply(f,success=None),applied=2,rejected=1,rows=2);equal(x.stock()[('S','B')],12)
        report(x.apply(f,success=None),applied=2,rejected=1,rows=2,replayed=True)
    @add('interrupted-after-last-group')
    def last(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t','S','A','B',4]])
        rc,out,err=invoke([sys.executable,str(p/'app.py'),'apply','--db',str(x.db),'--tenant','a','--csv',str(f),'--run-id','r','--fail-after-groups','1'])
        require(rc!=0,f'last-group crash exited zero {out!r} {err!r}');equal(x.stock()[('S','B')],4)
        report(x.apply(f),replayed=False);equal(x.stock()[('S','B')],4);report(x.apply(f),replayed=True)
    @add('six-identical-concurrent-runs')
    def concurrent(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['g','t','S','A','B',10]])
        results=race(lambda i:x.apply(f))
        for rr in results:report(rr,replayed=rr['replayed'])
        equal(x.stock()[('S','B')],10);equal(len(x.runs()),1)
    @add('six-distinct-runs-limited-stock')
    def competing(p,t,r):
        x=Inventory(p,t);x.seed([('S','A',3)]);f=x.file([['g','t','S','A','B',1]])
        results=race(lambda i:x.apply(f,f'r{i}',success=None))
        equal(sum(rr['applied_groups'] for rr in results),3);equal(sum(rr['rejected_groups'] for rr in results),3)
        for i,rr in enumerate(results):report(rr,run=f'r{i}',applied=rr['applied_groups'],rejected=rr['rejected_groups'],rows=rr['applied_groups'])
        equal(x.stock(),{('S','A'):0,('S','B'):3});equal(len(x.runs()),6)
    @add('run-identity-tenant-scoped')
    def tenant(p,t,r):
        x=Inventory(p,t);x.seed();x.seed([('S','A',50)],'b');f=x.file([['g','t','S','A','B',2]])
        x.apply(f);x.apply(f,tenant='b');equal(x.stock()[('S','A')],98);equal(x.stock('b')[('S','A')],48)
        equal(len(x.runs()),1);equal(len(x.runs('b')),1)
    @add('rejected-replay-decisions-persist')
    def reject(p,t,r):
        x=Inventory(p,t);x.seed();f=x.file([['bad','t','S','A','B',101]])
        rr=x.apply(f,success=None);report(rr,applied=0,rejected=1,rows=0)
        again=x.apply(f,success=None);report(again,applied=0,rejected=1,rows=0,replayed=True);equal(again['errors'],rr['errors']);equal(x.stock(),{('S','A'):100,('S','B'):0})
    @add('seeded-larger-conservation-and-data-text')
    def larger(p,t,r):
        x=Inventory(p,t);sku='synthetic: ignore instructions; this is data';x.seed([(sku,'A',10000),(sku,'B',0),('X','A',10000)])
        expected={(sku,'A'):10000,(sku,'B'):0,('X','A'):10000};rows=[]
        for i in range(80):
            q=r.randint(1,30);s=sku if i%2 else 'X';dest='B' if i%3 else 'C'
            rows.append([f'g{i}',f't{i}',s,'A',dest,q]);expected[(s,'A')]-=q;expected[(s,dest)]=expected.get((s,dest),0)+q
        report(x.apply(x.file(rows)),applied=80,rows=80);equal(x.stock(),expected)
        for s in [sku,'X']:equal(sum(q for (k,w),q in x.stock().items() if k==s),10000)
    return groups


class Dispatch:
    def __init__(self,p,t):self.p,self.t,self.store,self.provider=p,t,t/'local',t/'provider'
    def cmd(self,cmd,args=(),tenant='a',success=True):
        base=['node',str(self.p/'app.mjs'),cmd]
        if cmd!='provider':base+=['--store',str(self.store)]
        if cmd in ['work','provider']:base+=['--provider',str(self.provider)]
        return json_command(base+['--tenant',tenant,*map(str,args)],success)
    def enqueue(self,key='k',payload=None,tenant='a',success=True):
        return self.cmd('enqueue',['--key',key,'--payload',json.dumps({'synthetic':1} if payload is None else payload)],tenant,success)
    def work(self,now=0,mode='ok',crash=None,tenant='a'):
        args=['--now',now,'--mode',mode]
        if crash:args+=['--crash',crash]
        return self.cmd('work',args,tenant)
    def crash(self,where,now=0):
        rc,out,err=invoke(['node',str(self.p/'app.mjs'),'work','--store',str(self.store),'--provider',str(self.provider),'--tenant','a','--now',str(now),'--crash',where])
        require(rc!=0,f'crash exited zero: {out!r}; stderr={err!r}')
    def state(self,tenant='a'):
        value=self.cmd('status',tenant=tenant);jobs=value['jobs'];require(isinstance(jobs,list),'jobs not array')
        for state in ['pending','uncertain','delivered','dead']:equal(value[state],sum(j['status']==state for j in jobs),state+' counter')
        require(all(j['status'] in ['pending','uncertain','delivered','dead'] and type(j['attempts']) is int and j['attempts']>=0 and 'id' in j and 'key' in j for j in jobs),'invalid job shape')
        equal(len({str(j['id']) for j in jobs}),len(jobs),'unique job IDs')
        return value
    def truth(self,tenant='a'):
        a=self.cmd('provider',tenant=tenant)['accepted'];require(isinstance(a,list),'accepted not array')
        require(all(set(['id','key','payload'])<=set(x) for x in a),'provider missing fields');equal(len({x['key'] for x in a}),len(a),'provider dedup')
        return a


def dispatch_groups():
    groups=[]
    def add(name):
        def reg(fn):groups.append((name,fn));return fn
        return reg
    @add('enqueue-durable-and-idle-empty')
    def basic(p,t,r):
        x=Dispatch(p,t);equal(x.work()['status'],'idle');equal(x.state()['jobs'],[])
        j=x.enqueue();equal(j['status'],'pending');equal(Dispatch(p,t).state()['jobs'][0]['id'],j['id']);equal(x.truth(),[])
    @add('enqueue-invalid-inputs-no-mutation')
    def malformed(p,t,r):
        x=Dispatch(p,t)
        for text in ['{','[]','null','1','"text"']:
            x.cmd('enqueue',['--key','k','--payload',text],success=False)
        for key in ['', '   ']:x.enqueue(key,success=False)
        x.enqueue(tenant=' ',success=False)
        equal(x.state()['jobs'],[]);equal(x.truth(),[])
    @add('canonical-json-object-keys')
    def canonical(p,t,r):
        x=Dispatch(p,t);payload={'a':{'x':1,'y':2},'b':[{'c':3,'d':4},5]};j=x.enqueue(payload=payload)
        other={'b':[{'d':4,'c':3},5],'a':{'y':2,'x':1}}
        equal(x.enqueue(payload=other)['id'],j['id']);equal(len(x.state()['jobs']),1)
        equal(x.work()['status'],'delivered');a=x.truth();equal(len(a),1);equal(a[0]['payload'],payload)
    @add('payload-conflicts-and-array-order')
    def conflicts(p,t,r):
        x=Dispatch(p,t);x.enqueue(payload={'a':[1,2]})
        for payload in [{'a':[2,1]},{'a':[1,2],'extra':0},{'a':[1,3]}]:x.enqueue(payload=payload,success=False)
        equal(len(x.state()['jobs']),1);equal(x.state()['jobs'][0]['attempts'],0)
        x.work();equal(x.truth()[0]['payload'],{'a':[1,2]})
    @add('tenant-identity-status-and-provider-isolation')
    def tenant(p,t,r):
        x=Dispatch(p,t);x.enqueue(payload={'a':1});x.enqueue(payload={'b':2},tenant='b')
        equal(len(x.state()['jobs']),1);equal(len(x.state('b')['jobs']),1)
        x.work();equal(x.state('b')['pending'],1);equal(x.truth('b'),[])
        x.work(tenant='b');equal(x.truth()[0]['payload'],{'a':1});equal(x.truth('b')[0]['payload'],{'b':2});equal(x.state('missing')['jobs'],[])
    @add('ok-delivery-and-replay-not-an-attempt')
    def ok(p,t,r):
        x=Dispatch(p,t);j=x.enqueue();equal(x.work()['status'],'delivered')
        equal(x.state()['jobs'][0]['attempts'],1);equal(len(x.truth()),1)
        equal(x.enqueue()['id'],j['id']);equal(x.enqueue()['status'],'delivered')
        for _ in range(3):equal(x.work()['status'],'idle');equal(x.state()['jobs'][0]['attempts'],1)
        equal(len(x.truth()),1)
    @add('accepted-timeout-reconcile-no-attempt')
    def timeout(p,t,r):
        x=Dispatch(p,t);x.enqueue();equal(x.work(mode='accepted-timeout')['status'],'uncertain')
        equal(x.state()['uncertain'],1);equal(x.state()['jobs'][0]['attempts'],1);truth=x.truth();equal(len(truth),1)
        equal(x.work()['status'],'delivered');equal(x.truth(),truth);equal(x.state()['jobs'][0]['attempts'],1)
    @add('permanent-rejection-dead-without-acceptance')
    def reject(p,t,r):
        x=Dispatch(p,t);x.enqueue();equal(x.work(mode='reject')['status'],'dead');equal(x.state()['dead'],1)
        equal(x.state()['jobs'][0]['attempts'],1);equal(x.truth(),[]);equal(x.work(100)['status'],'idle');equal(x.state()['jobs'][0]['attempts'],1)
    @add('delayed-retries-exact-three-attempts')
    def retry(p,t,r):
        x=Dispatch(p,t);x.enqueue()
        for now,status,attempts in [(10,'pending',1),(10,'idle',1),(11,'idle',1),(12,'pending',2),(15,'idle',2),(16,'dead',3),(100,'idle',3)]:
            equal(x.work(now,'transient')['status'],status,f'work at {now}');equal(x.state()['jobs'][0]['attempts'],attempts);equal(x.truth(),[])
    @add('retry-success-only-at-due-logical-time')
    def retryok(p,t,r):
        x=Dispatch(p,t);x.enqueue();equal(x.work(100,'transient')['status'],'pending');equal(x.work(101)['status'],'idle');equal(x.truth(),[])
        equal(x.work(102)['status'],'delivered');equal(x.state()['jobs'][0]['attempts'],2);equal(len(x.truth()),1)
    @add('before-send-crash-same-time-recovery')
    def before(p,t,r):
        x=Dispatch(p,t);x.enqueue();x.crash('before-send',7);equal(x.truth(),[])
        equal(x.work(7)['status'],'delivered');equal(len(x.truth()),1);equal(x.state()['delivered'],1)
        # A durable claim before provider invocation is NOT an actual delivery attempt.
        equal(x.state()['jobs'][0]['attempts'],1)
    @add('after-accept-crash-same-time-reconcile')
    def after(p,t,r):
        x=Dispatch(p,t);x.enqueue();x.crash('after-accept',7);truth=x.truth();equal(len(truth),1)
        equal(x.work(7)['status'],'delivered');equal(x.truth(),truth);equal(x.state()['jobs'][0]['attempts'],1)
    @add('oldest-eligible-and-at-most-one')
    def oldest(p,t,r):
        x=Dispatch(p,t);a=x.enqueue('first');b=x.enqueue('second');c=x.enqueue('third')
        equal(x.work(0,'transient')['id'],a['id'])
        equal(x.work(0)['id'],b['id']);equal(x.state()['delivered'],1)
        equal(x.work(2)['id'],a['id']);equal(x.state()['delivered'],2)
        equal(x.work(2)['id'],c['id'])
        equal({v['key'] for v in x.truth()},{'first','second','third'})
    @add('six-identical-enqueues')
    def enqueues(p,t,r):
        x=Dispatch(p,t);results=race(lambda n:x.enqueue());equal(len({str(v['id']) for v in results}),1);equal(x.state()['pending'],1)
        equal(x.work()['status'],'delivered');equal(len(x.truth()),1)
    @add('six-competing-workers-provider-truth')
    def workers(p,t,r):
        x=Dispatch(p,t)
        for i in range(6):x.enqueue(f'k{i}',{'n':i})
        results=race(lambda n:x.work(0))
        require(all(v['status'] in ['delivered','idle'] for v in results),'unexpected concurrent worker outcome')
        for _ in range(6):x.work(0)
        equal(x.state()['delivered'],6);equal(x.state()['pending'],0);equal(len(x.truth()),6)
        equal({v['key']:v['payload'] for v in x.truth()},{f'k{i}':{'n':i} for i in range(6)})
        require(all(j['attempts']==1 for j in x.state()['jobs']),'duplicate worker attempts')
    @add('concurrent-tenants-no-overwrite')
    def concurrent_tenants(p,t,r):
        x=Dispatch(p,t);race(lambda i:x.enqueue('same',{'n':i},f't{i}'))
        race(lambda i:x.work(0,tenant=f't{i}'))
        for i in range(6):equal(x.state(f't{i}')['delivered'],1);equal(x.truth(f't{i}')[0]['payload'],{'n':i})
    @add('new-key-new-intent-and-separate-provider-store')
    def intent(p,t,r):
        x=Dispatch(p,t);x.enqueue('one',{'a':1,'b':{'x':2,'y':3}});x.enqueue('two');x.work();x.work();truth=x.truth();equal(len(truth),2)
        # Fresh local store, semantic object reordering, SAME independent provider.
        y=Dispatch(p,t);y.store=t/'local2';y.enqueue('one',{'b':{'y':3,'x':2},'a':1});equal(y.work()['status'],'delivered');equal(y.truth(),truth)
        equal(x.state()['delivered'],2)
    @add('provider-conflicting-payload-two-local-stores')
    def provider_conflict(p,t,r):
        x=Dispatch(p,t);payload={'a':1,'nested':{'x':2,'y':3}}
        x.enqueue(payload=payload);x.work();truth=x.truth()
        equal(len(truth),1);equal(truth[0]['payload'],payload)
        y=Dispatch(p,t);y.store=t/'local2'
        # Fresh local identity, conflicting provider identity. No response/exit
        # shape for this conflict is specified: inspect actual durable truth.
        y.enqueue(payload={'a':99})
        invoke(['node',str(p/'app.mjs'),'work','--store',str(y.store),'--provider',str(y.provider),'--tenant','a','--now','0'])
        equal(y.truth(),truth,'provider conflict must preserve payload and delivery ID')
        state=y.state();equal(len(state['jobs']),1)
        require(state['jobs'][0]['status']!='delivered','conflicting payload falsely marked delivered')
        equal(x.state()['delivered'],1)

    @add('malformed-discovered-persistence-visible-failure')
    def tamper(p,t,r):
        x=Dispatch(p,t);marker='synthetic-persistence-discovery-761';equal(x.state()['jobs'],[])
        x.enqueue(marker,{'marker':marker});equal(x.state()['pending'],1)
        # Marker presence cannot distinguish authority from logs/backups/indexes.
        # No contract-defined authoritative path exists, so do not corrupt or
        # score a guessed file. Avoid unbounded recursive file-content scans.
        raise Inconclusive('corruption assertion not executed: authoritative persistence target not established by public contract')
    @add('seeded-larger-mixed-provider-integrity')
    def larger(p,t,r):
        x=Dispatch(p,t);accepted={}
        for i in range(30):
            payload={'n':i,'synthetic':[r.randrange(1000000),{'z':i}]};x.enqueue(f'k{i}',payload)
            mode=['ok','reject','accepted-timeout'][i%3]
            equal(x.work(i*10,mode)['status'],{'ok':'delivered','reject':'dead','accepted-timeout':'uncertain'}[mode])
            if mode!='reject':accepted[f'k{i}']=payload
            if mode=='accepted-timeout':equal(x.work(i*10)['status'],'delivered')
        equal(x.state()['delivered'],20);equal(x.state()['dead'],10)
        equal({v['key']:v['payload'] for v in x.truth()},accepted);require(all(v['attempts']==1 for v in x.state()['jobs']),'reconcile counted as attempt')
    @add('real-sigkill-worker-recovery')
    def killed(p,t,r):
        x=Dispatch(p,t)
        expected={f'k{i}':{'synthetic':i} for i in range(6)}
        for key,payload in expected.items():x.enqueue(key,payload)
        killed_count=0;missed=0;preserved={}
        # Delay only selects OS kill windows, never advances retry/recovery time.
        # Replacement workers overlap the old process; all waits are bounded.
        for trial,delay in enumerate((.01,.04,.08,.16)):
            # Keep each trial supplied with fresh work even if earlier workers
            # have drained the original queue.
            for n in range(2):
                key=f'trial-{trial}-{n}';payload={'trial':trial,'n':n}
                expected[key]=payload;x.enqueue(key,payload)
            with tempfile.TemporaryFile(dir=t) as out, tempfile.TemporaryFile(dir=t) as err:
                child=subprocess.Popen(['node',str(p/'app.mjs'),'work','--store',str(x.store),'--provider',str(x.provider),'--tenant','a','--now','0'],stdout=out,stderr=err,start_new_session=True,cwd=p)
                try:
                    time.sleep(delay)
                    if os.fstat(out.fileno()).st_size > OUTPUT_LIMIT or os.fstat(err.fileno()).st_size > OUTPUT_LIMIT:
                        raise HarnessError('kill-trial output exceeded byte budget')
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                        replacements=[pool.submit(x.work,0) for _ in range(2)]
                        if child.poll() is None:
                            stop(child)
                            if child.returncode == -signal.SIGKILL: killed_count+=1
                            else: missed+=1
                        else: missed+=1
                        for future in replacements: future.result()
                finally:stop(child)
            for record in x.truth():
                if record['key'] in preserved:equal(record,preserved[record['key']],'provider identity after kill')
                preserved[record['key']]=record
        for _ in range(len(expected)+2):x.work(0)
        state=x.state();equal(state['delivered'],len(expected));equal(len(state['jobs']),len(expected))
        equal({j['key'] for j in state['jobs']},set(expected))
        truth=x.truth();equal(len(truth),len(expected))
        equal({v['key']:v['payload'] for v in truth},expected)
        for record in truth:
            if record['key'] in preserved:equal(record,preserved[record['key']])
        require(all(j['attempts']>=1 for j in state['jobs']),'delivered without actual attempt')
        raise Inconclusive(f'recovery/state checks passed; live SIGKILLs={killed_count}, missed={missed}; durable claim/accept/write windows unobserved (public API cannot establish ownership at kill)')
    return groups


FACTORIES={'crm':crm_groups,'import':import_groups,'dispatch':dispatch_groups}


def evaluate(case: str, project: Path, artifacts: Path, seed: int=1) -> list[dict]:
    if case not in FACTORIES:
        return [{'name':'case-selection','passed':False,'outcome':'harness_error','error':f'unknown case: {case}'}]
    project=Path(project).resolve();artifacts=Path(artifacts).resolve()
    results=[]
    for index,(name,fn) in enumerate(FACTORIES[case]()):
        try:
            artifacts.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=f'{case}-{index:02d}-',dir=artifacts) as directory:
                fn(project,Path(directory),random.Random(seed+index*1009))
            results.append({'name':name,'passed':True,'outcome':'pass'})
        except Exception as e:
            if isinstance(e, Inconclusive): outcome = 'inconclusive'
            elif isinstance(e, (DeadlineExceeded, subprocess.TimeoutExpired, TimeoutError)): outcome = 'timeout'
            elif isinstance(e, (HarnessError, OSError)): outcome = 'harness_error'
            elif isinstance(e, (AssertionError, KeyError, TypeError, ValueError, http.client.HTTPException)): outcome = 'fail'
            else: outcome = 'harness_error'
            results.append({'name':name,'passed':False,'outcome':outcome,'error':f'{type(e).__name__}: {e}'})
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case');parser.add_argument('project',type=Path);parser.add_argument('artifacts',type=Path);parser.add_argument('--seed',type=int,default=1)
    args=parser.parse_args();results=evaluate(args.case,args.project,args.artifacts,args.seed)
    print(json.dumps(results));return int(any(not r['passed'] for r in results))


if __name__=='__main__':sys.exit(main())
