import * as fs from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { setTimeout as delay } from 'node:timers/promises';

export const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
export function canonical(x) {
  // JSON.parse accepts extreme exponents as +/-Infinity. Preserve them as
  // valid JSON number tokens rather than JSON.stringify's lossy null encoding.
  if (x === Infinity) return '1e999';
  if (x === -Infinity) return '-1e999';
  if (Array.isArray(x)) return '[' + x.map(canonical).join(',') + ']';
  if (object(x)) return '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}';
  return JSON.stringify(x);
}
export const equal = (a, b) => canonical(a) === canonical(b);
export const blank = x => typeof x !== 'string' || !x.trim();
export async function directory(dir) {
  const missing = [];
  let current = path.resolve(dir);
  for (;;) {
    try { await fs.stat(current); break; }
    catch (e) {
      if (e.code !== 'ENOENT') throw e;
      missing.push(current);
      current = path.dirname(current);
    }
  }
  await fs.mkdir(dir, { recursive: true });
  // Sync parent entries too: syncing a newly created store alone does not
  // establish durability of the directory's name in its parent.
  for (const created of missing.reverse()) await syncDirectory(path.dirname(created));
  return fs.realpath(dir);
}
async function syncDirectory(dir) {
  const handle = await fs.open(dir, 'r');
  try { await handle.sync(); } finally { await handle.close(); }
}
export async function atomic(file, value) {
  const temp = file + '.' + randomUUID() + '.tmp';
  let handle;
  try {
    handle = await fs.open(temp, 'wx', 0o600);
    await handle.writeFile(canonical(value) + '\n');
    await handle.sync();
    await handle.close(); handle = null;
    await fs.rename(temp, file);
    await syncDirectory(path.dirname(file));
  } finally {
    if (handle) await handle.close();
    await fs.unlink(temp).catch(e => { if (e.code !== 'ENOENT') throw e; });
  }
}
function alive(pid) {
  try { process.kill(pid, 0); return true; }
  catch (e) { if (e.code === 'ESRCH') return false; if (e.code === 'EPERM') return true; throw e; }
}

// Dynamic Lamport bakery: publish choosing before reading tickets. Stable atomic
// participant files avoid partially written metadata. Never unlink another owner.
export async function locked(dir, action) {
  const locks = path.join(dir, '.locks');
  await fs.mkdir(locks, { recursive: true });
  const name = `${process.pid}-${randomUUID()}.json`;
  const file = path.join(locks, name);
  const participants = async () => {
    const result = [];
    for (const entry of await fs.readdir(locks)) {
      if (!entry.endsWith('.json')) continue; // interrupted atomic write temp files
      const match = /^(\d+)-[0-9a-f-]+\.json$/.exec(entry);
      if (!match) throw new Error('Malformed lock participant');
      let item;
      try { item = JSON.parse(await fs.readFile(path.join(locks, entry), 'utf8')); }
      catch (e) { if (e.code === 'ENOENT') continue; throw new Error('Malformed lock metadata'); }
      if (!object(item) || typeof item.choosing !== 'boolean' || !/^\d+$/.test(item.ticket)) throw new Error('Malformed lock metadata');
      if (alive(Number(match[1]))) result.push({ name: entry, ...item });
    }
    return result;
  };
  try {
    await atomic(file, { choosing: true, ticket: '0' });
    let ticket = 1n;
    for (const p of await participants()) ticket = ticket > BigInt(p.ticket) ? ticket : BigInt(p.ticket) + 1n;
    await atomic(file, { choosing: false, ticket: String(ticket) });
    for (;;) {
      const others = await participants();
      const blocked = others.some(p => p.name !== name && (p.choosing || (BigInt(p.ticket) > 0n && (BigInt(p.ticket) < ticket || (BigInt(p.ticket) === ticket && p.name < name)))));
      if (!blocked) break;
      await delay(5);
    }
    return await action();
  } finally {
    await fs.unlink(file).catch(e => { if (e.code !== 'ENOENT') throw e; });
  }
}
export async function load(dir, kind, validate) {
  let state;
  try { state = JSON.parse(await fs.readFile(path.join(dir, 'state.json'), 'utf8')); }
  catch (e) {
    if (e.code === 'ENOENT') return kind === 'local' ? { version: 1, kind, jobs: [] } : { version: 1, kind, accepted: [] };
    throw new Error('Cannot read valid store snapshot');
  }
  if (!object(state) || state.version !== 1 || state.kind !== kind || !validate(state)) throw new Error('Invalid store snapshot');
  return state;
}
export const save = (dir, state) => atomic(path.join(dir, 'state.json'), state);
