import { randomUUID } from 'node:crypto';
import { writeSync } from 'node:fs';
import { withStore, separateDirectories } from './store.mjs';

export const statuses = ['pending', 'uncertain', 'delivered', 'dead'];
const modes = ['ok', 'accepted-timeout', 'reject', 'transient'];
export function nonblank(value) { return typeof value === 'string' && value.trim().length > 0; }
function object(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
export function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (object(value)) return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  return JSON.stringify(value);
}
function same(a, b) { return canonical(a) === canonical(b); }
function identity(records, tenant, key) { return records.find(r => r.tenant === tenant && r.key === key); }
function fields(value, keys) {
  return object(value) && Object.keys(value).sort().join(',') === [...keys].sort().join(',');
}
export function validate(state, kind) {
  if (!fields(state, ['version', 'kind', 'records']) || state.version !== 1 || state.kind !== kind || !Array.isArray(state.records)) throw new Error('Malformed or unsupported store');
  const ids = new Set(), identities = new Set();
  for (const r of state.records) {
    const base = ['id', 'tenant', 'key', 'payload'];
    const keys = kind === 'local' ? [...base, 'status', 'attempts', 'due', 'deliveryId'] : base;
    const ident = JSON.stringify([r?.tenant, r?.key]);
    if (!fields(r, keys) || !nonblank(r.id) || !nonblank(r.tenant) || !nonblank(r.key) || !object(r.payload) || ids.has(r.id) || identities.has(ident)) throw new Error('Malformed persisted record');
    ids.add(r.id); identities.add(ident);
    if (kind === 'local' && (!statuses.includes(r.status) || !Number.isSafeInteger(r.attempts) || r.attempts < 0 || r.attempts > 3 || !(r.due === null || Number.isSafeInteger(r.due)) || !(r.deliveryId === null || nonblank(r.deliveryId)) || (r.status === 'delivered') !== (r.deliveryId !== null) || (r.status !== 'pending' && r.due !== null) || (r.status === 'pending' && r.attempts >= 3))) throw new Error('Malformed persisted job state');
  }
}
function abruptCrash(point) {
  writeSync(1, JSON.stringify({ error: 'Injected crash: ' + point }) + '\n');
  process.kill(process.pid, 'SIGKILL');
}
function tenantCheck(tenant) { if (!nonblank(tenant)) throw new Error('tenant must be nonblank'); }
export function enqueue(store, tenant, key, payload) {
  tenantCheck(tenant);
  if (!nonblank(key) || !object(payload)) throw new Error('key must be nonblank and payload must be a JSON object');
  return withStore(store, 'local', validate, (state, save) => {
    const existing = identity(state.records, tenant, key);
    if (existing) {
      if (!same(existing.payload, payload)) throw new Error('Identity payload conflict');
      return { id: existing.id, status: existing.status };
    }
    const job = { id: randomUUID(), tenant, key, payload, status: 'pending', attempts: 0, due: null, deliveryId: null };
    state.records.push(job); save();
    return { id: job.id, status: job.status };
  });
}
export function status(store, tenant) {
  tenantCheck(tenant);
  return withStore(store, 'local', validate, state => {
    const jobs = state.records.filter(r => r.tenant === tenant);
    return { ...Object.fromEntries(statuses.map(s => [s, jobs.filter(j => j.status === s).length])), jobs: jobs.map(({ id, key, status, attempts }) => ({ id, key, status, attempts })) };
  });
}
export function provider(providerStore, tenant) {
  tenantCheck(tenant);
  return withStore(providerStore, 'provider', validate, state => ({ accepted: state.records.filter(r => r.tenant === tenant).map(({ id, key, payload }) => ({ id, key, payload })) }));
}

// checkpoint is internal test instrumentation, never a public CLI option.
export function work(store, providerStore, tenant, now, mode = 'ok', crash, checkpoint = () => {}) {
  tenantCheck(tenant);
  if (!Number.isSafeInteger(now) || now > Number.MAX_SAFE_INTEGER - 4) throw new Error('now must be a safe integer with room for retry delays');
  if (!modes.includes(mode) || (crash !== undefined && !['before-send', 'after-accept'].includes(crash))) throw new Error('Invalid mode or crash');
  const [localDir, providerDir] = separateDirectories(store, providerStore);
  return withStore(localDir, 'local', validate, (local, saveLocal) => {
    const job = local.records.find(j => j.tenant === tenant && (j.status === 'uncertain' || (j.status === 'pending' && (j.due === null || j.due <= now))));
    if (!job) return { status: 'idle' };
    const result = () => ({ status: job.status, id: job.id });
    return withStore(providerDir, 'provider', validate, (remote, saveRemote) => {
      const accepted = identity(remote.records, tenant, job.key);
      if (accepted && !same(accepted.payload, job.payload)) throw new Error('Provider identity payload conflict');
      if (accepted) {
        job.status = 'delivered'; job.due = null; job.deliveryId = accepted.id;
        saveLocal(); return result();
      }
      if (job.attempts >= 3) {
        job.status = 'dead'; job.due = null; saveLocal(); return result();
      }
      job.status = 'uncertain'; job.due = null;
      saveLocal(); // Durable claim before any actual attempt.
      checkpoint('claimed');
      if (crash === 'before-send') abruptCrash(crash);

      // Start of the fake adapter invocation. Count even rejection/temporary failure.
      job.attempts++; saveLocal();
      checkpoint('attempted');
      if (mode === 'ok' || mode === 'accepted-timeout') {
        const delivery = { id: randomUUID(), tenant, key: job.key, payload: job.payload };
        remote.records.push(delivery); saveRemote();
        checkpoint('accepted');
        if (crash === 'after-accept') abruptCrash(crash);
        if (mode === 'ok') { job.status = 'delivered'; job.deliveryId = delivery.id; }
      } else if (mode === 'reject') {
        job.status = 'dead';
      } else if (job.attempts === 3) {
        job.status = 'dead';
      } else {
        job.status = 'pending'; job.due = now + 2 ** job.attempts;
      }
      saveLocal(); return result();
    });
  });
}
