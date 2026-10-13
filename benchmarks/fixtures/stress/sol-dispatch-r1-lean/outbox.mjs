import { randomUUID } from 'node:crypto';
import { writeSync } from 'node:fs';
import path from 'node:path';
import { realpath } from 'node:fs/promises';
import { directory, locked, load, save, object, blank, equal } from './storage.mjs';

const statuses = ['pending', 'uncertain', 'delivered', 'dead'];
const modes = ['ok', 'accepted-timeout', 'reject', 'transient'];
const identity = (a, b) => a.tenant === b.tenant && a.key === b.key;
const validIdentity = x => object(x) && !blank(x.id) && !blank(x.tenant) && !blank(x.key) && object(x.payload);
const unique = (xs, key) => new Set(xs.map(key)).size === xs.length;
const identityKey = x => JSON.stringify([x.tenant, x.key]);
const integer = n => Number.isSafeInteger(n);
const logical = n => typeof n === 'string' && /^-?(0|[1-9]\d*)$/.test(n);
function validLocal(s) {
  return Array.isArray(s.jobs) && unique(s.jobs, identityKey) && unique(s.jobs, x => x.id) && s.jobs.every(j =>
    validIdentity(j) && statuses.includes(j.status) && integer(j.attempts) && j.attempts >= 0 && j.attempts <= 3 &&
    (j.due === null || (j.status === 'pending' && logical(j.due))) &&
    (j.deliveryId === null || !blank(j.deliveryId)) &&
    (j.status !== 'delivered' || j.deliveryId !== null) &&
    (j.status !== 'pending' || (j.attempts < 3 && j.deliveryId === null)) &&
    (j.status !== 'dead' || (j.attempts > 0 && j.deliveryId === null)) &&
    (j.status !== 'uncertain' || j.claim !== null || j.deliveryId !== null) &&
    (j.claim === null || (j.status === 'uncertain' && j.attempts < 3 && j.deliveryId === null && object(j.claim) && !blank(j.claim.token) && !blank(j.claim.provider) && path.isAbsolute(j.claim.provider) && logical(j.claim.now) && modes.includes(j.claim.mode))));
}
function validProvider(s) {
  return Array.isArray(s.accepted) && unique(s.accepted, identityKey) && unique(s.accepted, x => x.id) && s.accepted.every(validIdentity) &&
    Array.isArray(s.calls) && unique(s.calls, x => x.token) && s.calls.every(c => object(c) && !blank(c.token) && !blank(c.jobId) && !blank(c.tenant) && !blank(c.key) && modes.includes(c.mode) && logical(c.now) && (c.deliveryId === null || !blank(c.deliveryId)) &&
      ((c.mode === 'ok' || c.mode === 'accepted-timeout') ? s.accepted.some(a => identity(a, c) && a.id === c.deliveryId) : c.deliveryId === null));
}
const local = dir => load(dir, 'local', validLocal);
async function provider(dir) {
  // Empty provider is initialized with its call ledger as well as acceptances.
  const s = await load(dir, 'provider', validProvider);
  if (!Object.hasOwn(s, 'calls')) s.calls = [];
  return s;
}
function crash(name, code) {
  writeSync(1, JSON.stringify({ error: `Simulated crash: ${name}` }) + '\n');
  process.exit(code); // intentionally bypass cleanup: restart must recover ownership
}
async function phase(name) {
  // IPC instrumentation used by OS-kill tests; normal CLI has no IPC channel.
  if (process.send) {
    await new Promise((resolve, reject) => {
      process.once('message', resolve);
      process.send({ phase: name }, e => { if (e) reject(e); });
    });
  }
}
function applyCall(job, call) {
  job.attempts++;
  job.claim = null;
  job.due = null;
  if (call.deliveryId) {
    job.deliveryId = call.deliveryId;
    job.status = call.mode === 'accepted-timeout' ? 'uncertain' : 'delivered';
  } else if (call.mode === 'reject' || job.attempts >= 3) job.status = 'dead';
  else { job.status = 'pending'; job.due = String(BigInt(call.now) + (2n ** BigInt(job.attempts))); }
}
async function inspect(dir, job) {
  return locked(dir, async () => {
    const p = await provider(dir);
    const accepted = p.accepted.find(a => identity(a, job));
    if (accepted && !equal(accepted.payload, job.payload)) throw new Error('Provider identity payload conflict');
    const call = job.claim && p.calls.find(c => c.token === job.claim.token);
    if (call && (call.jobId !== job.id || !identity(call, job))) throw new Error('Provider call identity conflict');
    return { accepted, call };
  });
}
export async function dispatch(command, options) {
  const tenant = options.tenant;
  if (blank(tenant)) throw new Error('tenant must be nonblank');
  if (command === 'provider') {
    const dir = await directory(options.provider);
    return locked(dir, async () => ({ accepted: (await provider(dir)).accepted.filter(a => a.tenant === tenant).map(({ id, key, payload }) => ({ id, key, payload })) }));
  }
  const dir = await directory(options.store);
  let providerDir;
  if (command === 'work') {
    providerDir = await directory(options.provider);
    if (providerDir === dir) throw new Error('Local and provider stores must be separate directories');
  }
  return locked(dir, async () => {
    const state = await local(dir);
    if (command === 'enqueue') {
      const old = state.jobs.find(j => j.tenant === tenant && j.key === options.key);
      if (old) {
        if (!equal(old.payload, options.payload)) throw new Error('Identity payload conflict');
        return { id: old.id, status: old.status };
      }
      const job = { id: randomUUID(), tenant, key: options.key, payload: options.payload, status: 'pending', attempts: 0, due: null, deliveryId: null, claim: null };
      state.jobs.push(job);
      await save(dir, state);
      return { id: job.id, status: job.status };
    }
    if (command === 'status') {
      const result = { pending: 0, uncertain: 0, delivered: 0, dead: 0, jobs: [] };
      for (const j of state.jobs.filter(j => j.tenant === tenant)) {
        let attempts = j.attempts;
        // A killed sender may have committed the actual invocation receipt but
        // not its local counter. Reads report that receipt without changing state.
        if (j.claim) {
          const claimDir = await realpath(j.claim.provider);
          if (claimDir === dir || claimDir !== j.claim.provider) throw new Error('Invalid claim provider directory');
          const { call } = await inspect(j.claim.provider, j);
          if (call) attempts++;
        }
        result[j.status]++;
        result.jobs.push({ id: j.id, key: j.key, status: j.status, attempts });
      }
      return result;
    }
    const now = options.now;
    const job = state.jobs.find(j => j.tenant === tenant && (j.status === 'uncertain' || (j.status === 'pending' && (j.due === null || BigInt(j.due) <= BigInt(now)))));
    if (!job) return { status: 'idle' };
    const result = () => ({ status: job.status, id: job.id });
    if (job.status === 'uncertain') {
      if (job.claim && job.claim.provider !== providerDir) throw new Error('Recovery requires original provider directory');
      const { accepted, call } = await inspect(providerDir, job);
      if (call) applyCall(job, call);
      if (accepted) {
        job.status = 'delivered'; job.deliveryId = accepted.id; job.claim = null; job.due = null;
        await save(dir, state);
        return result();
      }
      if (call) { await save(dir, state); return result(); }
      // No invocation receipt: ownership died before the fake provider call.
      job.claim = null;
      if (job.attempts >= 3) {
        job.status = 'dead'; job.deliveryId = null; await save(dir, state); return result();
      }
    }
    job.status = 'uncertain';
    job.deliveryId = null;
    job.claim = { token: randomUUID(), provider: providerDir, mode: options.mode, now };
    await save(dir, state);
    await phase('claimed');
    if (options.crash === 'before-send') crash('before-send', 71);
    const call = await locked(providerDir, async () => {
      const p = await provider(providerDir);
      let accepted = p.accepted.find(a => identity(a, job));
      if (accepted && !equal(accepted.payload, job.payload)) throw new Error('Provider identity payload conflict');
      if (options.mode === 'ok' || options.mode === 'accepted-timeout' || options.crash === 'after-accept') {
        if (!accepted) { accepted = { id: randomUUID(), tenant, key: job.key, payload: job.payload }; p.accepted.push(accepted); }
      }
      const c = { token: job.claim.token, jobId: job.id, tenant, key: job.key, mode: accepted && ['reject', 'transient'].includes(options.mode) ? 'ok' : options.mode, now, deliveryId: accepted?.id ?? null };
      p.calls.push(c);
      await save(providerDir, p);
      await phase('provider-committed');
      if (options.crash === 'after-accept') crash('after-accept', 72);
      return c;
    });
    applyCall(job, call);
    await save(dir, state);
    return result();
  });
}
