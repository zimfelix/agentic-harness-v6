import { work } from '../src/dispatch.mjs';
const [local, remote, point] = process.argv.slice(2);
work(local, remote, 'A', 7, 'ok', undefined, stage => {
  if (stage === point) {
    process.send({ stage });
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0);
  }
});
