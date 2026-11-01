import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { useEffects } from './EffectsProvider';

export function ScrollReveal({ children, className = '', delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const { reduced } = useEffects();
  const revealed = useRef(false);
  useEffect(() => {
    const node = ref.current;
    if (!node || reduced || revealed.current || !('IntersectionObserver' in window)) return;
    let animation: Animation | undefined;
    const observer = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting) return;
      revealed.current = true;
      // Content stays visible if observation/animation APIs are unavailable.
      animation = node.animate?.([{ opacity: 0, transform: 'translateY(20px)' }, { opacity: 1, transform: 'translateY(0)' }], {
        duration: 480, delay: Math.min(delay, 180), easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'backwards',
      });
      observer.disconnect();
    }, { threshold: 0.08 });
    observer.observe(node);
    return () => { observer.disconnect(); animation?.cancel(); };
  }, [reduced, delay]);
  return <div ref={ref} className={className}>{children}</div>;
}
