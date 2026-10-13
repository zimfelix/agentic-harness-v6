import { mkdir, readFile, readdir, rename, unlink, open, realpath } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { randomUUID } from 'node:crypto';
import { setTimeout as pause } from 'node:timers/promises';

async function syncDirectory(path) {
  const handle = await open(path, 'r');
  try { await handle.sync(); } finally { await handle.close(); }
}

export async function directory(path) {
  const firstCreated = await mkdir(path, { recursive: true });
  const canonical = await realpath(path);
  if (firstCreated) {
    // Persist newly created directory entries too, not only state.json.
    const stop = dirname(await realpath(firstCreated));
    let parent = dirname(canonical);
    for (;;) {
      await syncDirectory(parent);
      if (parent === stop) break;
      const next = dirname(parent);
      if (next === parent) throw new Error('Cannot resolve created directory ancestry');
      parent = next;
    }
  }
  return canonical;
}

export async function atomicJSON(path, value) {
  const tmp = `${path}.${process.pid}.${randomUUID()}.tmp`;
  let handle;
  try {
    handle = await open(tmp, 'wx', 0o600);
    await handle.writeFile(JSON.stringify(value));
    await handle.sync();
    await handle.close();
    handle = undefined;
    await rename(tmp, path);
    await syncDirectory(dirname(path));
  } finally {
    if (handle) await handle.close();
    await unlink(tmp).catch(e => { if (e.code !== 'ENOENT') throw e; });
  }
}

async function optionalJSON(path) {
  let text;
  try { text = await readFile(path, 'utf8'); }
  catch (e) { if (e.code === 'ENOENT') return null; throw e; }
  try { return JSON.parse(text); }
  catch { throw new Error(`Malformed persistence: ${path}`); }
}

export async function load(dir, kind, empty, validate) {
  const value = await optionalJSON(join(dir, 'state.json'));
  if (value === null) {
    // JSON null is not an empty store: distinguish it from a missing file.
    try { await readFile(join(dir, 'state.json')); }
    catch (e) { if (e.code === 'ENOENT') return empty(); throw e; }
    throw new Error(`Malformed ${kind} persistence`);
  }
  try { validate(value); }
  catch { throw new Error(`Malformed ${kind} persistence: ${join(dir, 'state.json')}`); }
  return value;
}
export const save = (dir, state) => atomicJSON(join(dir, 'state.json'), state);

function alive(pid) {
  try { process.kill(pid, 0); return true; }
  catch (e) { if (e.code === 'ESRCH') return false; if (e.code === 'EPERM') return true; throw e; }
}

// Lamport bakery: publish choosing, select max+1, then wait for all earlier
// (ticket,token) pairs. Records are atomically replaced, never half-written.
// A dead participant is ignored, not unlinked: no stale owner can remove a
// successor's lock. Each invocation has its own unique register.
export async function locked(dir, action) {
  const locks = join(dir, '.owners');
  await mkdir(locks, { recursive: true });
  const token = `${process.pid}-${randomUUID()}`;
  const path = join(locks, `${token}.json`);
  async function participants() {
    const records = [];
    for (const name of await readdir(locks)) {
      if (!name.endsWith('.json')) continue;
      const record = await optionalJSON(join(locks, name));
      if (record === null) {
        // A concurrent owner may have removed its record on exit.
        try { await readFile(join(locks, name)); }
        catch (e) { if (e.code === 'ENOENT') continue; throw e; }
        throw new Error('Malformed ownership record');
      }
      if (!Number.isSafeInteger(record.pid) || record.pid <= 0 ||
          typeof record.token !== 'string' || name !== `${record.token}.json` ||
          !record.token.startsWith(`${record.pid}-`) ||
          typeof record.choosing !== 'boolean' ||
          !/^[0-9]+$/.test(record.ticket) || typeof record.ticket !== 'string' ||
          (!record.choosing && BigInt(record.ticket) < 1n)) {
        throw new Error('Malformed ownership record');
      }
      if (alive(record.pid)) records.push(record);
    }
    return records;
  }
  try {
    await atomicJSON(path, { pid: process.pid, token, choosing: true, ticket: '0' });
    const records = await participants();
    const ticket = records.reduce((max, r) => BigInt(r.ticket) > max ? BigInt(r.ticket) : max, 0n) + 1n;
    await atomicJSON(path, { pid: process.pid, token, choosing: false, ticket: String(ticket) });
    for (;;) {
      const others = await participants();
      if (!others.some(r => r.token !== token && (r.choosing ||
          BigInt(r.ticket) < ticket || (BigInt(r.ticket) === ticket && r.token < token)))) break;
      await pause(5); // Ownership contention only, never logical retry timing.
    }
    return await action();
  } finally {
    await unlink(path).catch(e => { if (e.code !== 'ENOENT') throw e; });
  }
}
