import { Suspense, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { useLocation, useNavigationType, useOutlet } from 'react-router-dom';
import { useEffects } from './EffectsProvider';
import { CosmicLoader } from './CosmicLoader';

export function AnimatedPage() {
  const outlet = useOutlet();
  const location = useLocation();
  const navigationType = useNavigationType();
  const { reduced } = useEffects();
  const [shown, setShown] = useState({ pathname: location.pathname, outlet });
  const container = useRef<HTMLDivElement>(null);
  const scrollPositions = useRef(new Map<string, number>());
  const pendingScroll = useRef<{ pathname: string; top: number } | null>(null);
  const changing = shown.pathname !== location.pathname;
  const restoreScroll = useCallback((pathname: string) => {
    if (pendingScroll.current?.pathname !== pathname) return;
    window.scrollTo({ top: pendingScroll.current.top, behavior: 'instant' });
    pendingScroll.current = null;
  }, []);

  useEffect(() => {
    if (!changing) return;
    const node = container.current;
    scrollPositions.current.set(shown.pathname, window.scrollY);
    const animation = !reduced ? node?.animate?.([{ opacity: 1 }, { opacity: 0.25, transform: 'translateY(-6px)' }], { duration: 100, fill: 'forwards' }) : undefined;
    const timer = window.setTimeout(() => {
      animation?.cancel();
      pendingScroll.current = { pathname: location.pathname, top: navigationType === 'POP' ? scrollPositions.current.get(location.pathname) ?? 0 : 0 };
      setShown({ pathname: location.pathname, outlet });
    }, reduced ? 0 : 100);
    return () => { window.clearTimeout(timer); animation?.cancel(); };
  }, [location.pathname, changing, reduced, outlet, shown.pathname, navigationType]);

  useEffect(() => {
    if (reduced || changing) return;
    const animation = container.current?.animate?.([{ opacity: 0.35, transform: 'translateY(12px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 200, easing: 'ease-out' });
    return () => animation?.cancel();
  }, [shown.pathname, reduced, changing]);

  return (
    <div ref={container} inert={changing} className="animated-page">
      <Suspense
        fallback={
          <div className="min-h-96 flex items-center justify-center p-8" role="status">
            <CosmicLoader size="md" label="Loading workspace…" />
          </div>
        }
      >
        <CommittedPage
          pathname={changing ? shown.pathname : location.pathname}
          restoreScroll={restoreScroll}
        >
          {changing ? shown.outlet : outlet}
        </CommittedPage>
      </Suspense>
    </div>
  );
}

// This effect commits only when the lazy destination has resolved, never on its fallback.
function CommittedPage({ children, pathname, restoreScroll }: { children: ReactNode; pathname: string; restoreScroll: (pathname: string) => void }) {
  useLayoutEffect(() => restoreScroll(pathname), [pathname, restoreScroll]);
  return children;
}
