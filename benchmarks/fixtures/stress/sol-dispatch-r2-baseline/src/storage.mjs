import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, existsSync, linkSync, unlinkSync, openSync, closeSync, fsyncSync, realpathSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

const schemas = {
  local: `CREATE TABLE jobs (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE, tenant TEXT NOT NULL, key TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending','uncertain','delivered','dead')),
    attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 3),
    retry_at TEXT,
    provider_id TEXT,
    UNIQUE(tenant,key)
  ) STRICT;`,
  provider: `CREATE TABLE accepted (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE, tenant TEXT NOT NULL, key TEXT NOT NULL,
    payload TEXT NOT NULL, UNIQUE(tenant,key)
  ) STRICT;`,
  ownership: '',
};
const filenames = { local: 'state.sqlite', provider: 'provider.sqlite', ownership: 'ownership.sqlite' };

// Preserve JSON numeric values rather than rounding them through IEEE-754.
function numberText(source) {
  const match = /^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(source);
  let digits = (match[2] + (match[3] ?? '')).replace(/^0+/, '');
  if (!digits) return '0';
  let exponent = BigInt(match[4] ?? '0') - BigInt((match[3] ?? '').length);
  const trailing = /0+$/.exec(digits)?.[0].length ?? 0;
  if (trailing) { digits = digits.slice(0, -trailing); exponent += BigInt(trailing); }
  return `${match[1]}${digits}${exponent === 0n ? '' : `e${exponent}`}`;
}

export function parsePayload(text) {
  return JSON.parse(text, (key, value, context) => typeof value === 'number'
    ? JSON.rawJSON(numberText(context.source)) : value);
}

export function canonical(value) {
  if (value === null) return 'null';
  if (JSON.isRawJSON(value)) return value.rawJSON;
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (typeof value === 'object') {
    return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  }
  if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('Payload numbers must be finite');
  return JSON.stringify(value);
}

export function objectPayload(text) {
  const value = parsePayload(text);
  if (!value || typeof value !== 'object' || Array.isArray(value) || JSON.isRawJSON(value)) throw new Error('Payload must be a JSON object');
  return canonical(value);
}

function syncFile(path) {
  const fd = openSync(path, 'r');
  try { fsyncSync(fd); } finally { closeSync(fd); }
}

export function directory(path) {
  mkdirSync(resolve(path), { recursive: true, mode: 0o700 });
  return realpathSync(resolve(path));
}

function connect(path) {
  const db = new DatabaseSync(path);
  db.exec('PRAGMA busy_timeout=30000; PRAGMA synchronous=FULL; PRAGMA temp_store=MEMORY;');
  return db;
}

// Publish a complete initialized database without overwriting a racing initializer.
function initialize(path, kind) {
  if (existsSync(path)) return;
  const temp = `${path}.init-${randomUUID()}`;
  let db;
  try {
    db = connect(temp);
    db.exec(`PRAGMA journal_mode=DELETE; BEGIN IMMEDIATE;
      CREATE TABLE format (kind TEXT NOT NULL) STRICT;
      ${schemas[kind]}
      PRAGMA user_version=1;`);
    db.prepare('INSERT INTO format VALUES (?)').run(kind);
    db.exec('COMMIT');
    db.close(); db = undefined;
    syncFile(temp);
    try { linkSync(temp, path); } catch (error) { if (error.code !== 'EEXIST') throw error; }
    syncFile(join(path, '..'));
  } finally {
    if (db) db.close();
    if (existsSync(temp)) unlinkSync(temp);
  }
}

function validate(db, kind) {
  if (db.prepare('PRAGMA user_version').get().user_version !== 1) throw new Error('Unsupported or malformed persistence version');
  const format = db.prepare('SELECT kind FROM format').all();
  if (format.length !== 1 || format[0].kind !== kind) throw new Error('Wrong persistence store kind');
  if (db.prepare('PRAGMA quick_check').get().quick_check !== 'ok') throw new Error('Corrupt persistence');
  const tables = db.prepare("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all();
  const expected = kind === 'local' ? ['format', 'jobs'] : kind === 'provider' ? ['accepted', 'format'] : ['format'];
  if (JSON.stringify(tables.map(t => t.name)) !== JSON.stringify(expected)) throw new Error('Malformed persistence schema');
  const normalize = sql => sql.trim().replace(/;$/, '').replace(/\s+/g, ' ');
  for (const table of tables) {
    const sql = table.name === 'format' ? 'CREATE TABLE format (kind TEXT NOT NULL) STRICT' : schemas[kind];
    if (normalize(table.sql) !== normalize(sql)) throw new Error('Malformed persistence table definition');
  }
  if (kind === 'ownership') return;
  const rows = db.prepare(`SELECT * FROM ${kind === 'local' ? 'jobs' : 'accepted'}`).all();
  const identities = new Set(); const ids = new Set();
  for (const row of rows) {
    if (!Number.isSafeInteger(row.seq) || row.seq < 1 || typeof row.id !== 'string' || !row.id.trim() ||
        typeof row.tenant !== 'string' || !row.tenant.trim() || typeof row.key !== 'string' || !row.key.trim() ||
        typeof row.payload !== 'string' || objectPayload(row.payload) !== row.payload) throw new Error('Malformed persisted record');
    const identity = JSON.stringify([row.tenant, row.key]);
    if (identities.has(identity) || ids.has(row.id)) throw new Error('Duplicate persisted identity');
    identities.add(identity); ids.add(row.id);
    if (kind === 'local' && (!['pending', 'uncertain', 'delivered', 'dead'].includes(row.status) ||
        !Number.isInteger(row.attempts) || row.attempts < 0 || row.attempts > 3 ||
        (row.retry_at !== null && (typeof row.retry_at !== 'string' || !/^-?\d+$/.test(row.retry_at) || BigInt(row.retry_at).toString() !== row.retry_at)) ||
        (row.status === 'delivered' ? typeof row.provider_id !== 'string' || !row.provider_id.trim() : row.provider_id !== null))) {
      throw new Error('Malformed persisted job state');
    }
  }
}

export function openStore(dir, kind) {
  const path = join(directory(dir), filenames[kind]);
  initialize(path, kind);
  if (!statSync(path).isFile() || statSync(path).size === 0) throw new Error('Malformed existing persistence');
  const db = connect(path);
  try {
    // Require rollback journals for atomic commits across ATTACHed databases.
    if (db.prepare('PRAGMA journal_mode').get().journal_mode !== 'delete') throw new Error('Unsupported journal mode');
    validate(db, kind);
    return db;
  } catch (error) { db.close(); throw error; }
}

export function transaction(db, fn) {
  db.exec('BEGIN IMMEDIATE');
  try {
    const result = fn();
    db.exec('COMMIT');
    return result;
  } catch (error) {
    try { db.exec('ROLLBACK'); } catch { /* COMMIT may already have ended the transaction. */ }
    throw error;
  }
}

export function withLocal(dir, fn) {
  const ownership = openStore(dir, 'ownership');
  try {
    return transaction(ownership, () => {
      const local = openStore(dir, 'local');
      try { return fn(local); } finally { local.close(); }
    });
  } finally { ownership.close(); }
}

export function attachProvider(local, localDir, providerDir) {
  const own = directory(localDir); const remote = directory(providerDir);
  if (own === remote) throw new Error('Local and provider stores must be separate directories');
  const provider = openStore(remote, 'provider');
  provider.close();
  local.prepare('ATTACH DATABASE ? AS remote').run(join(remote, filenames.provider));
  local.exec('PRAGMA remote.synchronous=FULL;');
}
