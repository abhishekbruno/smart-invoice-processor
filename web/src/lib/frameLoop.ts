export function createFrameLoop(
  draw: (deltaSeconds: number) => void,
  scheduler: { request: (callback: FrameRequestCallback) => number; cancel: (id: number) => void },
) {
  let pending: number | null = null;
  let previous: number | null = null;
  let running = false;
  let disposed = false;
  const frame: FrameRequestCallback = now => {
    pending = null;
    if (!running || disposed) return;
    const dt = previous === null ? 0 : Math.min(0.05, Math.max(0, (now - previous) / 1000));
    previous = now;
    draw(dt);
    if (running && !disposed) pending = scheduler.request(frame);
  };
  const stop = () => {
    running = false;
    if (pending !== null) scheduler.cancel(pending);
    pending = null;
    previous = null;
  };
  return {
    start() {
      if (running || disposed) return;
      running = true;
      pending = scheduler.request(frame);
    },
    stop,
    dispose() { stop(); disposed = true; },
  };
}
