import { enqueue, status, work, providerTruth } from './src/dispatch.mjs';
import { objectPayload } from './src/storage.mjs';

function parse(args) {
  const [command, ...flags] = args;
  const required = {
    enqueue: ['store', 'tenant', 'key', 'payload'],
    status: ['store', 'tenant'],
    work: ['store', 'provider', 'tenant', 'now'],
    provider: ['provider', 'tenant'],
  };
  if (!Object.hasOwn(required, command ?? '')) throw new Error('Expected command: enqueue, status, work, provider');
  const allowed = [...required[command], ...(command === 'work' ? ['mode', 'crash'] : [])];
  const options = Object.create(null);
  for (let i = 0; i < flags.length; i += 2) {
    const flag = flags[i]; const name = flag.startsWith('--') ? flag.slice(2) : '';
    if (!allowed.includes(name) || Object.hasOwn(options, name) || flags[i + 1] === undefined) throw new Error(`Invalid or duplicate option: ${flag}`);
    options[name] = flags[i + 1];
  }
  for (const name of required[command]) if (!Object.hasOwn(options, name)) throw new Error(`Missing --${name}`);
  for (const name of ['tenant', 'key', 'store', 'provider']) {
    if (options[name] !== undefined && !options[name].trim()) throw new Error(`--${name} must be nonblank`);
  }
  if (command === 'enqueue') options.payload = objectPayload(options.payload);
  if (command === 'work') {
    if (!/^[+-]?\d+$/.test(options.now)) throw new Error('--now must be an integer');
    options.now = BigInt(options.now);
    if (options.mode && !['ok', 'accepted-timeout', 'reject', 'transient'].includes(options.mode)) throw new Error('Invalid --mode');
    if (options.crash && !['before-send', 'after-accept'].includes(options.crash)) throw new Error('Invalid --crash');
  }
  return { command, options };
}

try {
  const { command, options } = parse(process.argv.slice(2));
  const commands = { enqueue, status, work, provider: providerTruth };
  console.log(JSON.stringify(commands[command](options)));
} catch (error) {
  console.log(JSON.stringify({ error: error.message }));
  process.exitCode = 1;
}
