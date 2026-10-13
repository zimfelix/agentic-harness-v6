import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn, fork } from 'node:child_process';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

const root = path.resolve('.test-data');
const app = path.resolve('app.mjs');
async function fixture(t) {
  const base = path.join(root, randomUUID());
  await fs.mkdir(base, { recursive: true });
  t.after(async () => { await fs.rm(base, { recursive: true, force: true }); });
  const store = path.join(base, 'local'), provider = path.join(base, 'fake');
  function args(command, options = {}) {
    const defaults = command === 'provider' ? { provider, tenant: 'a' } : command === 'work' ? { store, provider, tenant: 'a', now: 10 } : { store, tenant: 'a' };
    return [command, ...Object.entries({ ...defaults, ...options }).flatMap(([k, v]) => ['--' + k, typeof v === 'object' ? JSON.stringify(v) : String(v)])];
  }
  async function run(command, options, fail = false) {
    const result = await execute(args(command, options));
    assert.equal(result.code === 0, !fail, result.stdout + result.stderr);
    assert.equal(result.stdout.trim().split('\n').length, 1);
    return JSON.parse(result.stdout);
  }
  return { base, store, provider, args, run, enqueue: (key = 'k', payload = { value: 1 }, tenant = 'a') => run('enqueue', { key, payload, tenant }) };
}
function execute(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [app, ...args]);
    let stdout = '', stderr = '';
    child.stdout.on('data', b => { stdout += b; });
    child.stderr.on('data', b => { stderr += b; });
    child.on('error', reject);
    child.on('close', (code, signal) => resolve({ code, signal, stdout, stderr }));
  });
}
async function killAt(f, phase, options = {}) {
  const child = fork(app, f.args('work', options), { silent: true });
  let stderr = '';
  child.stderr.on('data', x => { stderr += x; });
  const closed = new Promise(resolve => child.once('close', (code, signal) => resolve({ code, signal })));
  const timeout = setTimeout(() => child.kill('SIGKILL'), 10000);
  try {
    await new Promise((resolve, reject) => {
      child.on('error', reject);
      child.on('exit', () => reject(new Error('Child exited before target phase: ' + stderr)));
      child.on('message', msg => {
        if (msg.phase === phase) resolve();
        else child.send({ continue: true });
      });
    });
    child.kill('SIGSTOP');
    child.kill('SIGKILL');
    assert.equal((await closed).signal, 'SIGKILL');
  } finally { clearTimeout(timeout); child.kill('SIGKILL'); }
}

test('semantic identity, durable reopen, tenant isolation, conflicts are mutation-free', async t => {
  const f = await fixture(t);
  const payload = { b: [1, { y: 2, x: 3 }], a: 0 };
  const first = await f.enqueue('k', payload);
  assert.deepEqual(await f.enqueue('k', { a: 0, b: [1, { x: 3, y: 2 }] }), first);
  assert.notEqual((await f.enqueue('k', payload, 'b')).id, first.id);
  const bytes = await fs.readFile(path.join(f.store, 'state.json'));
  assert.match((await f.run('enqueue', { key: 'k', payload: { a: 0, b: [{ x: 3, y: 2 }, 1] } }, true)).error, /conflict/i);
  assert.deepEqual(await fs.readFile(path.join(f.store, 'state.json')), bytes);
  const status = await f.run('status');
  assert.deepEqual(status, { pending: 1, uncertain: 0, delivered: 0, dead: 0, jobs: [{ id: first.id, key: 'k', status: 'pending', attempts: 0 }] });
  assert.deepEqual((await f.run('status', { tenant: 'unknown' })).jobs, []);
});

test('ok and permanent rejection; original provider payload is independent truth', async t => {
  const f = await fixture(t);
  const payload = { nested: { z: [1, true, null] }, '__proto__': 'ignored by JS literal' };
  await f.enqueue('ok', payload); await f.enqueue('reject', {});
  assert.equal((await f.run('work')).status, 'delivered');
  assert.equal((await f.run('work', { mode: 'reject' })).status, 'dead');
  assert.deepEqual(await f.run('work'), { status: 'idle' });
  const p = await f.run('provider');
  assert.equal(p.accepted.length, 1); assert.deepEqual(p.accepted[0].payload, payload);
  const s = await f.run('status'); assert.equal(s.delivered, 1); assert.equal(s.dead, 1);
  assert.deepEqual(s.jobs.map(j => j.attempts), [1, 1]);
  assert.deepEqual(await f.enqueue('ok', payload), { id: s.jobs[0].id, status: 'delivered' });
});

