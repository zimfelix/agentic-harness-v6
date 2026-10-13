import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
test('repeated before-send deaths preserve retry budget at the same logical time', t => {
  mkdirSync(join(root, '.test-data'), { recursive: true });
  const base = mkdtempSync(join(root, '.test-data', 'recovery-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const store = join(base, 'local'); const provider = join(base, 'provider');
  function call(cmd, extra = {}, killed = false) {
    const options = cmd === 'enqueue' ? { store, tenant: 't', key: 'k', payload: '{}' }
      : cmd === 'status' ? { store, tenant: 't' }
        : { store, provider, tenant: 't', now: 4, ...extra };
    const result = spawnSync(process.execPath, [join(root, 'app.mjs'), cmd, ...Object.entries(options).flatMap(([k, v]) => [`--${k}`, String(v)])], { encoding: 'utf8' });
    if (killed) assert.equal(result.signal, 'SIGKILL'); else assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.equal(result.stdout.trim().split('\n').length, 1);
    return JSON.parse(result.stdout);
  }
  call('enqueue');
  call('work', { now: 0, mode: 'transient' });
  call('work', { now: 2, mode: 'transient' }); // Second due time is 6.
  assert.equal(call('work', { now: 5, crash: 'before-send' }).status, 'idle');
  for (let i = 0; i < 3; i++) {
    call('work', { now: 6, crash: 'before-send' }, true);
    assert.equal(call('status').jobs[0].attempts, 2);
  }
  assert.equal(call('work', { now: 6, mode: 'accepted-timeout' }).status, 'uncertain');
  assert.equal(call('status').jobs[0].attempts, 3);
  assert.equal(call('work', { now: 6 }).status, 'delivered');
  assert.equal(call('status').jobs[0].attempts, 3);
});

test('logical retry clock preserves integers beyond JavaScript Number precision', t => {
  mkdirSync(join(root, '.test-data'), { recursive: true });
  const base = mkdtempSync(join(root, '.test-data', 'big-clock-'));
  t.after(() => rmSync(base, { recursive: true, force: true }));
  const store = join(base, 'local'); const provider = join(base, 'provider');
  function call(command, options) {
    const result = spawnSync(process.execPath, [join(root, 'app.mjs'), command,
      ...Object.entries(options).flatMap(([k, v]) => [`--${k}`, String(v)])], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    return JSON.parse(result.stdout);
  }
  call('enqueue', { store, tenant: 't', key: 'k', payload: '{}' });
  const n = 99999999999999999999999999999999999999n;
  const options = { store, provider, tenant: 't' };
  assert.equal(call('work', { ...options, now: n, mode: 'transient' }).status, 'pending');
  assert.equal(call('work', { ...options, now: n + 1n }).status, 'idle');
  assert.equal(call('work', { ...options, now: n + 2n }).status, 'delivered');
});
