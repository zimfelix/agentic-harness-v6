import { writeSync } from 'node:fs';
export function crashAt(point) {
  writeSync(1, `${JSON.stringify({ error: `Simulated crash ${point}` })}\n`);
  process.kill(process.pid, 'SIGKILL');
}