test('three transient attempts and +2/+4 due boundaries; oldest eligible skips delayed jobs', async t => {
  const f = await fixture(t);
  const a = await f.enqueue('a');
  assert.deepEqual(await f.run('work', { now: 20, mode: 'transient' }), { id: a.id, status: 'pending' });
  assert.equal((await f.run('status')).jobs[0].attempts, 1);
  assert.deepEqual(await f.run('work', { now: 21 }), { status: 'idle' });
  const b = await f.enqueue('b');
  assert.equal((await f.run('work', { now: 21 })).id, b.id);
  assert.equal((await f.run('work', { now: 22, mode: 'transient' })).status, 'pending');
  assert.deepEqual(await f.run('work', { now: 25 }), { status: 'idle' });
  assert.equal((await f.run('status')).jobs[0].attempts, 2);
  assert.equal((await f.run('work', { now: 26, mode: 'transient' })).status, 'dead');
  assert.equal((await f.run('status')).jobs[0].attempts, 3);
  assert.deepEqual(await f.run('work', { now: 999 }), { status: 'idle' });
  assert.deepEqual((await f.run('provider')).accepted.map(x => x.key), ['b']);
});

test('accepted timeout reconciles once without another attempt or acceptance', async t => {
  const f = await fixture(t); await f.enqueue();
  assert.equal((await f.run('work', { mode: 'accepted-timeout' })).status, 'uncertain');
  const truth = await f.run('provider'); assert.equal(truth.accepted.length, 1);
  assert.equal((await f.run('status')).jobs[0].attempts, 1);
  assert.equal((await f.run('work', { mode: 'reject' })).status, 'delivered');
  assert.deepEqual(await f.run('provider'), truth);
  assert.equal((await f.run('status')).jobs[0].attempts, 1);
  const local = JSON.parse(await fs.readFile(path.join(f.store, 'state.json')));
  assert.equal(local.jobs[0].deliveryId, truth.accepted[0].id);
});

for (const crash of ['before-send', 'after-accept']) {
  test('abrupt injected exit recovers at same logical time: ' + crash, async t => {
    const f = await fixture(t); await f.enqueue();
    assert.match((await f.run('work', { crash }, true)).error, /crash/i);
    const s = await f.run('status'); assert.equal(s.uncertain, 1);
    assert.equal(s.jobs[0].attempts, crash === 'before-send' ? 0 : 1);
    assert.equal((await f.run('provider')).accepted.length, crash === 'before-send' ? 0 : 1);
    assert.equal((await f.run('work')).status, 'delivered');
    assert.equal((await f.run('status')).jobs[0].attempts, 1);
    assert.equal((await f.run('provider')).accepted.length, 1);
  });
}
for (const phase of ['claimed', 'provider-committed']) {
  test('real SIGSTOP/SIGKILL recovers process ownership: ' + phase, async t => {
    const f = await fixture(t); await f.enqueue();
    await killAt(f, phase);
    assert.equal((await f.run('status')).jobs[0].attempts, phase === 'claimed' ? 0 : 1);
    const before = await f.run('provider');
    assert.equal(before.accepted.length, phase === 'claimed' ? 0 : 1);
    const results = await Promise.all(Array.from({ length: 6 }, () => f.run('work')));
    assert.equal(results.filter(x => x.status === 'delivered').length, 1);
    const after = await f.run('provider'); assert.equal(after.accepted.length, 1);
    if (phase === 'provider-committed') assert.deepEqual(after, before);
    assert.equal((await f.run('status')).jobs[0].attempts, 1);
  });
}

test('killed transient invocation receipt recovers accounting and original due time', async t => {
  const f = await fixture(t); await f.enqueue();
  await killAt(f, 'provider-committed', { mode: 'transient', now: 10 });
  assert.equal((await f.run('status')).jobs[0].attempts, 1);
  assert.equal((await f.run('work', { now: 10 })).status, 'pending');
  assert.deepEqual(await f.run('work', { now: 11 }), { status: 'idle' });
  assert.equal((await f.run('work', { now: 12 })).status, 'delivered');
  assert.equal((await f.run('status')).jobs[0].attempts, 2);
});

