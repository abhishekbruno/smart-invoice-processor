import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

export type VisualMode = 'full' | 'balanced' | 'reduced';
const EffectsContext = createContext({ mode: 'balanced' as VisualMode, setMode: (_mode: VisualMode) => {}, reduced: false, reducedEffects: false, setReducedEffects: (_value: boolean) => {} });
export const useEffects = () => useContext(EffectsContext);

export function EffectsProvider({ children }: { children: ReactNode }) {
  const [systemReduced, setSystemReduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const [mode, setMode] = useState<VisualMode>(() => {
    try {
      const saved = localStorage.getItem('cosmic-visual-mode');
      if (saved === 'full' || saved === 'balanced' || saved === 'reduced') return saved;
      return localStorage.getItem('cosmic-reduced-effects') === 'true' ? 'reduced' : 'balanced';
    } catch { return 'balanced'; }
  });
  const reducedEffects = mode === 'reduced';
  const setReducedEffects = (value: boolean) => setMode(value ? 'reduced' : 'balanced');
  const reduced = systemReduced || reducedEffects;
  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setSystemReduced(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.reducedEffects = String(reduced);
    document.documentElement.dataset.visualMode = reduced ? 'reduced' : mode;
    try { localStorage.setItem('cosmic-visual-mode', mode); } catch { /* Storage may be disabled. */ }
  }, [reduced, mode]);
  useEffect(() => {
    const update = () => { document.documentElement.dataset.pageHidden = String(document.hidden); };
    update();
    document.addEventListener('visibilitychange', update);
    return () => document.removeEventListener('visibilitychange', update);
  }, []);
  return <EffectsContext.Provider value={{ mode, setMode, reduced, reducedEffects, setReducedEffects }}>{children}</EffectsContext.Provider>;
}
