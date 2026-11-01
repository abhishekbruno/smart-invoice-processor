import React, { useMemo, useRef, useState, useLayoutEffect, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchSystemStatus, fetchSettings } from '../services/api';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Receipt,
  UploadCloud,
  MessageSquare,
  BarChart3,
  Bot,
  FileText,
  Settings,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const navRef = useRef<HTMLElement>(null);
  const itemRefs = useRef<(HTMLAnchorElement | null)[]>([]);
  const [pillState, setPillState] = useState<{ top: number; height: number; opacity: number } | null>(null);

  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchSystemStatus,
    staleTime: 30000,
  });

  const { data: settingsData } = useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
    staleTime: 60000,
  });

  const currency = settingsData?.data?.preferred_display_currency || 'INR';

  const navItems = useMemo(
    () => [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard },
      { to: '/invoices', label: 'Invoice Manager', icon: Receipt },
      { to: '/upload', label: 'Invoice Upload', icon: UploadCloud },
      { to: '/chat', label: 'Ask AI', icon: MessageSquare, badge: 'Gemini' },
      { to: '/analytics', label: 'Analytics', icon: BarChart3 },
      { to: '/automation', label: 'Automation', icon: Bot },
      { to: '/reports', label: 'Reports', icon: FileText },
      { to: '/settings', label: 'Settings', icon: Settings },
    ],
    []
  );

  // Compute active item index for smooth gliding indicator
  const activeIndex = navItems.findIndex((item) =>
    item.to === '/' ? location.pathname === '/' : location.pathname.startsWith(item.to)
  );

  useLayoutEffect(() => {
    if (activeIndex >= 0) {
      const activeEl = itemRefs.current[activeIndex];
      if (activeEl) {
        setPillState({
          top: activeEl.offsetTop,
          height: activeEl.offsetHeight,
          opacity: 1,
        });
      }
    } else {
      setPillState((prev) => (prev ? { ...prev, opacity: 0 } : null));
    }
  }, [activeIndex, location.pathname]);

  // Handle resize smoothly
  useEffect(() => {
    const nav = navRef.current;
    if (!nav || !('ResizeObserver' in window)) return;
    const ro = new ResizeObserver(() => {
      if (activeIndex >= 0 && itemRefs.current[activeIndex]) {
        const activeEl = itemRefs.current[activeIndex]!;
        setPillState({
          top: activeEl.offsetTop,
          height: activeEl.offsetHeight,
          opacity: 1,
        });
      }
    });
    ro.observe(nav);
    return () => ro.disconnect();
  }, [activeIndex]);

  const isHealthy = status?.status === 'healthy';

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-md lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`cosmic-sidebar fixed top-0 bottom-0 left-0 z-40 w-60 bg-[#080614]/90 backdrop-blur-2xl border-r border-[rgba(184,160,248,0.14)] flex flex-col transition-transform duration-200 ease-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand header */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-white/[0.06]">
          <div className="w-7 h-7 rounded-lg cosmic-glass-control flex items-center justify-center text-[#BBA8F1] font-mono text-xs font-semibold tracking-tighter shadow-[0_0_12px_rgba(187,168,241,0.2)]">
            AI
          </div>
          <div className="min-w-0">
            <span className="font-display font-semibold text-[#F1EDF8] tracking-tight text-xs block truncate">
              Smart Invoice
            </span>
            <span className="text-[10px] text-[#9892AB] font-mono uppercase tracking-widest block truncate">
              Intelligent Workspace
            </span>
          </div>
        </div>

        {/* Navigation list with Single Shared Gliding Active Indicator */}
        <nav ref={navRef} className="relative flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {/* Gliding Active Indicator Pill */}
          {pillState && (
            <div
              aria-hidden="true"
              className="absolute left-3 right-3 rounded-xl pointer-events-none z-0 transition-[transform,height,opacity] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
              style={{
                top: 0,
                transform: `translate3d(0, ${pillState.top}px, 0)`,
                height: `${pillState.height}px`,
                opacity: pillState.opacity,
                background:
                  'linear-gradient(90deg, rgba(75, 55, 178, 0.40), rgba(36, 23, 77, 0.28))',
                border: '1px solid rgba(187, 168, 241, 0.45)',
                boxShadow:
                  '0 0 22px -3px rgba(115, 85, 224, 0.42), inset 0 1px 0 rgba(216, 201, 255, 0.18)',
              }}
            >
              {/* Left glowing neon accent notch */}
              <div className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-[#BBA8F1] shadow-[0_0_10px_#BBA8F1,0_0_4px_#FFF]" />
            </div>
          )}

          {navItems.map((item, index) => {
            const Icon = item.icon;
            const isActive =
              item.to === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(item.to);

            return (
              <NavLink
                key={item.to}
                ref={(el) => {
                  itemRefs.current[index] = el;
                }}
                to={item.to}
                onClick={onClose}
                className={`relative z-10 flex items-center justify-between px-3 h-[42px] rounded-xl text-xs font-sans font-medium transition-colors duration-200 select-none ${
                  isActive
                    ? 'text-[#F1EDF8] font-semibold'
                    : 'text-[#B8B2C8] hover:text-[#F1EDF8] hover:bg-white/[0.04]'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-colors duration-200 ${
                      isActive ? 'text-[#BBA8F1]' : 'text-[#8E86A5]'
                    }`}
                  />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[9px] uppercase font-mono tracking-wider px-2 py-0.5 rounded-full font-semibold bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/30">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Minimal status footer */}
        <div className="p-3.5 border-t border-white/[0.06] space-y-2">
          <div className="px-3.5 py-2.5 rounded-xl cosmic-glass-subtle flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <span
                className={`w-2 h-2 rounded-full shrink-0 ${
                  isHealthy
                    ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                    : statusLoading
                    ? 'bg-amber-400 animate-pulse'
                    : 'bg-rose-400'
                }`}
              />
              <span className="text-[11px] font-sans font-medium text-[#B8B2C8] truncate">
                {isHealthy
                  ? 'FastAPI Active'
                  : statusLoading
                  ? 'Connecting…'
                  : 'Backend Offline'}
              </span>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="text-[10px] font-mono text-[#BBA8F1] px-1.5 py-0.5 rounded bg-white/[0.04]">
                {currency}
              </span>
              <span className="text-[10px] font-mono text-[#9892AB]">v2.0</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
