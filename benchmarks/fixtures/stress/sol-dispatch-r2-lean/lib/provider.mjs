import { randomUUID } from 'node:crypto';
import { crashAt } from './crash.mjs';
import { load, save, locked } from './storage.mjs';
import { emptyProvider, validateProvider, equal, requireThat } from './model.mjs';

export const loadProvider = dir => load(dir, 'provider', emptyProvider, validateProvider);
export async function inspect(dir, tenant) {
  return locked(dir, async () => ({ accepted: (await loadProvider(dir)).accepted
    .filter(a => a.tenant === tenant).map(({ id, key, payload }) => ({ id, key, payload })) }));
}
export async function truth(dir, job, checkAcceptedPayload = true) {
  return locked(dir, async () => {
    const state = await loadProvider(dir);
    const accepted = state.accepted.find(a => a.tenant === job.tenant && a.key === job.key);
    if (accepted && checkAcceptedPayload) requireThat(equal(accepted.payload, job.payload), 'Provider identity payload conflict');
    const receipt = job.claim && state.receipts.find(r => r.token === job.claim.token);
    if (receipt) requireThat(receipt.tenant === job.tenant && receipt.key === job.key &&
      equal(receipt.payload, job.payload) && receipt.now === job.claim.now, 'Provider receipt conflict');
    return { accepted, receipt };
  });
}
export async function invoke(dir, job, mode, crash) {
  return locked(dir, async () => {
    const state = await loadProvider(dir);
    requireThat(!state.receipts.some(r => r.token === job.claim.token), 'Attempt token already invoked');
    let accepted = state.accepted.find(a => a.tenant === job.tenant && a.key === job.key);
    if (accepted) requireThat(equal(accepted.payload, job.payload), 'Provider identity payload conflict');
    if (!accepted && (mode === 'ok' || mode === 'accepted-timeout')) {
      accepted = { id: randomUUID(), tenant: job.tenant, key: job.key, payload: job.payload };
      state.accepted.push(accepted);
    }
    const receipt = {
      token: job.claim.token, tenant: job.tenant, key: job.key, payload: job.payload,
      now: job.claim.now, outcome: accepted ? 'accepted' : mode,
      deliveryId: accepted?.id ?? null,
    };
    state.receipts.push(receipt);
    await save(dir, state);
    if (crash === 'after-accept') crashAt('after-accept');
    return receipt;
  });
}
