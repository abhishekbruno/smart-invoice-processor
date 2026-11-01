import React, { useEffect, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchSystemStatus } from '../services/api';
import { useEffects } from './EffectsProvider';
import { BigBangCanvas } from './BigBangCanvas';
import { ArrowRight, RefreshCw } from 'lucide-react';

interface Props {
  onComplete?: () => void;
}

/**
 * AppLoadingScreen — Big Bang Cosmic Entrance
 *
 * Cinematic 5-Phase Sequence:
 * Phase 1: The Void (0–250ms) — Absolute black void, distant stars, tiny singularity spark.
 * Phase 2: Energy Compression (250–550ms) — Particles sucked inward, contracting energy rings, tension build.
 * Phase 3: The Big Bang (550–950ms) — Luminous burst, radial 3D expanding particles, expanding lavender shockwaves and dust.
 * Phase 4: Universe Formation (950–1350ms) — Particles settle into deep space, smooth violet sphere emerges at focal center.
 * Phase 5: Dashboard Reveal (1350ms+) — Overlay fades out smoothly, revealing sidebar, dashboard, and glass panels.
 *
 * Performance-optimized: Single coordinate canvas loop, zero memory leaks, disposes upon finish.
 * Reserved strictly for initial website entry; never replays on sidebar page navigation.
 */
