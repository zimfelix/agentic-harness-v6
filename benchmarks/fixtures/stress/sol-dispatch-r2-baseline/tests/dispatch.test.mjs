import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, rmSync, cpSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const root = resolve(import.meta.dirname, '..');
const tempRoot = join(root, '.test-data');
mkdirSync(tempRoot, { recursive: true });
function fixture(t) {
  const base = mkdtempSync(join(tempRoot, 'dispatch-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  return { base, store: join(base, 'local'), provider: join(base, 'provider'), tenant: 'alpha' };
}
function args(command, options) {
  return [join(root, 'app.mjs'), command, ...Object.entries(options).flatMap(([k, v]) => [`--${k}`, String(v)])];
}
function decode(result, success = true) {
  const lines = result.stdout.trim().split('\n');
  assert.equal(lines.length, 1, `stdout: ${result.stdout}; stderr: ${result.stderr}`);
  const value = JSON.parse(lines[0]);
  assert.ok(value && !Array.isArray(value) && typeof value === 'object');
  if (success) assert.equal(result.status, 0, result.stderr + result.stdout);
  else assert.notEqual(result.status, 0);
  return value;
}
function run(command, options, success = true) {
  return decode(spawnSync(process.execPath, args(command, options), { encoding: 'utf8', cwd: root, timeout: 15000 }), success);
}
function asyncRun(command, options) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(process.execPath, args(command, options), { cwd: root });
    let stdout = ''; let stderr = '';
    child.stdout.on('data', data => stdout += data);
    child.stderr.on('data', data => stderr += data);
    child.on('error', reject);
    child.on('close', (status, signal) => {
      try { resolvePromise(decode({ stdout, stderr, status, signal })); } catch (error) { reject(error); }
    });
  });
}
function enq(f, key, payload = '{}', tenant = f.tenant) {
  return run('enqueue', { store: f.store, tenant, key, payload });
}
function stat(f, tenant = f.tenant) { return run('status', { store: f.store, tenant }); }
function truth(f, tenant = f.tenant) { return run('provider', { provider: f.provider, tenant }); }
function work(f, now = 0, extra = {}) {
  return run('work', { store: f.store, provider: f.provider, tenant: f.tenant, now, ...extra });
}

test('semantic identity, tenant isolation, durable enqueue and conflict without mutation', t => {
  const f = fixture(t);
  const payload = '{"b":[1,{"z":2,"a":3}],"a":{"__proto__":4}}';
  const job = enq(f, 'same', payload);
  assert.equal(job.status, process.env.TEST_NEGATIVE_CONTROL ? 'delivered' : 'pending');
  assert.deepEqual(enq(f, 'same', '{"a":{"__proto__":4},"b":[1,{"a":3,"z":2}]}'), job);
  const before = readFileSync(join(f.store, 'state.sqlite'));
  assert.match(run('enqueue', { store: f.store, tenant: f.tenant, key: 'same', payload: '{"b":[2,1]}' }, false).error, /conflict/);
  assert.deepEqual(readFileSync(join(f.store, 'state.sqlite')), before);
  assert.ok(run('enqueue', { store: f.store, tenant: f.tenant, key: 'same', payload: '{"a":{"__proto__":4},"b":[{"a":3,"z":2},1]}' }, false).error);
  const other = enq(f, 'same', '{"different":true}', 'beta');
  assert.notEqual(other.id, job.id);
  assert.deepEqual(stat(f).jobs, [{ id: job.id, key: 'same', status: 'pending', attempts: 0 }]);
  assert.equal(stat(f, 'beta').jobs[0].id, other.id);
  assert.equal(stat(f, 'unknown').jobs.length, 0);
});

test('JSON numeric semantics preserve large values and equivalent spellings', t => {
  const f = fixture(t);
  const job = enq(f, 'numbers', '{"huge":1e400,"precise":9007199254740993,"zero":-0,"decimal":1.2300}');
  assert.deepEqual(enq(f, 'numbers', '{"decimal":123e-2,"zero":0.0,"precise":9007199254740993.0,"huge":10e399}'), job);
  assert.ok(run('enqueue', { store: f.store, tenant: f.tenant, key: 'numbers', payload: '{"huge":1e400,"precise":9007199254740992,"zero":0,"decimal":1.23}' }, false).error);
  assert.equal(work(f).status, 'delivered');
  const result = spawnSync(process.execPath, args('provider', { provider: f.provider, tenant: f.tenant }), { encoding: 'utf8' });
  assert.equal(result.status, 0);
  assert.match(result.stdout, /"huge":1e400/);
  assert.match(result.stdout, /"precise":9007199254740993/);
});

