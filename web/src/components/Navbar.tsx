import React from 'react';
import { Menu, RefreshCw, Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchSettings, fetchSystemStatus } from '../services/api';

interface NavbarProps {
  onToggleSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  const { data: settingsData, refetch } = useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
    staleTime: 60000,
  });

  const { data: systemStatus, isError, isLoading, refetch: refetchStatus } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchSystemStatus,
    staleTime: 30000,
  });

  const curr = settingsData?.data?.preferred_display_currency || 'INR';
  const isHealthy = systemStatus?.status === 'healthy';

  const handleOpenPalette = () => {
    window.dispatchEvent(new CustomEvent('open-command-palette'));
  };

  return (
    <header className="h-16 bg-[#020203]/80 backdrop-blur-2xl border-b border-[rgba(184,160,248,0.14)] sticky top-0 z-30 px-5 sm:px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 min-h-[40px] min-w-[40px] flex items-center justify-center rounded-xl text-[#B8B2C8] hover:text-[#F1EDF8] hover:bg-white/[0.04] border border-transparent hover:border-white/10 lg:hidden cursor-pointer"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Command Palette Trigger */}
        <button
          onClick={handleOpenPalette}
          className="flex items-center gap-2.5 px-3 py-1.5 rounded-full cosmic-glass-control text-[11px] text-[#B8B2C8] hover:text-[#F1EDF8] hover:border-[#BBA8F1]/40 transition cursor-pointer"
          aria-label="Open command palette (Ctrl+K)"
        >
          <Search className="w-3.5 h-3.5 text-[#BBA8F1]" />
          <span className="hidden sm:inline font-sans">Command Palette</span>
          <kbd className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/6 text-[#C4B5FD] border border-white/10">
            Ctrl K
          </kbd>
        </button>

        <div className="hidden md:flex items-center gap-2.5">
          <span className="text-[11px] font-sans font-medium px-3 py-1 rounded-full cosmic-glass-control text-[#B8B2C8]">
            Currency: <strong className="text-[#F1EDF8] font-mono font-semibold">{curr}</strong>
          </span>
          <span className="text-[11px] font-sans font-medium px-3 py-1 rounded-full cosmic-glass-pill">
            AI Engine: <strong className="text-[#F1EDF8] font-semibold">Gemini 2.5 Flash</strong>
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3.5 py-1 rounded-full cosmic-glass-control text-[11px] text-[#B8B2C8] font-sans">
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isHealthy
                ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]'
                : 'bg-rose-400 shadow-[0_0_6px_rgba(244,63,94,0.6)]'
            }`}
          />
          <span>{isHealthy ? 'Connected' : isLoading ? 'Connecting…' : isError ? 'Connection unavailable' : 'Check connection'}</span>
        </div>

        <button
          onClick={() => { refetch(); refetchStatus(); }}
          title="Refresh connection"
          className="p-1.5 rounded-xl text-[#9892AB] hover:text-[#F1EDF8] hover:bg-white/[0.03] transition cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
