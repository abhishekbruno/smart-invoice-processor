import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchSystemStatus } from '../services/api';
import { useEffects } from './EffectsProvider';
import { ArrowRight, RefreshCw } from 'lucide-react';

interface Props {
  onComplete?: () => void;
}

export const AppLoadingScreen: React.FC<Props> = ({ onComplete }) => {
  const { reduced } = useEffects();
  const [stage, setStage] = useState<'glow' | 'sphere' | 'expand' | 'text' | 'done'>('glow');
  const [fadingOut, setFadingOut] = useState(false);
  const [hidden, setHidden] = useState(false);

  // Real backend health check for actual initialization
  const { data: status, isError, refetch, isFetching } = useQuery({
    queryKey: ['system-status-init'],
    queryFn: fetchSystemStatus,
    retry: 2,
    staleTime: 60000,
  });

  const isReady = !!status && !isFetching;

  // Staged cinematic sequence matching user specification
  useEffect(() => {
    // If reduced motion is requested or already initialized in this session, skip immediately
    if (reduced || sessionStorage.getItem('cosmic_initialized') === 'true') {
      setHidden(true);
      onComplete?.();
      return;
    }

    const t1 = setTimeout(() => setStage('sphere'), 300);
    const t2 = setTimeout(() => setStage('expand'), 700);
    const t3 = setTimeout(() => setStage('text'), 1100);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [reduced, onComplete]);

  // Transition away once animation reached text stage and backend is ready (or after reasonable timeout)
  useEffect(() => {
    if (hidden || reduced) return;

    if (stage === 'text' && (isReady || isError)) {
      const dismissTimer = setTimeout(() => {
        if (!isError) {
          setFadingOut(true);
          sessionStorage.setItem('cosmic_initialized', 'true');
          const unmountTimer = setTimeout(() => {
            setHidden(true);
            onComplete?.();
          }, 450);
          return () => clearTimeout(unmountTimer);
        }
      }, 500);

      return () => clearTimeout(dismissTimer);
    }
  }, [stage, isReady, isError, hidden, reduced, onComplete]);

  if (hidden) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Application loading screen"
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#020203] select-none transition-all duration-500 ease-out ${
        fadingOut ? 'opacity-0 scale-105 pointer-events-none' : 'opacity-100 scale-100'
      }`}
    >
      {/* 1. Deep cosmic atmospheric ambient backdrop */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className={`absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_50%,rgba(103,70,186,0.22),transparent_75%)] transition-opacity duration-1000 ${
            stage !== 'glow' ? 'opacity-100' : 'opacity-40'
          }`}
        />
        {/* Subtle emerging background star points */}
        <div
          className={`absolute inset-0 transition-opacity duration-1000 ${
            stage === 'expand' || stage === 'text' ? 'opacity-70' : 'opacity-0'
          }`}
        >
          {[...Array(24)].map((_, i) => (
            <span
              key={i}
              className="absolute rounded-full bg-[#E5DDFC]"
              style={{
                top: `${(i * 37.3) % 94}%`,
                left: `${(i * 61.8) % 96}%`,
                width: i % 4 === 0 ? '2px' : '1.2px',
                height: i % 4 === 0 ? '2px' : '1.2px',
                opacity: 0.3 + (i % 5) * 0.14,
                animation: `pulse ${(i % 3) + 2}s infinite alternate`,
              }}
            />
          ))}
        </div>
      </div>

      {/* 2. Centered Cosmic Solar Sphere / Torus Core (Inspired by uploaded reference media) */}
      <div className="relative z-10 flex items-center justify-center w-64 h-64 sm:w-80 sm:h-80">
        {/* Expanding energy wave rings */}
        <div
          className={`absolute inset-0 rounded-full border border-[#BBA8F1]/30 transition-all duration-1000 ${
            stage === 'expand' || stage === 'text'
              ? 'scale-125 opacity-30 animate-ping'
              : 'scale-90 opacity-0'
          }`}
          style={{ animationDuration: '3s' }}
        />
        <div
          className={`absolute inset-6 rounded-full border border-[#9061F9]/20 transition-all duration-1000 ${
            stage === 'expand' || stage === 'text' ? 'scale-110 opacity-40' : 'scale-95 opacity-0'
          }`}
        />

        {/* Outer radiant neon magenta/violet halo */}
        <div
          className={`absolute inset-8 rounded-full bg-gradient-to-tr from-[#7C3AED]/40 via-[#C084FC]/30 to-[#3B82F6]/30 blur-2xl transition-all duration-700 ${
            stage !== 'glow' ? 'scale-100 opacity-90' : 'scale-50 opacity-20'
          }`}
        />

        {/* Main Cosmic Solar Ring / Torus Visual (Derived from uploaded reference photo) */}
        <div
          className={`relative w-48 h-48 sm:w-60 sm:h-60 rounded-full transition-all duration-700 ease-out ${
            stage !== 'glow' ? 'scale-100 opacity-100' : 'scale-75 opacity-0'
          }`}
        >
          {/* Neon rim illumination with dimensional shadows */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `
                radial-gradient(circle at 75% 20%, rgba(244,114,182,0.95), transparent 45%),
                radial-gradient(circle at 25% 80%, rgba(99,102,241,0.85), transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(139,92,246,0.9), transparent 70%)
              `,
              boxShadow: `
                0 0 50px rgba(168,85,247,0.55),
                inset 0 0 45px rgba(236,72,153,0.5),
                inset 0 0 18px rgba(255,255,255,0.7)
              `,
              animation: 'spin 18s linear infinite',
            }}
          />

          {/* Inner dark cosmic void center */}
          <div className="absolute inset-4 rounded-full bg-[#020203] shadow-[inset_0_0_30px_rgba(30,15,60,0.9)] flex items-center justify-center">
            {/* Fine central stellar ember dot */}
            <div className="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_12px_#E879F9] animate-pulse" />
          </div>

          {/* Fine orbital energy particle streak */}
          <div
            className="absolute inset-[-4px] rounded-full border border-t-white/80 border-r-[#C084FC]/60 border-b-transparent border-l-transparent animate-spin"
            style={{ animationDuration: '4s' }}
          />
        </div>
      </div>

      {/* 3. Refined Typography & Subtitle */}
      <div
        className={`relative z-10 flex flex-col items-center text-center mt-6 px-4 transition-all duration-700 ${
          stage === 'text' ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <h1 className="font-display text-xl sm:text-2xl font-bold tracking-[0.2em] text-[#F1EDF8] drop-shadow-[0_2px_12px_rgba(187,168,241,0.35)]">
          SMART INVOICE PROCESSOR
        </h1>
        <p className="font-mono text-[10px] sm:text-xs uppercase tracking-[0.32em] text-[#BBA8F1] mt-2">
          INTELLIGENT WORKSPACE
        </p>

        {/* Initialization Status */}
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