test('ok, reject, independent provider truth, FIFO and terminal statuses', t => {
  const f = fixture(t);
  const first = enq(f, 'first', '{"items":[2,1],"nested":{"a":null}}');
  const second = enq(f, 'second');
  enq(f, 'isolated', '{}', 'beta');
  assert.deepEqual(work(f), { status: 'delivered', id: first.id });
  assert.deepEqual(work(f, 0, { mode: 'reject' }), { status: 'dead', id: second.id });
  assert.deepEqual(work(f), { status: 'idle' });
  const accepted = truth(f).accepted;
  assert.equal(accepted.length, 1);
  assert.deepEqual(accepted[0].payload, { items: [2, 1], nested: { a: null } });
  assert.equal(accepted[0].key, 'first');
  assert.deepEqual(truth(f, 'beta'), { accepted: [] });
  assert.deepEqual(stat(f).jobs.map(j => [j.status, j.attempts]), [['delivered', 1], ['dead', 1]]);
  assert.equal(stat(f, 'beta').pending, 1);
  assert.equal(enq(f, 'first', '{"nested":{"a":null},"items":[2,1]}').status, 'delivered');
  const db = new DatabaseSync(join(f.store, 'state.sqlite'));
  assert.equal(db.prepare('SELECT provider_id FROM jobs WHERE id=?').get(first.id).provider_id, accepted[0].id);
  db.close();
  rmSync(f.store, { recursive: true });
  assert.deepEqual(truth(f).accepted, accepted); // Provider does not derive truth from outbox.
});

test('transient +2/+4, due boundaries, three attempts, oldest eligible selection', t => {
  const f = fixture(t);
  const first = enq(f, 'retry');
  assert.deepEqual(work(f, 10, { mode: 'transient' }), { status: 'pending', id: first.id });
  assert.deepEqual(work(f, 11), { status: 'idle' });
  assert.equal(stat(f).jobs[0].attempts, 1);
  const younger = enq(f, 'younger');
  assert.deepEqual(work(f, 11), { status: 'delivered', id: younger.id });
  assert.equal(work(f, 12, { mode: 'transient' }).status, 'pending');
  assert.equal(work(f, 15).status, 'idle');
  assert.equal(stat(f).jobs[0].attempts, 2);
  assert.equal(work(f, 16, { mode: 'transient' }).status, 'dead');
  assert.equal(stat(f).jobs[0].attempts, 3);
  assert.equal(work(f, 16).status, 'idle');
  assert.equal(truth(f).accepted.length, 1);
});

test('accepted-timeout reconciles without another attempt or changed provider ID', t => {
  const f = fixture(t);
  const job = enq(f, 'timeout', '{"a":1}');
  assert.deepEqual(work(f, 7, { mode: 'accepted-timeout' }), { status: 'uncertain', id: job.id });
  const accepted = truth(f).accepted;
  assert.equal(stat(f).uncertain, 1);
  assert.equal(stat(f).jobs[0].attempts, 1);
  assert.equal(work(f, 7, { mode: 'reject' }).status, 'delivered');
  assert.equal(stat(f).jobs[0].attempts, 1);
  assert.deepEqual(truth(f).accepted, accepted);
});

for (const crash of ['before-send', 'after-accept']) {
  test(`real SIGKILL ${crash} and same-time restart`, t => {
    const f = fixture(t); const job = enq(f, 'crash');
    const result = spawnSync(process.execPath, args('work', { store: f.store, provider: f.provider, tenant: f.tenant, now: 5, crash }), { encoding: 'utf8' });
    assert.equal(result.signal, 'SIGKILL');
    decode(result, false);
    assert.equal(stat(f).uncertain, 1);
    assert.equal(stat(f).jobs[0].attempts, crash === 'before-send' ? 0 : 1);
    const accepted = truth(f).accepted;
    assert.equal(accepted.length, crash === 'before-send' ? 0 : 1);
    assert.deepEqual(work(f, 5), { status: 'delivered', id: job.id });
    assert.equal(stat(f).jobs[0].attempts, 1);
    assert.equal(truth(f).accepted.length, 1);
    if (accepted.length) assert.deepEqual(truth(f).accepted, accepted);
  });
}

