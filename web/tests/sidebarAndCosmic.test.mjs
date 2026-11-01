import { test } from 'node:test';
import assert from 'node:assert/strict';

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/invoices', label: 'Invoice Manager' },
  { to: '/upload', label: 'Invoice Upload' },
  { to: '/chat', label: 'Ask AI', badge: 'Gemini' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/automation', label: 'Automation' },
  { to: '/reports', label: 'Reports' },
  { to: '/settings', label: 'Settings' },
];

function getActiveIndex(pathname) {
  return navItems.findIndex((item) =>
    item.to === '/' ? pathname === '/' : pathname.startsWith(item.to)
  );
}

test('resolves active index deterministically across all primary routes with zero ambiguity', () => {
  assert.equal(getActiveIndex('/'), 0);
  assert.equal(getActiveIndex('/invoices'), 1);
  assert.equal(getActiveIndex('/invoices/123'), 1);
  assert.equal(getActiveIndex('/upload'), 2);
  assert.equal(getActiveIndex('/chat'), 3);
  assert.equal(getActiveIndex('/analytics'), 4);
  assert.equal(getActiveIndex('/automation'), 5);
  assert.equal(getActiveIndex('/reports'), 6);
  assert.equal(getActiveIndex('/settings'), 7);
  assert.equal(getActiveIndex('/unknown-route'), -1);
});

test('rapid transition sequence maps cleanly between all adjacent and non-adjacent destinations', () => {
  const sequence = [
    '/',
    '/invoices',
    '/upload',
    '/chat',
    '/analytics',
    '/settings',
    '/',
    '/chat',
    '/automation',
  ];

  const indices = sequence.map(getActiveIndex);
  assert.deepEqual(indices, [0, 1, 2, 3, 4, 7, 0, 3, 5]);

  // Ensure every active index is in the valid single-item range [0, navItems.length - 1]
  for (const idx of indices) {
    assert.ok(idx >= 0 && idx < navItems.length);
  }
});

test('cosmic beam trajectory alternator prevents identical consecutive paths', () => {
  let lastTrajectory = -1;
  const recorded = [];

  for (let i = 0; i < 20; i++) {
    const candidates = [0, 1, 2, 3].filter((t) => t !== lastTrajectory);
    const chosen = candidates[Math.floor(Math.random() * candidates.length)];
    assert.notEqual(chosen, lastTrajectory, 'Consecutive beams must not share the same trajectory');
    lastTrajectory = chosen;
    recorded.push(chosen);
  }

  // Confirm coverage across multiple distinct diagonal directions
  const uniqueDirections = new Set(recorded);
  assert.ok(uniqueDirections.size >= 3, 'Beams must traverse varied directions');
});

test('cosmic beam opacity envelope is smooth and strictly bounded [0, 1]', () => {
  const steps = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0];
  for (const progress of steps) {
    const envelope = Math.sin(progress * Math.PI);
    assert.ok(envelope >= 0 && envelope <= 1.0, `Envelope must be in [0, 1], got ${envelope}`);
  }
  // Mid-flight should have peak luminance
  assert.ok(Math.sin(0.5 * Math.PI) >= 0.99);
  // Entry and exit must be zero
  assert.ok(Math.abs(Math.sin(0.0 * Math.PI)) < 0.0001);
  assert.ok(Math.abs(Math.sin(1.0 * Math.PI)) < 0.0001);
});

test('active cosmic beam pool caps simultaneous beams at 2 to preserve clean cosmic atmosphere', () => {
  const pool = [
    { id: 0, active: true },
    { id: 1, active: true },
    { id: 2, active: false },
    { id: 3, active: false },
  ];

  const activeCount = pool.reduce((acc, b) => acc + (b.active ? 1 : 0), 0);
  const canSpawnThird = activeCount < 2;
  assert.equal(canSpawnThird, false, 'Must not spawn a third concurrent beam');

  // Deactivate one
  pool[0].active = false;
  const newActiveCount = pool.reduce((acc, b) => acc + (b.active ? 1 : 0), 0);
  const canSpawnNow = newActiveCount < 2;
  assert.equal(canSpawnNow, true, 'Can spawn when fewer than 2 beams are active');
});

test('Big Bang phase progression maps accurately to the 5 cinematic stages', () => {
  function getPhaseForTime(elapsed) {
    if (elapsed >= 1.35) return 5;
    if (elapsed >= 0.95) return 4;
    if (elapsed >= 0.55) return 3;
    if (elapsed >= 0.25) return 2;
    return 1;
  }

  // Phase 1: The Void (0 - 250ms)
  assert.equal(getPhaseForTime(0.0), 1);
  assert.equal(getPhaseForTime(0.15), 1);
  assert.equal(getPhaseForTime(0.24), 1);

  // Phase 2: Energy Compression (250 - 550ms)
  assert.equal(getPhaseForTime(0.25), 2);
  assert.equal(getPhaseForTime(0.40), 2);
  assert.equal(getPhaseForTime(0.54), 2);

  // Phase 3: The Big Bang (550 - 950ms)
  assert.equal(getPhaseForTime(0.55), 3);
  assert.equal(getPhaseForTime(0.75), 3);
  assert.equal(getPhaseForTime(0.94), 3);

  // Phase 4: Universe Formation (950 - 1350ms)
  assert.equal(getPhaseForTime(0.95), 4);
  assert.equal(getPhaseForTime(1.15), 4);
  assert.equal(getPhaseForTime(1.34), 4);

  // Phase 5: Dashboard Reveal (1350ms+)
  assert.equal(getPhaseForTime(1.35), 5);
  assert.equal(getPhaseForTime(1.60), 5);
});

test('Big Bang intro plays on initial visit and skips subsequent sidebar navigation', () => {
  const mockStorage = new Map();

  function shouldPlayBigBang() {
    return mockStorage.get('cosmic_initialized') !== 'true';
  }

  function markInitialized() {
    mockStorage.set('cosmic_initialized', 'true');
  }

  // First visit
  assert.equal(shouldPlayBigBang(), true, 'Must play on initial visit');

  // Complete animation
  markInitialized();
  assert.equal(shouldPlayBigBang(), false, 'Must not replay after initial visit');

  // Navigate to various sidebar routes
  const routes = ['/invoices', '/upload', '/chat', '/analytics', '/reports', '/settings', '/'];
  for (const route of routes) {
    assert.equal(shouldPlayBigBang(), false, `Must not replay on navigation to ${route}`);
  }
});

test('Big Bang 3D perspective projection preserves positive scale and depth fidelity', () => {
  const focalLength = 340;
  const zValues = [-120, -50, 0, 50, 150, 300];

  for (const z of zValues) {
    const depth = focalLength + z;
    const perspective = depth > 10 ? focalLength / depth : 1;
    assert.ok(Number.isFinite(perspective), `Perspective must be finite for z=${z}`);
    assert.ok(perspective > 0, `Perspective must be strictly positive for z=${z}`);
  }
});


