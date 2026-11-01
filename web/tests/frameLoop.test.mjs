import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createFrameLoop } from '../src/lib/frameLoop.ts';

function setup() {
  let id = 0;
  const queued = new Map();
  const steps = [];
  const loop = createFrameLoop(dt => steps.push(dt), {
    request: cb => { queued.set(++id, cb); return id; },
    cancel: key => queued.delete(key),
  });
  const tick = time => { const callbacks = [...queued.values()]; queued.clear(); callbacks.forEach(cb => cb(time)); };
  return { loop, queued, steps, tick };
}

test('pause and dispose remove pending work; repeated starts never fork the loop', () => {
  const { loop, queued, tick, steps } = setup();
  loop.start(); loop.start();
  assert.equal(queued.size, 1);
  tick(100); tick(120);
  assert.deepEqual(steps, [0, 0.02]);
  loop.stop();
  assert.equal(queued.size, 0);
  tick(140);
  assert.equal(steps.length, 2);
  loop.start(); loop.dispose(); loop.start();
  assert.equal(queued.size, 0);
});

test('resume resets elapsed time and long frames are bounded', () => {
  const { loop, tick, steps } = setup();
  loop.start(); tick(10); tick(30); loop.stop();
  loop.start(); tick(90000); tick(90020); tick(91000);
  assert.deepEqual(steps, [0, 0.02, 0, 0.02, 0.05]);
});

test('stopping inside a draw does not schedule an orphan frame', () => {
  const queued = new Map(); let id = 0;
  const loop = createFrameLoop(() => loop.stop(), {
    request: cb => { queued.set(++id, cb); return id; },
    cancel: key => queued.delete(key),
  });
  loop.start(); const callback = [...queued.values()][0]; queued.clear(); callback(10);
  assert.equal(queued.size, 0);
});