test('arbitrary-size logical integers, parsed extreme JSON numbers and special keys survive', async t => {
  const f = await fixture(t);
  const payload = '{"__proto__":{"safe":true},"huge":1e999,"negative":-1e999}';
  await f.run('enqueue', { key: 'extreme', payload });
  await f.run('enqueue', { key: 'extreme', payload: '{"negative":-2e999,"huge":2e999,"__proto__":{"safe":true}}' });
  await f.run('enqueue', { key: 'extreme', payload: '{"huge":null}' }, true);
  const now = 900719925474099234567890n;
  assert.equal((await f.run('work', { now: String(now), mode: 'transient' })).status, 'pending');
  assert.deepEqual(await f.run('work', { now: String(now + 1n) }), { status: 'idle' });
  assert.equal((await f.run('work', { now: String(now + 2n) })).status, 'delivered');
  assert.deepEqual((await f.run('provider')).accepted[0].payload, JSON.parse(payload));
});

test('concurrent enqueue and workers do not lose jobs or cross tenants', async t => {
  const f = await fixture(t);
  const replay = await Promise.all(Array.from({ length: 14 }, () => f.enqueue('same', { a: 1 })));
  assert.equal(new Set(replay.map(x => x.id)).size, 1);
  await Promise.all(Array.from({ length: 16 }, (_, i) => f.enqueue('k' + i, { i }, i % 2 ? 'a' : 'b')));
  await Promise.all(Array.from({ length: 22 }, (_, i) => f.run('work', { tenant: i % 2 ? 'a' : 'b' })));
  for (const tenant of ['a', 'b']) {
    const s = await f.run('status', { tenant });
    assert.equal(s.pending + s.uncertain + s.dead, 0);
    assert.equal(s.delivered, tenant === 'a' ? 9 : 8);
    assert.ok(s.jobs.every(j => j.attempts === 1));
    assert.equal((await f.run('provider', { tenant })).accepted.length, s.delivered);
  }
  assert.deepEqual(await fs.readdir(path.join(f.store, '.locks')), []);
  assert.deepEqual(await fs.readdir(path.join(f.provider, '.locks')), []);
});

test('provider deduplicates across independent local stores and refuses changed payload', async t => {
  const f = await fixture(t);
  const other = path.join(f.base, 'second-local');
  await f.enqueue('k', { a: 1, b: 2 });
  await f.run('enqueue', { store: other, key: 'k', payload: { b: 2, a: 1 } });
  await Promise.all([f.run('work'), f.run('work', { store: other })]);
  assert.equal((await f.run('provider')).accepted.length, 1);
  const changed = path.join(f.base, 'changed-local');
  await f.run('enqueue', { store: changed, key: 'k', payload: { a: 2 } });
  const truth = await fs.readFile(path.join(f.provider, 'state.json'));
  assert.match((await f.run('work', { store: changed }, true)).error, /conflict/i);
  assert.deepEqual(await fs.readFile(path.join(f.provider, 'state.json')), truth);
  await f.enqueue('k', { a: 7 }, 'b'); await f.run('work', { tenant: 'b' });
  assert.equal((await f.run('provider', { tenant: 'b' })).accepted.length, 1);
});

test('invalid arguments and malformed persistence fail visibly; snapshots can restore', async t => {
  const f = await fixture(t);
  for (const payload of ['[]', 'null', '4', '{']) await f.run('enqueue', { key: 'k', payload }, true);
  await f.run('enqueue', { key: ' ', payload: {} }, true);
  await f.run('status', { tenant: ' ' }, true);
  for (const now of ['1.5', 'abc']) await f.run('work', { now }, true);
  await f.run('work', { mode: 'unknown' }, true);
  await f.run('work', { crash: 'unknown' }, true);
  await f.run('work', { provider: f.store }, true);
  await f.enqueue(); await f.run('work');
  const localBytes = await fs.readFile(path.join(f.store, 'state.json'));
  const providerBytes = await fs.readFile(path.join(f.provider, 'state.json'));
  for (const bad of ['{', '{}', '{"version":1,"kind":"local","jobs":[{}]}']) {
    await fs.writeFile(path.join(f.store, 'state.json'), bad);
    await f.run('status', {}, true);
    await f.run('enqueue', { key: 'new', payload: {} }, true);
    assert.equal(await fs.readFile(path.join(f.store, 'state.json'), 'utf8'), bad);
  }
  await fs.writeFile(path.join(f.store, 'state.json'), localBytes);
  await fs.writeFile(path.join(f.provider, 'state.json'), '{"version":1,"kind":"provider","accepted":[],"calls":[{}]}');
  await f.run('provider', {}, true);
  await fs.writeFile(path.join(f.provider, 'state.json'), providerBytes);
  assert.equal((await f.run('status')).delivered, 1);
  assert.equal((await f.run('provider')).accepted.length, 1);
  // Assertion challenge: the checker must reject a deliberately wrong count.
  assert.throws(() => assert.equal((JSON.parse(localBytes)).jobs.length, 2), assert.AssertionError);
});
