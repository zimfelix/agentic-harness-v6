import { randomUUID } from 'node:crypto';
import { writeSync } from 'node:fs';
import { withLocal, transaction, attachProvider, openStore, parsePayload } from './storage.mjs';

export function enqueue({ store, tenant, key, payload }) {
  return withLocal(store, db => transaction(db, () => {
    const existing = db.prepare('SELECT id,status,payload FROM jobs WHERE tenant=? AND key=?').get(tenant, key);
    if (existing) {
      if (existing.payload !== payload) throw new Error('Identity conflicts with a different payload');
      return { id: existing.id, status: existing.status };
    }
    const id = randomUUID();
    db.prepare('INSERT INTO jobs(id,tenant,key,payload,status) VALUES (?,?,?,?,?)').run(id, tenant, key, payload, 'pending');
    return { id, status: 'pending' };
  }));
}

export function status({ store, tenant }) {
  return withLocal(store, db => {
    const jobs = db.prepare('SELECT id,key,status,attempts FROM jobs WHERE tenant=? ORDER BY seq').all(tenant);
    const result = { pending: 0, uncertain: 0, delivered: 0, dead: 0, jobs };
    for (const job of jobs) result[job.status]++;
    return result;
  });
}

export function providerTruth({ provider, tenant }) {
  const db = openStore(provider, 'provider');
  try {
    return { accepted: db.prepare('SELECT id,key,payload FROM accepted WHERE tenant=? ORDER BY seq').all(tenant)
      .map(row => ({ ...row, payload: parsePayload(row.payload) })) };
  } finally { db.close(); }
}

function crash(point) {
  writeSync(1, `${JSON.stringify({ error: `Injected crash ${point}` })}\n`);
  process.kill(process.pid, 'SIGKILL');
}

function acceptance(db, job) {
  const row = db.prepare('SELECT id,payload FROM remote.accepted WHERE tenant=? AND key=?').get(job.tenant, job.key);
  if (row && row.payload !== job.payload) throw new Error('Provider identity conflicts with a different payload');
  return row;
}

function delivered(db, job, id) {
  transaction(db, () => db.prepare("UPDATE jobs SET status='delivered',provider_id=? WHERE id=?").run(id, job.id));
  return { status: 'delivered', id: job.id };
}

export function work({ store, provider, tenant, now, mode = 'ok', crash: crashPoint }) {
  return withLocal(store, db => {
    attachProvider(db, store, provider);
    const job = db.prepare(`SELECT * FROM jobs WHERE tenant=? AND status IN ('pending','uncertain') ORDER BY seq`).all(tenant)
      .find(row => row.status === 'uncertain' || row.retry_at === null || BigInt(row.retry_at) <= now);
    if (!job) return { status: 'idle' };
    if (job.status === 'uncertain') {
      const existing = acceptance(db, job);
      if (existing) return delivered(db, job, existing.id);
    }
    if (job.attempts >= 3) {
      transaction(db, () => db.prepare("UPDATE jobs SET status='dead' WHERE id=?").run(job.id));
      return { status: 'dead', id: job.id };
    }
    // Claim is durable independently of the invocation, but consumes no attempt.
    transaction(db, () => db.prepare("UPDATE jobs SET status='uncertain' WHERE id=?").run(job.id));
    if (crashPoint === 'before-send') crash(crashPoint);

    // This transaction IS the fake-provider invocation boundary. The local
    // attempt and provider effect commit together, even if killed mid-commit.
    const response = transaction(db, () => {
      db.prepare('UPDATE jobs SET attempts=attempts+1 WHERE id=?').run(job.id);
      const existing = acceptance(db, job);
      if (existing) return { accepted: true, id: existing.id };
      if (mode === 'reject') {
        db.prepare("UPDATE jobs SET status='dead' WHERE id=?").run(job.id);
        return { status: 'dead' };
      }
      if (mode === 'transient') {
        const attempts = job.attempts + 1;
        const status = attempts === 3 ? 'dead' : 'pending';
        const next = status === 'dead' ? now : now + (attempts === 1 ? 2n : 4n);
        db.prepare('UPDATE jobs SET status=?,retry_at=? WHERE id=?').run(status, next.toString(), job.id);
        return { status };
      }
      const id = randomUUID();
      db.prepare('INSERT INTO remote.accepted(id,tenant,key,payload) VALUES (?,?,?,?)').run(id, job.tenant, job.key, job.payload);
      return { accepted: true, id };
    });
    if (!response.accepted) return { status: response.status, id: job.id };
    if (crashPoint === 'after-accept') crash(crashPoint);
    if (mode === 'accepted-timeout') return { status: 'uncertain', id: job.id };
    return delivered(db, job, response.id);
  });
}
