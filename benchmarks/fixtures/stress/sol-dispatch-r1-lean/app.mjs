import { dispatch } from './outbox.mjs';
import { blank, object, canonical } from './storage.mjs';

const commands = {
  enqueue: ['store', 'tenant', 'key', 'payload'],
  status: ['store', 'tenant'],
  work: ['store', 'provider', 'tenant', 'now', 'mode', 'crash'],
  provider: ['provider', 'tenant'],
};
function parse(args) {
  const [command, ...rest] = args;
  if (!Object.hasOwn(commands, command)) throw new Error('Expected enqueue, status, work or provider');
  const options = {};
  for (let i = 0; i < rest.length; i += 2) {
    const flag = rest[i];
    const name = flag.startsWith('--') ? flag.slice(2) : '';
    if (!commands[command].includes(name) || Object.hasOwn(options, name) || i + 1 >= rest.length) throw new Error('Invalid or duplicate option');
    options[name] = rest[i + 1];
  }
  for (const name of commands[command].filter(n => n !== 'mode' && n !== 'crash')) {
    if (blank(options[name])) throw new Error(`${name} is required and must be nonblank`);
  }
  if (command === 'enqueue') {
    try { options.payload = JSON.parse(options.payload); } catch { throw new Error('payload must be valid JSON'); }
    if (!object(options.payload)) throw new Error('payload must be a JSON object');
  }
  if (command === 'work') {
    if (!/^-?\d+$/.test(options.now)) throw new Error('now must be an integer');
    options.now = String(BigInt(options.now));
    options.mode ??= 'ok';
    if (!['ok', 'accepted-timeout', 'reject', 'transient'].includes(options.mode)) throw new Error('Invalid mode');
    if (options.crash && !['before-send', 'after-accept'].includes(options.crash)) throw new Error('Invalid crash');
    // after-accept necessarily invokes the accepting behavior, whatever mode
    // was supplied; the simulated crash, not a response, is the outcome.
    if (options.crash === 'after-accept') options.mode = 'ok';
  }
  return { command, options };
}
try {
  const { command, options } = parse(process.argv.slice(2));
  console.log(canonical(await dispatch(command, options)));
} catch (error) {
  console.log(JSON.stringify({ error: error.message }));
  process.exitCode = 1;
}
