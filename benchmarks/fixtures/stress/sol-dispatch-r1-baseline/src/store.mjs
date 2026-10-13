import { DatabaseSync } from 'node:sqlite';
import { existsSync, mkdirSync, openSync, closeSync, fsyncSync, realpathSync, renameSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { resolve, dirname, join } from 'node:path';

function syncDirectory(path) {
  const fd = openSync(path, 'r');
  try { fsyncSync(fd); } finally { closeSync(fd); }
}

export function prepareDirectory(path) {
  const absolute = resolve(path);
  const missing = [];
  for (let p = absolute; !existsSync(p); p = dirname(p)) missing.push(p);
  for (const p of missing.reverse()) {
    try { mkdirSync(p); } catch (error) { if (error.code !== 'EEXIST') throw error; }
    syncDirectory(dirname(p));
  }
  return realpathSync(absolute);
}

export function separateDirectories(local, provider) {
  const a = prepareDirectory(local);
  const b = prepareDirectory(provider);
  if (a === b) throw new Error('Local and provider stores must be separate directories');
  return [a, b];
}

function database(path) {
  const db = new DatabaseSync(path);
  try {
    db.exec('PRAGMA busy_timeout=30000; PRAGMA synchronous=FULL;');
    return db;
  } catch (error) { db.close(); throw error; }
}

// OS SQLite locks, not removable lock files: death releases ownership automatically.
export function withStore(path, kind, validate, action) {
  const directory = prepareDirectory(path);
  const mutex = database(join(directory, 'mutex.sqlite'));
  let db;
  try {
    mutex.exec('BEGIN IMMEDIATE');
    const filename = join(directory, 'state.sqlite');
    if (!existsSync(filename)) {
      // Publish only a complete database. A kill during initialization may leave
      // an unused init file, but cannot publish an empty/partial state.sqlite.
      const temporary = join(directory, 'init-' + randomUUID() + '.sqlite');
      const initialDb = database(temporary);
      try {
        initialDb.exec('BEGIN IMMEDIATE; CREATE TABLE snapshot (id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);');
        const initial = { version: 1, kind, records: [] };
        initialDb.prepare('INSERT INTO snapshot VALUES (1, ?)').run(JSON.stringify(initial));
        initialDb.exec('COMMIT');
      } finally { initialDb.close(); }
      renameSync(temporary, filename);
      syncDirectory(directory);
    }
    db = database(filename);
    const rows = db.prepare('SELECT id, body FROM snapshot').all();
    if (rows.length !== 1 || rows[0].id !== 1) throw new Error('Malformed snapshot');
    const state = JSON.parse(rows[0].body);
    validate(state, kind);
    const save = () => {
      validate(state, kind);
      db.exec('BEGIN IMMEDIATE');
      try {
        db.prepare('UPDATE snapshot SET body=? WHERE id=1').run(JSON.stringify(state));
        db.exec('COMMIT');
        syncDirectory(directory);
      } catch (error) {
        try { db.exec('ROLLBACK'); } catch { /* COMMIT may already have completed. */ }
        throw error;
      }
    };
    return action(state, save);
  } finally {
    db?.close();
    // Closing rolls back the lock transaction; never unlinks anyone's files.
    mutex.close();
  }
}
