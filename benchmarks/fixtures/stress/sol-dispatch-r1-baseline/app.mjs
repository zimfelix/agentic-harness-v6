import { parseArgs } from 'node:util';
import { enqueue, status, provider, work } from './src/dispatch.mjs';

try {
  const [command, ...args] = process.argv.slice(2);
  const commands = {
    enqueue: ['store', 'tenant', 'key', 'payload'],
    status: ['store', 'tenant'],
    provider: ['provider', 'tenant'],
    work: ['store', 'provider', 'tenant', 'now', 'mode', 'crash'],
  };
  if (!Object.hasOwn(commands, command)) throw new Error('Expected enqueue, status, work or provider');
  const allowed = commands[command];
  const { values, tokens } = parseArgs({ args, options: Object.fromEntries(allowed.map(k => [k, { type: 'string' }])), tokens: true, allowPositionals: false });
  const seen = new Set();
  for (const token of tokens) {
    if (seen.has(token.name)) throw new Error('Duplicate option: ' + token.name);
    seen.add(token.name);
  }
  for (const name of allowed.filter(k => !['mode', 'crash'].includes(k))) {
    if (values[name] === undefined || !values[name].trim()) throw new Error('Missing nonblank --' + name);
  }
  let result;
  switch (command) {
    case 'enqueue': result = enqueue(values.store, values.tenant, values.key, JSON.parse(values.payload)); break;
    case 'status': result = status(values.store, values.tenant); break;
    case 'provider': result = provider(values.provider, values.tenant); break;
    case 'work': {
      if (!/^-?\d+$/.test(values.now)) throw new Error('now must be an integer');
      result = work(values.store, values.provider, values.tenant, Number(values.now), values.mode, values.crash);
      break;
    }
  }
  process.stdout.write(JSON.stringify(result) + '\n');
} catch (error) {
  process.stdout.write(JSON.stringify({ error: error.message }) + '\n');
  process.exitCode = 1;
}