test('concurrent enqueue identities and multi-tenant workers preserve all jobs', async t => {
  const f = fixture(t);
  const options = (tenant, key) => ({ store: f.store, tenant, key, payload: '{"v":1}' });
  const duplicate = await Promise.all(Array.from({ length: 12 }, () => asyncRun('enqueue', options('alpha', 'duplicate'))));
  assert.equal(new Set(duplicate.map(j => j.id)).size, 1);
  await Promise.all(Array.from({ length: 12 }, (_, i) => asyncRun('enqueue', options(i % 2 ? 'alpha' : 'beta', `k${i}`))));
  await Promise.all(Array.from({ length: 20 }, (_, i) => asyncRun('work', { store: f.store, provider: f.provider, tenant: i % 2 ? 'alpha' : 'beta', now: 0 })));
  assert.equal(stat(f).delivered, 7);
  assert.equal(stat(f, 'beta').delivered, 6);
  assert.ok(stat(f).jobs.every(j => j.attempts === 1));
  assert.equal(truth(f).accepted.length, 7);
  assert.equal(truth(f, 'beta').accepted.length, 6);
});

test('permanent provider dedup across separate local stores and semantic provider conflict', async t => {
  const f = fixture(t); const other = { ...f, store: join(f.base, 'other-local') };
  enq(f, 'same', '{"a":1,"b":2}');
  enq(other, 'same', '{"b":2,"a":1}');
  await Promise.all([f, other].map(x => asyncRun('work', { store: x.store, provider: x.provider, tenant: x.tenant, now: 0 })));
  assert.equal(truth(f).accepted.length, 1);
  assert.equal(stat(f).delivered, 1); assert.equal(stat(other).delivered, 1);
  const conflict = { ...f, store: join(f.base, 'conflicting-local') };
  enq(conflict, 'same', '{"a":9}');
  assert.match(run('work', { store: conflict.store, provider: f.provider, tenant: f.tenant, now: 0 }, false).error, /conflict/);
  assert.equal(truth(f).accepted.length, 1);
  assert.equal(stat(conflict).jobs[0].attempts, 0);
});

async function killedHolder(t, script) {
  const child = spawn(process.execPath, ['--input-type=module', '-e', script], { cwd: root });
  t.after(() => { if (child.exitCode === null) child.kill('SIGKILL'); });
  let stderr = '';
  child.stderr.on('data', data => stderr += data);
  await new Promise((resolvePromise, reject) => {
    const timeout = setTimeout(() => reject(new Error(`Holder did not start: ${stderr}`)), 8000);
    child.stdout.once('data', () => { clearTimeout(timeout); resolvePromise(); });
    child.once('error', reject);
    child.once('exit', () => { clearTimeout(timeout); reject(new Error(`Holder exited: ${stderr}`)); });
  });
  return child;
}
function closeAfterKill(child) {
  return new Promise(resolvePromise => { child.once('close', resolvePromise); child.kill('SIGKILL'); });
}

test('external kill rolls back in-flight attached transaction and releases ownership to waiting worker', async t => {
  const f = fixture(t); enq(f, 'killed');
  const script = `import {withLocal,transaction,attachProvider} from './src/storage.mjs';
    withLocal(${JSON.stringify(f.store)}, db => {
      attachProvider(db,${JSON.stringify(f.store)},${JSON.stringify(f.provider)});
      transaction(db,()=>db.exec("UPDATE jobs SET status='uncertain'"));
      db.exec('BEGIN IMMEDIATE');
      db.exec("UPDATE jobs SET attempts=1; INSERT INTO remote.accepted(id,tenant,key,payload) VALUES ('not-committed','alpha','killed','{}')");
      console.log('locked'); Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0);
    });`;
  const holder = await killedHolder(t, script);
  const waiting = asyncRun('work', { store: f.store, provider: f.provider, tenant: f.tenant, now: 0 });
  await closeAfterKill(holder);
  assert.equal((await waiting).status, 'delivered');
  assert.equal(stat(f).jobs[0].attempts, 1);
  assert.equal(truth(f).accepted.length, 1);
  assert.notEqual(truth(f).accepted[0].id, 'not-committed');
});

