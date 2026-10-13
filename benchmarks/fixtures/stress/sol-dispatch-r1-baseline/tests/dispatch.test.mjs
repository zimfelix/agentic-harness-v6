import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn, fork } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, cpSync, readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { canonical, validate } from '../src/dispatch.mjs';

const root = resolve(import.meta.dirname, '..');
function fixture(t) {
  const dir = mkdtempSync(join(root, 'tests', '.run-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return { dir, local: join(dir, 'local'), remote: join(dir, 'remote') };
}
function run(args, { crash = false } = {}) {
  return new Promise((resolveResult, reject) => {
    const child = spawn(process.execPath, ['app.mjs', ...args], { cwd: root });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => stdout += chunk);
    child.stderr.on('data', chunk => stderr += chunk);
    child.on('error', reject);
    child.on('close', (code, signal) => {
      try {
        const lines = stdout.trim().split('\n');
        assert.equal(lines.length, 1, stdout);
        const json = JSON.parse(lines[0]);
        assert.equal(typeof json, 'object'); assert.ok(json && !Array.isArray(json));
        if (crash) assert.equal(signal, 'SIGKILL');
        resolveResult({ code, signal, json, stderr });
      } catch (error) { reject(error); }
    });
  });
}
async function good(args) { const r = await run(args); assert.equal(r.code, 0, r.stderr + JSON.stringify(r.json)); return r.json; }
async function bad(args) { const r = await run(args); assert.notEqual(r.code, 0); assert.equal(typeof r.json.error, 'string'); return r; }
const enq = (s, key, payload = '{"x":1}', tenant = 'A') => ['enqueue', '--store', s.local, '--tenant', tenant, '--key', key, '--payload', payload];
const stat = (s, tenant = 'A') => ['status', '--store', s.local, '--tenant', tenant];
const truth = (s, tenant = 'A') => ['provider', '--provider', s.remote, '--tenant', tenant];
const work = (s, now = 7, mode = 'ok', tenant = 'A') => ['work', '--store', s.local, '--provider', s.remote, '--tenant', tenant, '--now', String(now), '--mode', mode];

// Unit boundaries complement CLI integration, including recursive semantic equality.
test('canonical structural semantics and strict snapshot validation', () => {
  assert.equal(canonical({ z: [{ b: 2, a: 1 }], a: -0 }), canonical({ a: 0, z: [{ a: 1, b: 2 }] }));
  assert.notEqual(canonical({ a: [1, 2] }), canonical({ a: [2, 1] }));
  assert.notEqual(canonical({}), canonical({ x: null }));
  assert.equal(canonical(JSON.parse('{"__proto__":{"z":1}}')), '{"__proto__":{"z":1}}');
  assert.throws(() => validate({ version: 2, kind: 'local', records: [] }, 'local'));
  assert.throws(() => validate({ version: 1, kind: 'local', records: [{ status: 'mystery' }] }, 'local'));
});

test('durable enqueue replay, semantic conflicts, tenant scope, delivered replay', async t => {
  const s = fixture(t);
  const first = await good(enq(s, 'k', '{"nested":{"b":2,"a":1},"list":[1,2]}'));
  assert.equal(first.status, 'pending');
  assert.deepEqual(await good(enq(s, 'k', '{"list":[1,2],"nested":{"a":1,"b":2}}')), first);
  const before = readFileSync(join(s.local, 'state.sqlite'));
  await bad(enq(s, 'k', '{"list":[2,1],"nested":{"a":1,"b":2}}'));
  assert.deepEqual(readFileSync(join(s.local, 'state.sqlite')), before);
  const other = await good(enq(s, 'k', '{"else":true}', 'B'));
  assert.notEqual(first.id, other.id);
  assert.deepEqual(await good(stat(s)), { pending: 1, uncertain: 0, delivered: 0, dead: 0, jobs: [{ id: first.id, key: 'k', status: 'pending', attempts: 0 }] });
  assert.deepEqual(await good(work(s).slice(0, -2)), { status: 'delivered', id: first.id });
  assert.equal((await good(enq(s, 'k', '{"nested":{"b":2,"a":1},"list":[1,2]}'))).status, 'delivered');
  const accepted = (await good(truth(s))).accepted;
  assert.equal(accepted.length, 1); assert.notEqual(accepted[0].id, first.id);
  assert.deepEqual(accepted[0].payload, { nested: { b: 2, a: 1 }, list: [1, 2] });
  assert.deepEqual(await good(truth(s, 'B')), { accepted: [] });
  assert.equal((await good(stat(s, 'B'))).jobs[0].id, other.id);
  assert.deepEqual(await good(work(s)), { status: 'idle' });
});

test('strict CLI validation and separated directories', async t => {
  const s = fixture(t);
  for (const payload of ['[]', 'null', '1', 'true', 'bad']) await bad(enq(s, 'k', payload));
  await bad(enq(s, ' ', '{}')); await bad(enq(s, 'k', '{}', '\t'));
  await bad(['unknown']); await bad(['status', '--store', s.local]);
  await bad([...stat(s), '--tenant', 'B']); await bad([...stat(s), '--unknown', 'x']);
  for (const now of ['1.2', '1e2', 'NaN', '9007199254740992']) await bad(work(s, now));
  await bad(work(s, 7, 'invalid')); await bad([...work(s), '--crash', 'invalid']);
  await bad(['work', '--store', s.local, '--provider', s.local, '--tenant', 'A', '--now', '7']);
  assert.equal((await good(stat(s))).jobs.length, 0);
});

test('oldest eligible, tenant isolation, retry schedule and three attempt ceiling', async t => {
  const s = fixture(t);
  const a = await good(enq(s, 'old'));
  const b = await good(enq(s, 'new'));
  await good(enq(s, 'foreign', '{}', 'B'));
  assert.deepEqual(await good(work(s, 10, 'transient')), { status: 'pending', id: a.id });
  // Oldest is not due, so the next eligible job may proceed.
  assert.deepEqual(await good(work(s, 11, 'reject')), { status: 'dead', id: b.id });
  assert.deepEqual(await good(work(s, 11)), { status: 'idle' });
  assert.equal((await good(stat(s))).jobs[0].attempts, 1);
  assert.equal((await good(work(s, 20, 'transient'))).status, 'pending');
  assert.deepEqual(await good(work(s, 23)), { status: 'idle' });
  assert.equal((await good(work(s, 24, 'transient'))).status, 'dead');
  const state = await good(stat(s));
  assert.equal(state.dead, 2); assert.equal(state.jobs[0].attempts, 3); assert.equal(state.jobs[1].attempts, 1);
  assert.equal((await good(stat(s, 'B'))).jobs[0].attempts, 0);
  assert.deepEqual(await good(truth(s)), { accepted: [] });
  assert.deepEqual(await good(work(s, 100)), { status: 'idle' });
});

test('transient retry can succeed and accepted timeout reconciles without increment', async t => {
  const s = fixture(t);
  await good(enq(s, 'k'));
  await good(work(s, 7, 'transient'));
  assert.equal((await good(work(s, 9, 'accepted-timeout'))).status, 'uncertain');
  const before = await good(truth(s)); assert.equal(before.accepted.length, 1);
  const state = await good(stat(s)); assert.equal(state.uncertain, 1); assert.equal(state.jobs[0].attempts, 2);
  assert.equal((await good(work(s, 9, 'reject'))).status, 'delivered');
  assert.equal((await good(stat(s))).jobs[0].attempts, 2);
  assert.deepEqual(await good(truth(s)), before);
});

test('injected crashes use SIGKILL and recover at identical logical time', async t => {
  const s = fixture(t);
  await good(enq(s, 'before'));
  await run([...work(s), '--crash', 'before-send'], { crash: true });
  assert.equal((await good(stat(s))).jobs[0].status, 'uncertain');
  assert.equal((await good(stat(s))).jobs[0].attempts, 0);
  assert.deepEqual(await good(truth(s)), { accepted: [] });
  assert.equal((await good(work(s))).status, 'delivered');
  await good(enq(s, 'after'));
  await run([...work(s), '--crash', 'after-accept'], { crash: true });
  const accepted = await good(truth(s)); assert.equal(accepted.accepted.length, 2);
  assert.equal((await good(work(s))).status, 'delivered');
  const jobs = (await good(stat(s))).jobs;
  assert.deepEqual(jobs.map(j => j.attempts), [1, 1]);
  assert.deepEqual(await good(truth(s)), accepted);
});

async function externallyKill(s, point) {
  const child = fork(join(root, 'tests/kill-worker.mjs'), [s.local, s.remote, point], { cwd: root, stdio: ['ignore', 'ignore', 'pipe', 'ipc'] });
  await new Promise((resolveReady, reject) => {
    const timer = setTimeout(() => { child.kill('SIGKILL'); reject(new Error('Checkpoint timeout')); }, 10000);
    child.once('error', reject);
    child.once('message', message => {
      clearTimeout(timer); assert.equal(message.stage, point); resolveReady();
    });
    child.once('exit', () => { clearTimeout(timer); reject(new Error('Exited before checkpoint')); });
  });
  const closed = new Promise(resolveClosed => child.once('exit', (code, signal) => resolveClosed({ code, signal })));
  child.kill('SIGKILL');
  assert.equal((await closed).signal, 'SIGKILL');
}

test('external real kill while local and provider locks are held', async t => {
  for (const point of ['claimed', 'accepted']) {
    const s = fixture(t); await good(enq(s, 'k'));
    await externallyKill(s, point);
    const state = await good(stat(s));
    assert.equal(state.jobs[0].status, 'uncertain');
    assert.equal(state.jobs[0].attempts, point === 'claimed' ? 0 : 1);
    assert.equal((await good(truth(s))).accepted.length, point === 'claimed' ? 0 : 1);
    assert.equal((await good(work(s))).status, 'delivered');
    assert.equal((await good(stat(s))).jobs[0].attempts, 1);
    assert.equal((await good(truth(s))).accepted.length, 1);
  }
});

test('third uncertain attempt reconciles acceptance or exhausts safely when absent', async t => {
  for (const accepted of [false, true]) {
    const s = fixture(t); await good(enq(s, 'k'));
    await good(work(s, 1, 'transient')); await good(work(s, 3, 'transient'));
    if (accepted) await good(work(s, 7, 'accepted-timeout'));
    else await externallyKill(s, 'attempted');
    assert.equal((await good(stat(s))).jobs[0].attempts, 3);
    assert.equal((await good(work(s, 7))).status, accepted ? 'delivered' : 'dead');
    assert.equal((await good(stat(s))).jobs[0].attempts, 3);
    assert.equal((await good(truth(s))).accepted.length, accepted ? 1 : 0);
  }
});

test('concurrent enqueue/worker processes preserve jobs, tenants and uniqueness', async t => {
  const s = fixture(t);
  const replays = await Promise.all(Array.from({ length: 10 }, () => good(enq(s, 'same'))));
  assert.equal(new Set(replays.map(r => r.id)).size, 1);
  await Promise.all(Array.from({ length: 12 }, (_, i) => good(enq(s, 'k' + i, '{"i":' + i + '}', i % 2 ? 'A' : 'B'))));
  // Enqueue races with work as well as workers racing each other.
  await Promise.all([
    ...Array.from({ length: 18 }, (_, i) => good(work(s, 7, 'ok', i % 2 ? 'A' : 'B'))),
    good(enq(s, 'late', '{}', 'B')),
  ]);
  await good(work(s, 7, 'ok', 'B'));
  const a = await good(stat(s)), b = await good(stat(s, 'B'));
  assert.equal(a.delivered, 7); assert.equal(b.delivered, 7);
  assert.ok([...a.jobs, ...b.jobs].every(j => j.attempts === 1));
  assert.equal((await good(truth(s))).accepted.length, 7);
  assert.equal((await good(truth(s, 'B'))).accepted.length, 7);
});

test('independent local stores share one provider dedup truth and detect payload conflict', async t => {
  const s = fixture(t); const second = { ...s, local: join(s.dir, 'second') };
  await Promise.all([good(enq(s, 'shared')), good(enq(second, 'shared'))]);
  await Promise.all([good(work(s)), good(work(second))]);
  assert.equal((await good(truth(s))).accepted.length, 1);
  const third = { ...s, local: join(s.dir, 'third') };
  await good(enq(third, 'shared', '{"x":2}'));
  const before = readFileSync(join(third.local, 'state.sqlite'));
  await bad(work(third));
  assert.deepEqual(readFileSync(join(third.local, 'state.sqlite')), before);
  assert.equal((await good(truth(s))).accepted.length, 1);
});

test('corrupt existing sqlite and malformed snapshots fail visibly without replacing data', async t => {
  const s = fixture(t); await good(enq(s, 'k')); await good(truth(s));
  const localFile = join(s.local, 'state.sqlite');
  const db = new DatabaseSync(localFile);
  db.prepare('UPDATE snapshot SET body=?').run('{"version":1,"kind":"local","records":[{}]}'); db.close();
  const before = readFileSync(localFile);
  await bad(stat(s)); await bad(enq(s, 'new')); await bad(work(s));
  assert.deepEqual(readFileSync(localFile), before);
  const remoteFile = join(s.remote, 'state.sqlite');
  writeFileSync(remoteFile, 'not sqlite'); await bad(truth(s));
  assert.equal(readFileSync(remoteFile, 'utf8'), 'not sqlite');
  const fresh = { ...s, local: join(s.dir, 'fresh') }; await good(enq(fresh, 'k'));
  const unclaimed = await good(stat(fresh));
  await bad(work(fresh)); assert.deepEqual(await good(stat(fresh)), unclaimed);
  writeFileSync(localFile, ''); await bad(stat(s));
});

test('backup and restore of both stopped stores preserves recovery truth', async t => {
  const s = fixture(t); await good(enq(s, 'k')); await good(work(s, 7, 'accepted-timeout'));
  const before = await good(truth(s));
  const restored = { local: join(s.dir, 'restore-local'), remote: join(s.dir, 'restore-remote') };
  cpSync(s.local, restored.local, { recursive: true }); cpSync(s.remote, restored.remote, { recursive: true });
  assert.equal((await good(work(restored))).status, 'delivered');
  assert.deepEqual(await good(truth(restored)), before);
  assert.equal((await good(stat(restored))).jobs[0].attempts, 1);
});
