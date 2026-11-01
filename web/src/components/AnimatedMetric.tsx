import { useEffect, useRef } from 'react';
import { useEffects } from './EffectsProvider';

export function AnimatedMetric({ value, format = String }: { value: number; format?: (value: number) => string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const played = useRef(false);
  const { reduced } = useEffects();
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    // Always synchronize the latest API value, including after a preference change.
    node.textContent = format(value);
    if (played.current || reduced || document.hidden || !Number.isFinite(value)) return;
    played.current = true;
    let frame = 0;
    const start = performance.now();
    const draw = (now: number) => {
      if (document.hidden) { node.textContent = format(value); return; }
      const progress = Math.min(1, (now - start) / 600);
      node.textContent = format(value * (1 - Math.pow(1 - progress, 3)));
      if (progress < 1) frame = requestAnimationFrame(draw);
    };
    frame = requestAnimationFrame(draw);
    return () => { cancelAnimationFrame(frame); };
  }, [value, format, reduced]);
  return <><span className="sr-only">{format(value)}</span><span ref={ref} aria-hidden="true">{format(value)}</span></>;
}