test('one owner finishing does not release the next owner lock', async t => {
  const f = fixture(t); enq(f, 'lock');
  const holder = await killedHolder(t, `import {withLocal} from './src/storage.mjs';
    withLocal(${JSON.stringify(f.store)}, () => {console.log('locked');Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0);});`);
  let finished = false;
  const waiting = asyncRun('status', { store: f.store, tenant: f.tenant }).then(result => { finished = true; return result; });
  await new Promise(resolvePromise => setTimeout(resolvePromise, 120));
  assert.equal(finished, false);
  await closeAfterKill(holder);
  assert.equal((await waiting).pending, 1);
});

test('visible validation errors and malformed local/provider persistence', t => {
  const f = fixture(t);
  for (const payload of ['[]', 'null', '2', 'bad', '{"invalid":NaN}']) {
    assert.ok(run('enqueue', { store: f.store, tenant: f.tenant, key: 'bad', payload }, false).error);
  }
  for (const tenant of ['', '  ']) assert.ok(run('status', { store: f.store, tenant }, false).error);
  for (const key of ['', '  ']) assert.ok(run('enqueue', { store: f.store, tenant: f.tenant, key, payload: '{}' }, false).error);
  assert.ok(decode(spawnSync(process.execPath, args('status', { store: f.store, tenant: f.tenant }).concat(['--tenant', 'beta']), { encoding: 'utf8' }), false).error);
  enq(f, 'valid');
  for (const now of ['1.5', 'NaN', '1e3']) assert.ok(run('work', { store: f.store, provider: f.provider, tenant: f.tenant, now }, false).error);
  assert.ok(run('work', { store: f.store, provider: f.provider, tenant: f.tenant, now: 0, mode: 'unknown' }, false).error);
  assert.ok(run('work', { store: f.store, provider: f.store, tenant: f.tenant, now: 0 }, false).error);
  const db = new DatabaseSync(join(f.store, 'state.sqlite'));
  db.exec("UPDATE jobs SET payload='not-json'"); db.close();
  assert.ok(run('status', { store: f.store, tenant: f.tenant }, false).error);
  mkdirSync(f.provider, { recursive: true });
  writeFileSync(join(f.provider, 'provider.sqlite'), 'malformed');
  assert.ok(run('provider', { provider: f.provider, tenant: f.tenant }, false).error);
  writeFileSync(join(f.provider, 'provider.sqlite'), '');
  assert.ok(run('provider', { provider: f.provider, tenant: f.tenant }, false).error);
});

test('empty valid-looking SQLite schema is rejected instead of silently initialized', t => {
  const f = fixture(t); mkdirSync(f.provider);
  const db = new DatabaseSync(join(f.provider, 'provider.sqlite')); db.close();
  assert.ok(run('provider', { provider: f.provider, tenant: f.tenant }, false).error);
});

test('negative logical seconds and quiescent backup/restore of both stores', t => {
  const f = fixture(t); enq(f, 'backup', '{"synthetic":true}');
  assert.equal(work(f, -10, { mode: 'accepted-timeout' }).status, 'uncertain');
  const savedTruth = truth(f);
  cpSync(f.store, join(f.base, 'saved-local'), { recursive: true });
  cpSync(f.provider, join(f.base, 'saved-provider'), { recursive: true });
  rmSync(f.store, { recursive: true }); rmSync(f.provider, { recursive: true });
  cpSync(join(f.base, 'saved-local'), f.store, { recursive: true });
  cpSync(join(f.base, 'saved-provider'), f.provider, { recursive: true });
  assert.equal(work(f, -10).status, 'delivered');
  assert.deepEqual(truth(f), savedTruth);
  assert.equal(stat(f).jobs[0].attempts, 1);
});