export const AppLoadingScreen: React.FC<Props> = ({ onComplete }) => {
  const { reduced } = useEffects();
  const [phase, setPhase] = useState<1 | 2 | 3 | 4 | 5>(1);
  const [fadingOut, setFadingOut] = useState(false);
  const [hidden, setHidden] = useState(() => {
    return sessionStorage.getItem('cosmic_initialized') === 'true';
  });

  // Real backend health check for initialization
  const { data: status, isError, refetch, isFetching } = useQuery({
    queryKey: ['system-status-init'],
    queryFn: fetchSystemStatus,
    retry: 2,
    staleTime: 60000,
  });

  const isReady = !!status && !isFetching;

  // Reduced motion bypass
  useEffect(() => {
    if (reduced || hidden) {
      setHidden(true);
      sessionStorage.setItem('cosmic_initialized', 'true');
      onComplete?.();
    }
  }, [reduced, hidden, onComplete]);

  const handlePhaseChange = useCallback((newPhase: 1 | 2 | 3 | 4 | 5) => {
    setPhase(newPhase);
  }, []);

  // When animation reaches Phase 5 and backend is ready (or error shown), initiate smooth transition
  const handleSequenceComplete = useCallback(() => {
    if (hidden || reduced) return;

    if (isReady || isError) {
      if (!isError) {
        setFadingOut(true);
        sessionStorage.setItem('cosmic_initialized', 'true');
        setTimeout(() => {
          setHidden(true);
          onComplete?.();
        }, 450);
      }
    } else {
      // If backend is taking longer, hold at Phase 4 (Sphere pulse) until ready
      const checkInterval = setInterval(() => {
        if (status || isError) {
          clearInterval(checkInterval);
          if (!isError) {
            setFadingOut(true);
            sessionStorage.setItem('cosmic_initialized', 'true');
            setTimeout(() => {
              setHidden(true);
              onComplete?.();
            }, 450);
          }
        }
      }, 150);
    }
  }, [hidden, reduced, isReady, isError, status, onComplete]);

  if (hidden || reduced) return null;

  const showSphere = phase >= 4;
  const showText = phase >= 4;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Application initialization"
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#020203] select-none transition-all duration-500 ease-out ${
        fadingOut ? 'opacity-0 scale-102 pointer-events-none' : 'opacity-100 scale-100'
      }`}
    >
      {/* Big Bang Particle Physics Canvas (Phases 1-4) */}
      <BigBangCanvas
        onPhaseChange={handlePhaseChange}
        onComplete={handleSequenceComplete}
      />

      {/* Atmospheric ambient radial wash emerging in Phase 4 */}
      <div
        className={`absolute inset-0 pointer-events-none transition-opacity duration-700 ${
          showSphere ? 'opacity-100' : 'opacity-0'
        }`}
        style={{
          background:
            'radial-gradient(ellipse 60% 50% at 50% 50%, rgba(107, 66, 205, 0.22), transparent 75%)',
        }}
      />

      {/* Phase 4: Centerpiece Smooth Violet Cosmic Sphere (Emerges from detonation) */}
      <div
        className={`relative z-20 flex items-center justify-center w-56 h-56 sm:w-64 sm:h-64 transition-all duration-700 ease-out ${
          showSphere ? 'scale-100 opacity-100' : 'scale-20 opacity-0 pointer-events-none'
        }`}
      >
        {/* Expanding Cosmic Energy Halo */}
        <div
          className={`absolute inset-0 rounded-full border border-[#BBA8F1]/45 pointer-events-none transition-all duration-800 ease-out ${
            showSphere ? 'scale-140 opacity-0' : 'scale-50 opacity-100'
          }`}
          style={{
            boxShadow: '0 0 35px rgba(187, 168, 241, 0.4)',
          }}
        />

        {/* Ambient lavender glow */}
        <div className="absolute inset-2 rounded-full bg-gradient-to-tr from-[#6D28D9]/35 via-[#A855F7]/30 to-[#3B82F6]/25 blur-xl opacity-90" />

        {/* Outer tilted orbital energy ring 1 */}
        <div
          className="absolute inset-0 rounded-full border border-[#C084FC]/40 pointer-events-none"
          style={{
            animation: 'cosmic-orbit-1 6s linear infinite',
          }}
        >
          <div className="absolute -top-1 left-1/2 w-2 h-2 -ml-1 rounded-full bg-white shadow-[0_0_8px_#C084FC]" />
        </div>

        {/* Inner tilted orbital energy ring 2 (counter-rotating) */}
        <div
          className="absolute inset-3.5 rounded-full border border-[#818CF8]/35 pointer-events-none"
          style={{
            animation: 'cosmic-orbit-2 4.5s linear infinite',
          }}
        >
          <div className="absolute -bottom-1 left-1/2 w-1.5 h-1.5 -ml-0.75 rounded-full bg-[#E9D5FF] shadow-[0_0_6px_#818CF8]" />
        </div>

        {/* The Smooth Violet Energy Sphere (No solar textures, no flares, smooth luxury material) */}
        <div
          className="relative w-28 h-28 sm:w-32 sm:h-32 rounded-full shadow-[0_0_36px_-4px_rgba(168,85,247,0.7),inset_0_1px_2px_rgba(255,255,255,0.6),inset_0_-4px_12px_rgba(19,9,43,0.9)]"
          style={{
            background:
              'radial-gradient(circle at 35% 30%, #F5EDFF 0%, #C084FC 28%, #7C3AED 58%, #311868 85%, #13092B 100%)',
          }}
        >
          <div className="absolute inset-0 rounded-full border border-white/20 shadow-[inset_0_0_8px_rgba(255,255,255,0.3)]" />
        </div>
      </div>

      {/* Phase 4-5: Refined Typography & Subtitle (SMART INVOICE / INTELLIGENT WORKSPACE) */}
      <div
        className={`relative z-20 flex flex-col items-center text-center mt-6 px-4 transition-all duration-700 ease-out ${
          showText ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <h1 className="font-display text-xl sm:text-2xl font-bold tracking-[0.2em] text-[#F1EDF8] drop-shadow-[0_2px_12px_rgba(187,168,241,0.35)]">
          SMART INVOICE
        </h1>
        <p className="font-mono text-[10px] sm:text-xs uppercase tracking-[0.32em] text-[#BBA8F1] mt-2">
          INTELLIGENT WORKSPACE
        </p>

        {/* Real Status / Error Handling */}
        <div className="mt-5 flex items-center gap-2">
          {!isError ? (
            <div className="flex items-center gap-2.5 text-[11px] font-mono text-[#9892AB]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#BBA8F1] animate-ping" />
              <span>{isReady ? 'Workspace active' : 'Connecting to workspace…'}</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-200 text-xs">
              <span>Backend connection offline</span>
              <div className="flex items-center gap-2 mt-1">
                <button
                  onClick={() => refetch()}
                  className="px-3 py-1 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-white flex items-center gap-1.5 text-[11px] cursor-pointer"
                >
                  <RefreshCw size={12} className={isFetching ? 'animate-spin' : ''} />
                  Retry
                </button>
                <button
                  onClick={() => {
                    setFadingOut(true);
                    sessionStorage.setItem('cosmic_initialized', 'true');
                    setTimeout(() => {
                      setHidden(true);
                      onComplete?.();
                    }, 400);
                  }}
                  className="px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-[#F1EDF8] flex items-center gap-1.5 text-[11px] cursor-pointer"
                >
                  Proceed <ArrowRight size={12} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
