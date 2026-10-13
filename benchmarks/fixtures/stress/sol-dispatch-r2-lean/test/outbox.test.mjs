import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn, fork } from 'node:child_process';
import { mkdtemp, rm, readFile, writeFile, mkdir, cp, symlink } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { setTimeout as pause } from 'node:timers/promises';

const root = resolve(import.meta.dirname, '..');
const app = join(root, 'app.mjs');
async function fixture(t) {
  const dir = await mkdtemp(join(root, '.test-run-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  return { dir, store: join(dir, 'queue'), provider: join(dir, 'provider') };
}
function start(args, options = {}) {
  const { nodeArgs = [], ...spawnOptions } = options;
  const child = spawn(process.execPath, [...nodeArgs, app, ...args], { cwd: root, ...spawnOptions });
  let stdout = '', stderr = '';
  child.stdout.on('data', d => { stdout += d; });
  child.stderr.on('data', d => { stderr += d; });
  const done = new Promise((res, rej) => {
    const timeout = setTimeout(() => { child.kill('SIGKILL'); rej(new Error(`CLI timeout: ${args}`)); }, 30000);
    child.on('error', e => { clearTimeout(timeout); rej(e); });
    child.on('close', (code, signal) => {
      clearTimeout(timeout);
      try {
        const lines = stdout.trim().split('\n');
        assert.equal(lines.length, 1, stdout);
        const value = JSON.parse(lines[0]);
        assert.equal(typeof value, 'object');
        assert.notEqual(value, null);
        assert.equal(stderr, '');
        res({ code, signal, value });
      } catch (e) { rej(e); }
    });
  });
  return { child, done };
}
async function cli(args, failure = false) {
  const result = await start(args).done;
  if (failure) { assert.notEqual(result.code, 0); assert.equal(typeof result.value.error, 'string'); }
  else { assert.equal(result.code, 0, JSON.stringify(result)); assert.equal(result.signal, null); }
  return result.value;
}
const enq = (f, key, payload = { event: key }, tenant = 'alpha') =>
  cli(['enqueue', '--store', f.store, '--tenant', tenant, '--key', key, '--payload', JSON.stringify(payload)]);
const stat = (f, tenant = 'alpha') => cli(['status', '--store', f.store, '--tenant', tenant]);
const provider = (f, tenant = 'alpha') => cli(['provider', '--provider', f.provider, '--tenant', tenant]);
const workArgs = (f, now, mode = 'ok', tenant = 'alpha', crash) => ['work', '--store', f.store,
  '--provider', f.provider, '--tenant', tenant, '--now', String(now), '--mode', mode,
  ...(crash ? ['--crash', crash] : [])];
const work = (f, now, mode = 'ok', tenant = 'alpha') => cli(workArgs(f, now, mode, tenant));
async function state(f) { return JSON.parse(await readFile(join(f.store, 'state.json'), 'utf8')); }

async function pausedWorker(t, f, gate, now, mode = 'ok') {
  const child = fork(app, workArgs(f, now, mode), {
    cwd: root, execArgv: ['--import', join(root, 'test/gate.mjs')],
    env: { ...process.env, OUTBOX_TEST_GATE: gate }, silent: true,
  });
  t.after(() => { if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL'); });
  const exited = new Promise(resolve => child.once('exit', (code, signal) => resolve({ code, signal })));
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Gate timeout')), 10000);
    child.once('message', m => { clearTimeout(timer); assert.equal(m.paused, gate); resolve(); });
    child.once('exit', () => { clearTimeout(timer); reject(new Error('Exited before gate')); });
    child.once('error', reject);
  });
  return { child, exited };
}

test('semantic identity, conflict without mutation, arrays and tenant isolation', async t => {
  const f = await fixture(t);
  const p = JSON.parse('{"z":1,"nested":{"b":2,"a":1},"array":[1,2],"__proto__":{"x":1}}');
  const a = await enq(f, 'same', p);
  const b = await enq(f, 'same', JSON.parse('{"__proto__":{"x":1},"array":[1,2],"nested":{"a":1,"b":2},"z":1}'));
  assert.deepEqual(a, b);
  const before = await readFile(join(f.store, 'state.json'));
  await cli(['enqueue', '--store', f.store, '--tenant', 'alpha', '--key', 'same',
    '--payload', JSON.stringify({ ...p, array: [2, 1] })], true);
  assert.deepEqual(await readFile(join(f.store, 'state.json')), before);
  const other = await enq(f, 'same', { other: true }, 'beta');
  assert.notEqual(other.id, a.id);
  assert.deepEqual((await stat(f)).jobs, [{ id: a.id, key: 'same', status: 'pending', attempts: 0 }]);
  assert.equal((await work(f, 0, 'ok', 'beta')).id, other.id);
  assert.equal((await stat(f)).pending, 1);
  assert.deepEqual((await provider(f)).accepted, []);
  assert.deepEqual((await provider(f, 'beta')).accepted[0].payload, { other: true });
});

test('oldest eligible, at most one, independent provider truth and stable IDs', async t => {
  const f = await fixture(t);
  const a = await enq(f, 'a', { n: 1 });
  const b = await enq(f, 'b', { n: 2 });
  assert.deepEqual(await work(f, 10, 'transient'), { status: 'pending', id: a.id });
  assert.deepEqual(await work(f, 10), { status: 'delivered', id: b.id });
  assert.deepEqual(await work(f, 11), { status: 'idle' });
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.deepEqual(await work(f, 12), { status: 'delivered', id: a.id });
  const accepted = (await provider(f)).accepted;
  assert.equal(accepted.length, 2);
  const s = await state(f);
  assert.equal(s.jobs[0].deliveryId, accepted.find(v => v.key === 'a').id);
  assert.deepEqual(accepted.find(v => v.key === 'a').payload, { n: 1 });
  assert.deepEqual(await enq(f, 'a', { n: 1 }), { id: a.id, status: 'delivered' });
  assert.deepEqual(await work(f, 12), { status: 'idle' });
});

test('retry deadlines +2 then +4 and exactly three attempts, permanent rejection', async t => {
  const f = await fixture(t);
  await enq(f, 'retry');
  assert.equal((await work(f, 100, 'transient')).status, 'pending');
  assert.equal((await work(f, 101, 'transient')).status, 'idle');
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.equal((await work(f, 102, 'transient')).status, 'pending');
  assert.equal((await work(f, 105, 'transient')).status, 'idle');
  assert.equal((await stat(f)).jobs[0].attempts, 2);
  assert.equal((await work(f, 106, 'transient')).status, 'dead');
  assert.deepEqual((await stat(f)).jobs.map(j => [j.status, j.attempts]), [['dead', 3]]);
  assert.equal((await work(f, 106)).status, 'idle');
  await enq(f, 'reject');
  assert.equal((await work(f, 106, 'reject')).status, 'dead');
  assert.deepEqual((await stat(f)).jobs.map(j => [j.status, j.attempts]), [['dead', 3], ['dead', 1]]);
  assert.deepEqual((await provider(f)).accepted, []);
});

test('lost response reconciles provider ID without another attempt, ignoring mode', async t => {
  const f = await fixture(t);
  const a = await enq(f, 'timeout', { nested: [1, { test: true }] });
  assert.deepEqual(await work(f, 5, 'accepted-timeout'), { status: 'uncertain', id: a.id });
  assert.equal((await stat(f)).uncertain, 1);
  const accepted = (await provider(f)).accepted;
  assert.equal(accepted.length, 1);
  assert.equal((await work(f, 5, 'reject')).status, 'delivered');
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.equal((await state(f)).jobs[0].deliveryId, accepted[0].id);
  assert.deepEqual((await provider(f)).accepted, accepted);
});

test('both public crash flags use abrupt death and recover at the same logical time', async t => {
  for (const point of ['before-send', 'after-accept']) {
    const f = await fixture(t);
    await enq(f, point);
    const result = await start(workArgs(f, 7, 'ok', 'alpha', point)).done;
    assert.equal(result.signal, 'SIGKILL');
    assert.equal(typeof result.value.error, 'string');
    const s = await stat(f);
    assert.equal(s.uncertain, 1);
    assert.equal(s.jobs[0].attempts, point === 'before-send' ? 0 : 1);
    assert.equal((await provider(f)).accepted.length, point === 'before-send' ? 0 : 1);
    assert.equal((await work(f, 7)).status, 'delivered');
    assert.equal((await stat(f)).jobs[0].attempts, 1);
    assert.equal((await provider(f)).accepted.length, 1);
  }
});

test('external SIGKILL after durable claim: live owner blocks contender, then recovers', async t => {
  const f = await fixture(t);
  await enq(f, 'kill-claim');
  const owner = await pausedWorker(t, f, 'claim', 20);
  const waiter = start(workArgs(f, 20));
  t.after(() => { if (waiter.child.exitCode === null) waiter.child.kill('SIGKILL'); });
  await pause(100);
  assert.equal(waiter.child.exitCode, null, 'must not bypass a live owner');
  owner.child.kill('SIGKILL');
  assert.equal((await owner.exited).signal, 'SIGKILL');
  assert.equal((await waiter.done).value.status, 'delivered');
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.equal((await provider(f)).accepted.length, 1);
});

test('killing an acquiring contender cannot remove the live worker ownership', async t => {
  const f = await fixture(t);
  await enq(f, 'owner-safe');
  const owner = await pausedWorker(t, f, 'claim', 0);
  const contender = await pausedWorker(t, f, 'ticket', 0);
  contender.child.kill('SIGKILL');
  assert.equal((await contender.exited).signal, 'SIGKILL');
  const survivor = start(workArgs(f, 0));
  t.after(() => { if (survivor.child.exitCode === null) survivor.child.kill('SIGKILL'); });
  await pause(100);
  assert.equal(survivor.child.exitCode, null);
  owner.child.kill('SIGKILL');
  await owner.exited;
  assert.equal((await survivor.done).value.status, 'delivered');
  assert.equal((await provider(f)).accepted.length, 1);
  assert.equal((await stat(f)).jobs[0].attempts, 1);
});

test('external SIGKILL after provider commit recovers both locks and never resends', async t => {
  const f = await fixture(t);
  await enq(f, 'kill-accept');
  const owner = await pausedWorker(t, f, 'accept', 30);
  owner.child.kill('SIGKILL');
  assert.equal((await owner.exited).signal, 'SIGKILL');
  const accepted = (await provider(f)).accepted;
  assert.equal(accepted.length, 1);
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.equal((await work(f, 30, 'reject')).status, 'delivered');
  assert.equal((await stat(f)).jobs[0].attempts, 1);
  assert.deepEqual((await provider(f)).accepted, accepted);
});

test('killed transient/reject receipts preserve execution-time deadlines and attempt limits', async t => {
  const f = await fixture(t);
  await enq(f, 'killed-retry');
  for (const [now, expected, attempts] of [[10, 'pending', 1], [17, 'pending', 2], [21, 'dead', 3]]) {
    const owner = await pausedWorker(t, f, 'receipt', now, 'transient');
    owner.child.kill('SIGKILL');
    assert.equal((await owner.exited).signal, 'SIGKILL');
    const s = await stat(f);
    assert.equal(s.jobs[0].status, expected);
    assert.equal(s.jobs[0].attempts, attempts);
    if (attempts < 3) {
      const due = now + (attempts === 1 ? 2 : 4);
      assert.equal((await state(f)).jobs[0].due, String(due));
      assert.equal((await work(f, due - 1)).status, 'idle');
    }
  }
  await enq(f, 'killed-reject');
  const owner = await pausedWorker(t, f, 'receipt', 21, 'reject');
  owner.child.kill('SIGKILL');
  await owner.exited;
  assert.equal((await stat(f)).jobs[1].status, 'dead');
  assert.equal((await stat(f)).jobs[1].attempts, 1);
  assert.equal((await provider(f)).accepted.length, 0);
});

test('concurrent enqueues and workers preserve identities and both tenants', async t => {
  const f = await fixture(t);
  const results = await Promise.all(Array.from({ length: 16 }, (_, i) =>
    enq(f, `k${i % 4}`, { v: i % 4 }, i < 8 ? 'alpha' : 'beta')));
  assert.equal(new Set(results.map(r => r.id)).size, 8);
  await Promise.all([
    ...Array.from({ length: 16 }, (_, i) => work(f, 0, 'ok', i % 2 ? 'alpha' : 'beta')),
    ...Array.from({ length: 8 }, (_, i) => enq(f, `extra${i % 2}`, { extra: i % 2 }, i < 4 ? 'alpha' : 'beta')),
  ]);
  await Promise.all(Array.from({ length: 8 }, (_, i) => work(f, 0, 'ok', i % 2 ? 'alpha' : 'beta')));
  for (const tenant of ['alpha', 'beta']) {
    const s = await stat(f, tenant);
    assert.equal(s.jobs.length, 6);
    assert.equal(s.delivered, 6);
    assert.ok(s.jobs.every(j => j.attempts === 1));
    assert.equal((await provider(f, tenant)).accepted.length, 6);
  }
});

test('independent queue stores share provider deduplication and semantic conflict checks', async t => {
  const f = await fixture(t);
  const g = { ...f, store: join(f.dir, 'queue2') };
  const h = { ...f, store: join(f.dir, 'queue3') };
  await enq(f, 'same', { a: 1, b: 2 });
  await enq(g, 'same', { b: 2, a: 1 });
  const out = await Promise.all([work(f, 0), work(g, 0)]);
  assert.ok(out.every(r => r.status === 'delivered'));
  const accepted = (await provider(f)).accepted;
  assert.equal(accepted.length, 1);
  assert.equal((await state(f)).jobs[0].deliveryId, (await state(g)).jobs[0].deliveryId);
  await enq(h, 'same', { a: 9 });
  await cli(workArgs(h, 0), true);
  assert.deepEqual((await provider(f)).accepted, accepted);
  assert.equal((await stat(h)).jobs[0].attempts, 0);
});

test('malformed JSON, schema and independent provider persistence fail visibly', async t => {
  const f = await fixture(t);
  await mkdir(f.store);
  for (const value of ['{', 'null', '{}', JSON.stringify({ version: 9, kind: 'queue', jobs: [], clocks: [] })]) {
    await writeFile(join(f.store, 'state.json'), value);
    await cli(['status', '--store', f.store, '--tenant', 'alpha'], true);
    await cli(['enqueue', '--store', f.store, '--tenant', 'alpha', '--key', 'x', '--payload', '{}'], true);
    assert.equal(await readFile(join(f.store, 'state.json'), 'utf8'), value);
  }
  await rm(f.store, { recursive: true });
  await enq(f, 'provider-corrupt');
  await mkdir(f.provider);
  await writeFile(join(f.provider, 'state.json'), '{');
  await cli(['provider', '--provider', f.provider, '--tenant', 'alpha'], true);
  await cli(workArgs(f, 0), true);
  await cli(['status', '--store', f.store, '--tenant', 'alpha'], true);
  assert.equal(await readFile(join(f.provider, 'state.json'), 'utf8'), '{');
});

test('input validation, separate physical stores, monotonic and large logical seconds', async t => {
  const f = await fixture(t);
  const bad = [
    ['enqueue', '--store', f.store, '--tenant', ' ', '--key', 'x', '--payload', '{}'],
    ['enqueue', '--store', f.store, '--tenant', 'alpha', '--key', '', '--payload', '{}'],
    ...['null', '[]', '1', '{', '{"x":1e400}'].map(p => ['enqueue', '--store', f.store, '--tenant', 'alpha', '--key', 'x', '--payload', p]),
    ['status', '--store', f.store, '--tenant', 'alpha', '--tenant', 'beta'],
    workArgs(f, '1.2'), workArgs(f, 0, 'bogus'), workArgs(f, 0, 'reject', 'alpha', 'after-accept'),
    ['status', '--store', f.store], ['bogus'],
  ];
  for (const args of bad) await cli(args, true);
  await assert.rejects(readFile(join(f.store, 'state.json')), { code: 'ENOENT' });
  await enq(f, 'bigtime');
  const alias = join(f.dir, 'alias');
  await symlink(f.store, alias);
  await cli(workArgs({ ...f, provider: alias }, 0), true);
  const now = 90071992547409931234567890n;
  assert.equal((await work(f, now, 'transient')).status, 'pending');
  assert.equal((await work(f, now + 1n)).status, 'idle');
  await cli(workArgs(f, now - 1n), true);
  assert.equal((await work(f, now + 2n)).status, 'delivered');
  const another = join(f.dir, 'wrong-provider');
  await enq(f, 'bound');
  await work(f, now + 2n, 'accepted-timeout');
  await cli(workArgs({ ...f, provider: another }, now + 2n), true);
});

test('persistence failures never acknowledge success and recover without losing or duplicating delivery', async t => {
  const f = await fixture(t);
  async function fault(args, point) {
    const r = await start(args, {
      nodeArgs: ['--import', join(root, 'test/fault.mjs')],
      env: { ...process.env, OUTBOX_TEST_FAULT: point },
    }).done;
    assert.equal(r.code, 1);
    assert.match(r.value.error, /Injected persistence failure/);
  }
  await fault(['enqueue', '--store', f.store, '--tenant', 'alpha', '--key', 'write-fail', '--payload', '{}'], 'enqueue');
  assert.equal((await stat(f)).jobs.length, 0);
  const a = await enq(f, 'write-fail', {});
  await fault(workArgs(f, 0), 'provider');
  assert.equal((await stat(f)).jobs[0].attempts, 0);
  assert.equal((await provider(f)).accepted.length, 0);
  await fault(workArgs(f, 0), 'success');
  const accepted = (await provider(f)).accepted;
  assert.equal(accepted.length, 1);
  const s = await stat(f);
  assert.equal(s.uncertain, 1);
  assert.equal(s.jobs[0].attempts, 1);
  assert.deepEqual(await work(f, 0), { id: a.id, status: 'delivered' });
  assert.deepEqual((await provider(f)).accepted, accepted);
  assert.equal((await stat(f)).jobs[0].attempts, 1);
});

test('quiescent snapshots restore independently, preserving uncertainty and acceptance', async t => {
  const f = await fixture(t);
  await enq(f, 'restore');
  await work(f, 0, 'accepted-timeout');
  const backup = join(f.dir, 'backup');
  await mkdir(backup);
  await cp(f.store, join(backup, 'queue'), { recursive: true });
  await cp(f.provider, join(backup, 'provider'), { recursive: true });
  const accepted = (await provider(f)).accepted;
  await work(f, 0);
  // Restore to original paths because queue claims/provider binding use real paths.
  await rm(f.store, { recursive: true });
  await rm(f.provider, { recursive: true });
  await cp(join(backup, 'queue'), f.store, { recursive: true });
  await cp(join(backup, 'provider'), f.provider, { recursive: true });
  assert.equal((await stat(f)).uncertain, 1);
  assert.equal((await work(f, 0)).status, 'delivered');
  assert.deepEqual((await provider(f)).accepted, accepted);
  assert.equal((await stat(f)).jobs[0].attempts, 1);
});
