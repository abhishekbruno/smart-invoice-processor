import React from 'react';
import { useEffects } from './EffectsProvider';

const stars = Array.from({ length: 55 }, (_, i) => ({
  x: (i * 61.8034) % 100,
  y: (i * 37.213 + 7) % 100,
  r: i % 8 === 0 ? 1.2 : 0.65,
}));

/**
 * Pure GPU-accelerated static and drifting cosmic background.
 * Uses zero scroll event listeners or per-frame DOM style updates to ensure 60 FPS scrolling.
 */
export const CosmicBackground: React.FC = () => {
  const { mode } = useEffects();

  return (
    <div
      aria-hidden="true"
      className="cosmic-background fixed inset-0 z-0 overflow-hidden pointer-events-none select-none bg-[#020203]"
      style={{ contain: 'strict' }}
    >
      <div className="cosmic-nebula" />
      {[0, 1, 2].map((layer) => (
        <svg
          key={layer}
          className={`star-layer star-layer-${layer}`}
          width="100%"
          height="100%"
        >
          {stars
            .filter((_, i) => i % 3 === layer && (mode === 'full' || i < 32))
            .map((star, i) => (
              <circle
                key={i}
                cx={star.x + '%'}
                cy={star.y + '%'}
                r={star.r}
                fill={layer === 2 ? '#a6b9ff' : '#e4d9ff'}
                opacity={0.24 + (i % 4) * 0.1}
              />
            ))}
        </svg>
      ))}
      <div className="cosmic-vignette" />
    </div>
  );
};
