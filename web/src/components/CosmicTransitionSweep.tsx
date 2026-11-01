import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useEffects } from './EffectsProvider';

/**
 * Cosmic Transition Sweep
 * Renders a subtle, non-blocking violet atmospheric energy streak
 * that glides across the main content area during sidebar navigation.
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
    }, 280);

    return () => clearTimeout(timer);
  }, [location.pathname, reduced]);

  if (!active || reduced) return null;

  return (
    <div
      aria-hidden="true"
      className="fixed inset-y-0 right-0 left-0 lg:left-60 pointer-events-none z-30 overflow-hidden"
    >
      {/* Light traveling atmospheric streak */}
      <div
        className="absolute inset-y-0 w-32 bg-gradient-to-r from-transparent via-[#C084FC]/20 to-transparent blur-md"
        style={{
          animation: 'cosmic-sweep 0.28s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
        }}
      />

      {/* Leading subtle electric edge */}
      <div
        className="absolute inset-y-0 w-0.5 bg-gradient-to-b from-transparent via-[#E9D5FF]/60 to-transparent"
        style={{
          animation: 'cosmic-sweep-edge 0.28s cubic-bezier(0.2, 0.8, 0.2, 1) forwards',
        }}
      />
    </div>
  );
};

