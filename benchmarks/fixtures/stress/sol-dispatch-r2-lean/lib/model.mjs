export const statuses = ['pending', 'uncertain', 'delivered', 'dead'];
export const modes = ['ok', 'accepted-timeout', 'reject', 'transient'];
export const integer = value => typeof value === 'string' && /^-?(0|[1-9][0-9]*)$/.test(value);
export const nonblank = value => typeof value === 'string' && value.trim().length > 0;
export const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
export function requireThat(condition, message = 'Invalid state') {
  if (!condition) throw new Error(message);
}
export function canonical(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (object(value)) return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  requireThat(['string', 'boolean', 'number'].includes(typeof value));
  if (typeof value === 'number') requireThat(Number.isFinite(value), 'Payload numbers must be finite');
  return JSON.stringify(value);
}
export const equal = (a, b) => canonical(a) === canonical(b);
export const identity = (tenant, key) => JSON.stringify([tenant, key]);
export const emptyQueue = () => ({ version: 1, kind: 'queue', clocks: [], jobs: [] });
export const emptyProvider = () => ({ version: 1, kind: 'provider', accepted: [], receipts: [] });
function base(s, kind) { requireThat(object(s) && s.version === 1 && s.kind === kind); }
function unique(list, key) {
  requireThat(new Set(list.map(key)).size === list.length);
}
export function validateQueue(s) {
  base(s, 'queue');
  requireThat(Array.isArray(s.clocks) && Array.isArray(s.jobs));
  for (const c of s.clocks) requireThat(object(c) && nonblank(c.tenant) && integer(c.now));
  unique(s.clocks, c => c.tenant);
  for (const j of s.jobs) {
    requireThat(object(j) && nonblank(j.id) && nonblank(j.tenant) && nonblank(j.key) && object(j.payload));
    canonical(j.payload);
    requireThat(statuses.includes(j.status) && Number.isInteger(j.attempts) && j.attempts >= 0 && j.attempts <= 3);
    requireThat(j.due === null || integer(j.due));
    requireThat(j.provider === null || nonblank(j.provider));
    requireThat(j.deliveryId === null || nonblank(j.deliveryId));
    requireThat((j.status === 'delivered') === (j.deliveryId !== null));
    requireThat(j.status !== 'pending' || j.attempts < 3);
    requireThat(j.due === null || j.status === 'pending');
    requireThat(j.status !== 'pending' || (j.attempts === 0 ? j.due === null : j.due !== null));
    requireThat(j.status !== 'dead' || j.attempts > 0);
    requireThat(j.status === 'pending' && j.attempts === 0 || j.provider !== null);
    requireThat(j.claim === null || (object(j.claim) && nonblank(j.claim.token) && integer(j.claim.now) &&
      j.status === 'uncertain' && j.provider !== null && j.attempts < 3));
  }
  unique(s.jobs, j => j.id);
  unique(s.jobs, j => identity(j.tenant, j.key));
}
export function validateProvider(s) {
  base(s, 'provider');
  requireThat(Array.isArray(s.accepted) && Array.isArray(s.receipts));
  for (const a of s.accepted) {
    requireThat(object(a) && nonblank(a.id) && nonblank(a.tenant) && nonblank(a.key) && object(a.payload));
    canonical(a.payload);
  }
  unique(s.accepted, a => identity(a.tenant, a.key));
  unique(s.accepted, a => a.id);
  unique(s.receipts, r => r.token);
  for (const r of s.receipts) {
    requireThat(object(r) && nonblank(r.token) && nonblank(r.tenant) && nonblank(r.key) &&
      object(r.payload) && integer(r.now) && ['accepted', 'reject', 'transient'].includes(r.outcome));
    canonical(r.payload);
    requireThat(r.deliveryId === null || nonblank(r.deliveryId));
    if (r.outcome === 'accepted') {
      const a = s.accepted.find(a => a.id === r.deliveryId);
      requireThat(a && a.tenant === r.tenant && a.key === r.key && equal(a.payload, r.payload));
    } else requireThat(r.deliveryId === null);
  }
}
