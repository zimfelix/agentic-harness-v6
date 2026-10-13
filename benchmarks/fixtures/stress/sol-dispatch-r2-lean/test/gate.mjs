// Test-only instrumentation: pause immediately after a real atomic rename.
// The parent sends SIGKILL. No production test hook or alternative provider.
import fs from 'node:fs/promises';
import { syncBuiltinESMExports } from 'node:module';
import { basename } from 'node:path';
const rename = fs.rename;
fs.rename = async function (from, to) {
  await rename(from, to);
  const gate = process.env.OUTBOX_TEST_GATE;
  if (basename(to) !== 'state.json' && gate !== 'ticket') return;
  const s = JSON.parse(await fs.readFile(to, 'utf8'));
  if ((gate === 'ticket' && s.choosing === false) ||
      (gate === 'claim' && s.kind === 'queue' && s.jobs.some(j => j.claim)) ||
      (gate === 'accept' && s.kind === 'provider' && s.accepted.length) ||
      (gate === 'receipt' && s.kind === 'provider' && s.receipts.length)) {
    const keepAlive = setInterval(() => {}, 1000);
    process.send({ paused: gate });
    await new Promise(() => {});
    clearInterval(keepAlive);
  }
};
syncBuiltinESMExports();
