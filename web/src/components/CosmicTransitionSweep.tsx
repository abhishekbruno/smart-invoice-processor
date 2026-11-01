import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useEffects } from './EffectsProvider';

interface ParticleCoord {
  x: number;
  y: number;
  size: number;
  color: string;
}

// Pre-computed convergence particles around center
const WARP_PARTICLES: ParticleCoord[] = Array.from({ length: 10 }, (_, i) => {
  const angle = (i / 10) * Math.PI * 2 + (i % 2 === 0 ? 0.15 : -0.15);
  const distance = 45 + (i % 3) * 16;
  return {
    x: Math.round(Math.cos(angle) * distance),
    y: Math.round(Math.sin(angle) * distance),
    size: i % 3 === 0 ? 2.5 : 1.8,
    color: i % 2 === 0 ? '#E9D5FF' : '#C084FC',
  };
});

/**
 * CosmicTransitionSweep — Cosmic Warp Transition
 *
 * Lightweight, non-blocking navigation transition between sidebar pages:
 * - A small cluster of violet cosmic particles converges briefly near center.
 * - A delicate circular energy ripple expands outward.
 * - Soft atmospheric ambient illumination dissolves seamlessly.
 * - Finishes in ~300ms, non-blocking, preserves persistent cosmic background.
 */
export const CosmicTransitionSweep: React.FC = () => {
  const location = useLocation();
  const { reduced } = useEffects();
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (reduced) return;

    setActive(true);
    const timer = setTimeout(() => {
      setActive(false);
    }, 310);

    return () => clearTimeout(timer);
  }, [location.pathname, reduced]);

  if (!active || reduced) return null;

  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 lg:left-60 pointer-events-none z-30 overflow-hidden"
    >
      {/* Central Cosmic Warp Anchor */}
      <div className="absolute left-1/2 top-[38%] -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        {/* Soft atmospheric lavender glow pulse */}
        <div
          className="absolute w-72 h-72 rounded-full bg-[radial-gradient(circle,rgba(168,85,247,0.20)_0%,rgba(99,102,241,0.06)_45%,transparent_70%)] pointer-events-none"
          style={{
            animation: 'cosmic-warp-glow 0.31s cubic-bezier(0.16, 1, 0.3, 1) forwards',
          }}
        />

        {/* Thin expanding circular energy ripple */}
        <div
          className="absolute w-56 h-56 rounded-full border border-[#C084FC]/45 pointer-events-none shadow-[0_0_16px_rgba(192,132,252,0.3)]"
          style={{
            animation: 'cosmic-warp-ripple 0.31s cubic-bezier(0.16, 1, 0.3, 1) forwards',
          }}
        />

        {/* Converging cosmic particles cluster */}
        {WARP_PARTICLES.map((p, idx) => (
          <span
            key={idx}
            className="absolute rounded-full pointer-events-none"
            style={
              {
                '--tw-translate-x': `${p.x}px`,
                '--tw-translate-y': `${p.y}px`,
                width: `${p.size}px`,
                height: `${p.size}px`,
                backgroundColor: p.color,
                boxShadow: `0 0 6px ${p.color}`,
                animation: `cosmic-converge 0.28s cubic-bezier(0.16, 1, 0.3, 1) forwards`,
              } as React.CSSProperties
            }
          />
        ))}
      </div>
    </div>
  );
};
