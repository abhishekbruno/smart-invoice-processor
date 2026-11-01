# Cosmic Energy UI 2.0

Implement the supplied brief directly in the existing React and Flutter clients. Keep API contracts, extraction, currency conversion, OAuth and invoice decisions unchanged. No deployment or Git operations.

## Design

Use the reference palette: near-black space, violet nebula haze, electric blue highlights and restrained lavender filaments. Retain the existing procedural Canvas core (no Three.js dependency exists). Center it above the hero heading so its luminous center cannot obscure text. Replace the marketing-style dashboard and invented impact figures with real financial summaries, a spending area chart, vendor breakdown and recent invoices.

## Implementation sequence

1. Shared effects preference and a tested animation scheduler: dynamic reduced motion, hidden-tab/offscreen suspension, elapsed-time animation, cancellation and cleanup. Tests must catch orphaned animation requests and time jumps after resume.
2. Upgrade CelestialEnergyCanvas: responsive projected 3D surface, layered organic ribbons, traveling arcs, emission particles and expanding waves. Use one lazy-loaded core on Dashboard only. Persistent CSS/SVG starfield elsewhere with three depth layers.
3. Shared ScrollReveal and AnimatedPage: 480 ms one-time reveals; 100 ms exit and 200 ms entry, reduced-motion bypass, rapid navigation cancellation. Keep background and query cache mounted. Refine shared glass material.
4. DashboardHero and dashboard: API-backed metrics, currency-aware chart/tooltips, real activity/status links, explicit loading/error/empty states. Remove fabricated impact metrics. Add local Reduced Effects setting.
5. Flutter: native starfield/gradients, improved existing CustomPainter core, lifecycle and accessibility pause, Reduced Effects setting, short page transitions, no default backdrop blurs. Preserve providers and connectivity.
6. Verify TypeScript, production build and meaningful animation tests. Inspect currency/status bindings and cleanup. Attempt visual browser QA only with authorized browser access. Document any unavailable checks, including Flutter SDK and device/GPU profiling.

## Review focus

- Missing API data must never become a fabricated zero or rate.
- Reduced-motion preference changes must stop effects immediately.
- Hidden/offscreen animation must leave no recurring request scheduled.
- Fast repeated navigation must settle on the latest route.
- Small viewport core must fit its transparent canvas; tables remain readable.

## Constraints discovered

- Workspace has no Git metadata; edit in place as requested.
- Browser permission gate declined access to localhost:5173; no alternate browser access attempted.
- Flutter and Dart executables were not on PATH; the installed SDK was found at C:/src/flutter and used for validation.

## Progress

- Inspected existing Canvas renderer, persistent Layout, dashboard API types and Flutter widgets.
- Implementation and code review complete. React build/tests and Flutter analysis/widget tests pass. See cosmic-energy-ui-verification.md for evidence and the browser permission limitation.
