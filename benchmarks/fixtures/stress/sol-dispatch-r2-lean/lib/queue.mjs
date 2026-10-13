import { randomUUID } from 'node:crypto';
import { load, save, locked } from './storage.mjs';
import { emptyQueue, validateQueue, equal, requireThat, statuses } from './model.mjs';
import { truth, invoke } from './provider.mjs';
import { crashAt } from './crash.mjs';

const loadQueue = dir => load(dir, 'queue', emptyQueue, validateQueue);
export async function enqueue(dir, tenant, key, payload) {
  return locked(dir, async () => {
    const s = await loadQueue(dir);
    const existing = s.jobs.find(j => j.tenant === tenant && j.key === key);
    if (existing) {
      requireThat(equal(existing.payload, payload), 'Identity payload conflict');
      return { id: existing.id, status: existing.status };
    }
    const job = { id: randomUUID(), tenant, key, payload, status: 'pending', attempts: 0,
      due: null, provider: null, deliveryId: null, claim: null };
    s.jobs.push(job);
    await save(dir, s);
    return { id: job.id, status: job.status };
  });
}

function receiptResult(job, receipt, uncertain) {
  job.attempts++;
  job.claim = null;
  job.due = null;
  if (receipt.outcome === 'accepted') {
    job.status = uncertain ? 'uncertain' : 'delivered';
    job.deliveryId = uncertain ? null : receipt.deliveryId;
  } else if (receipt.outcome === 'reject' || job.attempts === 3) job.status = 'dead';
  else {
    job.status = 'pending';
    job.due = String(BigInt(receipt.now) + (job.attempts === 1 ? 2n : 4n));
  }
}

// A lock spans the entire worker. Thus any claim visible to this owner was
// abandoned. Receipts distinguish a durable provider invocation from a crash
// before sending, without guessing from leases or local intent counters.
async function recoverClaims(s, tenant) {
  let changed = false;
  for (const j of s.jobs.filter(j => j.tenant === tenant && j.claim)) {
    const { receipt } = await truth(j.provider, j, false);
    if (receipt) receiptResult(j, receipt, true);
    else j.claim = null;
    changed = true;
  }
  return changed;
}

export async function status(dir, tenant) {
  return locked(dir, async () => {
    const s = await loadQueue(dir);
    if (await recoverClaims(s, tenant)) await save(dir, s);
    const jobs = s.jobs.filter(j => j.tenant === tenant);
    return { ...Object.fromEntries(statuses.map(k => [k, jobs.filter(j => j.status === k).length])),
      jobs: jobs.map(({ id, key, status, attempts }) => ({ id, key, status, attempts })) };
  });
}

export async function work(dir, provider, tenant, now, mode, crash) {
  return locked(dir, async () => {
    const s = await loadQueue(dir);
    let clock = s.clocks.find(c => c.tenant === tenant);
    requireThat(!clock || BigInt(now) >= BigInt(clock.now), 'Logical time must not decrease for a tenant');
    // Reject an incompatible provider before recovering or altering any job.
    for (const j of s.jobs.filter(j => j.tenant === tenant && ['pending', 'uncertain'].includes(j.status))) {
      requireThat(j.provider === null || j.provider === provider, 'Job is bound to a different provider directory');
    }
    await recoverClaims(s, tenant);
    if (clock) clock.now = now;
    else { clock = { tenant, now }; s.clocks.push(clock); }
    const job = s.jobs.find(j => j.tenant === tenant && (j.status === 'uncertain' ||
      (j.status === 'pending' && (j.due === null || BigInt(j.due) <= BigInt(now)))));
    if (!job) { await save(dir, s); return { status: 'idle' }; }
    if (job.status === 'uncertain') {
      const { accepted } = await truth(provider, job);
      if (accepted) {
        job.status = 'delivered';
        job.deliveryId = accepted.id;
        job.due = null;
        await save(dir, s);
        return { status: job.status, id: job.id };
      }
    }
    if (job.attempts >= 3) {
      job.status = 'dead';
      job.due = null;
      await save(dir, s);
      return { status: job.status, id: job.id };
    }
    job.status = 'uncertain';
    job.due = null;
    job.provider = provider;
    job.claim = { token: randomUUID(), now };
    await save(dir, s);
    if (crash === 'before-send') crashAt('before-send');
    const receipt = await invoke(provider, job, mode, crash);
    receiptResult(job, receipt, mode === 'accepted-timeout');
    await save(dir, s);
    return { status: job.status, id: job.id };
  });
}
