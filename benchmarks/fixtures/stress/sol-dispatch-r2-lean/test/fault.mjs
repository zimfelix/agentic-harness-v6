// Test-only I/O fault injection at real persistence boundaries.
import fs from 'node:fs/promises';
import { syncBuiltinESMExports } from 'node:module';
import { basename } from 'node:path';
const rename = fs.rename;
fs.rename = async function (from, to) {
  if (basename(to) === 'state.json') {
    const s = JSON.parse(await fs.readFile(from, 'utf8'));
    const fault = process.env.OUTBOX_TEST_FAULT;
    if ((fault === 'enqueue' && s.kind === 'queue' && s.jobs.some(j => j.provider === null)) ||
        (fault === 'provider' && s.kind === 'provider') ||
        (fault === 'success' && s.kind === 'queue' && s.jobs.some(j => j.status === 'delivered'))) {
      throw Object.assign(new Error('Injected persistence failure'), { code: 'EIO' });
    }
  }
  return rename(from, to);
};
syncBuiltinESMExports();
