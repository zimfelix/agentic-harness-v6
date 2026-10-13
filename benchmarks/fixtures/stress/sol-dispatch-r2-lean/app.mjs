import { resolve } from 'node:path';
import { directory } from './lib/storage.mjs';
import { nonblank, object, canonical, modes, requireThat } from './lib/model.mjs';
import { enqueue, status, work } from './lib/queue.mjs';
import { inspect } from './lib/provider.mjs';

function parse(args) {
  const command = args.shift();
  const allowed = {
    enqueue: ['store', 'tenant', 'key', 'payload'],
    status: ['store', 'tenant'],
    work: ['store', 'provider', 'tenant', 'now', 'mode', 'crash'],
    provider: ['provider', 'tenant'],
  };
  requireThat(Object.hasOwn(allowed, command), 'Expected enqueue, status, work or provider command');
  const opts = Object.create(null);
  while (args.length) {
    const flag = args.shift();
    requireThat(flag.startsWith('--') && allowed[command].includes(flag.slice(2)), `Unknown option: ${flag}`);
    const name = flag.slice(2);
    requireThat(!Object.hasOwn(opts, name) && args.length > 0, `Duplicate or missing option: ${flag}`);
    opts[name] = args.shift();
  }
  for (const name of allowed[command].filter(k => !['mode', 'crash'].includes(k))) {
    requireThat(Object.hasOwn(opts, name), `Missing --${name}`);
  }
  for (const name of ['tenant', 'key', 'store', 'provider'].filter(k => Object.hasOwn(opts, k))) {
    requireThat(nonblank(opts[name]), `--${name} must be nonblank`);
  }
  if (command === 'enqueue') {
    try { opts.payload = JSON.parse(opts.payload); }
    catch { throw new Error('--payload must parse as a JSON object'); }
    requireThat(object(opts.payload), '--payload must parse as a JSON object');
    canonical(opts.payload);
  }
  if (command === 'work') {
    requireThat(/^[+-]?[0-9]+$/.test(opts.now), '--now must be an integer');
    opts.now = String(BigInt(opts.now));
    opts.mode ??= 'ok';
    requireThat(modes.includes(opts.mode), 'Invalid --mode');
    requireThat(opts.crash === undefined || ['before-send', 'after-accept'].includes(opts.crash), 'Invalid --crash');
    requireThat(opts.crash !== 'after-accept' || ['ok', 'accepted-timeout'].includes(opts.mode),
      '--crash after-accept requires an accepting mode');
    requireThat(resolve(opts.store) !== resolve(opts.provider), 'Queue and provider must be separate directories');
  }
  return { command, opts };
}

async function main() {
  const { command, opts: o } = parse(process.argv.slice(2));
  const store = o.store && await directory(o.store);
  const provider = o.provider && await directory(o.provider);
  if (command === 'work') requireThat(store !== provider, 'Queue and provider must be separate directories');
  if (command === 'enqueue') return enqueue(store, o.tenant, o.key, o.payload);
  if (command === 'status') return status(store, o.tenant);
  if (command === 'provider') return inspect(provider, o.tenant);
  return work(store, provider, o.tenant, o.now, o.mode, o.crash);
}
try {
  console.log(JSON.stringify(await main()));
} catch (error) {
  console.log(JSON.stringify({ error: error.message }));
  process.exitCode = 1;
}
