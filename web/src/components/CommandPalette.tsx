import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  LayoutDashboard,
  UploadCloud,
  Receipt,
  Sparkles,
  BarChart3,
  Bot,
  FileSpreadsheet,
  Settings,
  ShieldAlert,
  RefreshCw,
  Sliders,
  CornerDownLeft,
  X,
} from 'lucide-react';
import { useEffects } from './EffectsProvider';
import { useNotifications } from './NotificationProvider';
import { triggerFolderScan } from '../services/api';

interface CommandItem {
  id: string;
  title: string;
  description: string;
  category: 'Navigation' | 'Quick Actions' | 'Preferences';
  icon: React.ElementType;
  keywords: string[];
  shortcut?: string;
  action: () => void;
}

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const inputRef = useRef<HTMLInputElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const navigate = useNavigate();
  const { mode, setMode } = useEffects();
  const notify = useNotifications();

  // Define commands
  const commands: CommandItem[] = useMemo(() => [
    // Navigation
    {
      id: 'nav-dashboard',
      title: 'Dashboard',
      description: 'Overview, financial telemetry, and live metrics',
      category: 'Navigation',
      icon: LayoutDashboard,
      keywords: ['home', 'overview', 'summary', 'metrics', 'spending', 'kpi'],
      shortcut: 'G D',
      action: () => { navigate('/'); setIsOpen(false); },
    },
    {
      id: 'nav-upload',
      title: 'Invoice Upload',
      description: 'Upload PDF invoice for extraction and parsing',
      category: 'Navigation',
      icon: UploadCloud,
      keywords: ['upload', 'pdf', 'drop', 'ingest', 'file'],
      shortcut: 'G U',
      action: () => { navigate('/upload'); setIsOpen(false); },
    },
    {
      id: 'nav-invoices',
      title: 'Invoice Manager',
      description: 'Search, filter, review, and verify all parsed invoices',
      category: 'Navigation',
      icon: Receipt,
      keywords: ['ledger', 'list', 'bills', 'search', 'verify', 'vendor'],
      shortcut: 'G I',
      action: () => { navigate('/invoices'); setIsOpen(false); },
    },
    {
      id: 'nav-chat',
      title: 'Ask AI Assistant',
      description: 'Conversational RAG intelligence powered by Gemini 2.5 Flash',
      category: 'Navigation',
      icon: Sparkles,
      keywords: ['gemini', 'chat', 'ask', 'question', 'rag', 'query'],
      shortcut: 'G A',
      action: () => { navigate('/chat'); setIsOpen(false); },
    },
    {
      id: 'nav-analytics',
      title: 'Analytics & Insights',
      description: 'Deep spending trends, vendor breakdown, and currency distribution',
      category: 'Navigation',
      icon: BarChart3,
      keywords: ['charts', 'graphs', 'monthly', 'trends', 'breakdown', 'stats'],
      action: () => { navigate('/analytics'); setIsOpen(false); },
    },
    {
      id: 'nav-automation',
      title: 'RPA & Automation',
      description: 'Gmail synchronization and folder monitoring',
      category: 'Navigation',
      icon: Bot,
      keywords: ['gmail', 'sync', 'watch', 'folder', 'poller', 'auto'],
      action: () => { navigate('/automation'); setIsOpen(false); },
    },
    {
      id: 'nav-reports',
      title: 'Reports & Exports',
      description: 'Generate and download CSV, Excel, and PDF audit summaries',
      category: 'Navigation',
      icon: FileSpreadsheet,
      keywords: ['export', 'download', 'csv', 'xlsx', 'excel', 'audit'],
      action: () => { navigate('/reports'); setIsOpen(false); },
    },
    {
      id: 'nav-settings',
      title: 'Settings',
      description: 'Workspace preferences, currency, and vector re-indexing',
      category: 'Navigation',
      icon: Settings,
      keywords: ['config', 'preferences', 'currency', 'reindex', 'api'],
      action: () => { navigate('/settings'); setIsOpen(false); },
    },

    // Quick Actions
    {
      id: 'action-duplicates',
      title: 'Review Suspected Duplicates',
      description: 'Inspect invoices flagged by duplicate detection shield',
      category: 'Quick Actions',
      icon: ShieldAlert,
      keywords: ['duplicates', 'flagged', 'suspected', 'fraud', 'review'],
      action: () => { navigate('/invoices?status=suspected_duplicate'); setIsOpen(false); },
    },
    {
      id: 'action-scan-folder',
      title: 'Scan Invoices Watch Folder',
      description: 'Trigger immediate local watch directory ingestion',
      category: 'Quick Actions',
      icon: RefreshCw,
      keywords: ['scan', 'folder', 'ingest', 'disk', 'watch'],
      action: async () => {
        setIsOpen(false);
        notify.info('Scanning watch directory for new invoices...', 'Folder Scan');
        try {
          const res = await triggerFolderScan();
          notify.success(`Scanned ${res.total_scanned} files (${res.new_imported} imported, ${res.duplicates_skipped} duplicates skipped).`, 'Scan Completed');
        } catch (e: any) {
          notify.error(e?.message || 'Folder scan request failed.', 'Scan Error');
        }
      },
    },

    // Preferences & Modes
    {
      id: 'pref-mode-full',
      title: `Visual Effects: Full ${mode === 'full' ? '(Active)' : ''}`,
      description: 'Maximum cosmic particles and cinematic depth',
      category: 'Preferences',
      icon: Sliders,
      keywords: ['mode', 'effects', 'full', 'particles', 'graphics'],
      action: () => { setMode('full'); notify.info('Visual effects mode set to Full', 'Settings'); setIsOpen(false); },
    },
    {
      id: 'pref-mode-balanced',
      title: `Visual Effects: Balanced ${mode === 'balanced' ? '(Active)' : ''}`,
      description: 'Optimal balance of cosmic aesthetics and smooth 60 FPS performance',
      category: 'Preferences',
      icon: Sliders,
      keywords: ['mode', 'effects', 'balanced', 'default', 'performance'],
      action: () => { setMode('balanced'); notify.info('Visual effects mode set to Balanced', 'Settings'); setIsOpen(false); },
    },
    {
      id: 'pref-mode-reduced',
      title: `Visual Effects: Reduced ${mode === 'reduced' ? '(Active)' : ''}`,
      description: 'Lightweight static mode for low-power devices and reduced motion',
      category: 'Preferences',
      icon: Sliders,
      keywords: ['mode', 'effects', 'reduced', 'minimal', 'light', 'battery'],
      action: () => { setMode('reduced'); notify.info('Visual effects mode set to Reduced', 'Settings'); setIsOpen(false); },
    },
  ], [navigate, mode, setMode, notify]);

  // Filter commands based on query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return commands;
    const cleanQuery = query.toLowerCase().trim();

    return commands.filter((cmd) => {
      const matchTitle = cmd.title.toLowerCase().includes(cleanQuery);
      const matchDesc = cmd.description.toLowerCase().includes(cleanQuery);
      const matchKeyword = cmd.keywords.some((k) => k.toLowerCase().includes(cleanQuery));
      return matchTitle || matchDesc || matchKeyword;
    });
  }, [commands, query]);

  // Reset index on search change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Keyboard shortcut listener: Ctrl+K / Cmd+K / custom event
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if modifier is not pressed and user is in an input
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        setIsOpen(false);
      }
    };

    const handleCustomOpen = () => setIsOpen(true);

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('open-command-palette', handleCustomOpen);

    return () => {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('open-command-palette', handleCustomOpen);
    };
  }, [isOpen]);

  // Manage focus restoration
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      setTimeout(() => inputRef.current?.focus(), 30);
    } else {
      setQuery('');
      previousActiveElement.current?.focus();
    }
  }, [isOpen]);

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current && listRef.current.children[selectedIndex]) {
      const selectedEl = listRef.current.children[selectedIndex] as HTMLElement;
      selectedEl.scrollIntoView({ block: 'nearest' });
    }
  }, [selectedIndex]);

  // Keyboard navigation inside list with Arrow keys and Tab/Shift+Tab
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown' || (e.key === 'Tab' && !e.shiftKey)) {
      e.preventDefault();
      setSelectedIndex((prev) => (filteredCommands.length ? (prev + 1) % filteredCommands.length : 0));
    } else if (e.key === 'ArrowUp' || (e.key === 'Tab' && e.shiftKey)) {
      e.preventDefault();
      setSelectedIndex((prev) => (filteredCommands.length ? (prev - 1 + filteredCommands.length) % filteredCommands.length : 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      className="fixed inset-0 z-50 flex items-start justify-center pt-[12vh] sm:pt-[15vh] px-4 animate-fade-in"
    >
      {/* Dimmed backdrop */}
      <div
        className="fixed inset-0 bg-black/65 backdrop-blur-md transition-opacity"
        onClick={() => setIsOpen(false)}
        aria-hidden="true"
      />

      {/* Floating Glass Modal */}
      <div
        className="relative w-full max-w-xl rounded-2xl bg-[#0c0819]/95 backdrop-blur-2xl border border-[rgba(184,160,248,0.22)] shadow-[0_24px_70px_rgba(0,0,0,0.8),0_0_35px_rgba(139,92,246,0.15)] overflow-hidden flex flex-col max-h-[75vh]"
        style={{
          background: 'linear-gradient(155deg, rgba(22, 16, 46, 0.96) 0%, rgba(10, 7, 20, 0.98) 100%)',
        }}
      >
        {/* Search Input Bar */}
        <div className="relative flex items-center px-4 py-3.5 border-b border-white/8">
          <Search className="w-4 h-4 text-[#BBA8F1] shrink-0 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder="Search commands, navigate, or run actions..."
            className="w-full bg-transparent text-sm text-[#F1EDF8] placeholder-[#8E83A3] focus:outline-none font-sans font-light"
          />
          {query ? (
            <button
              onClick={() => setQuery('')}
              className="p-1 rounded-md text-[#8E83A3] hover:text-[#F1EDF8] transition cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          ) : (
            <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/6 text-[#9F94B8] border border-white/10">
              ESC
            </kbd>
          )}
        </div>

        {/* Results List */}
        <div
          ref={listRef}
          className="flex-1 overflow-y-auto p-2 space-y-1 divide-y divide-white/[0.03] overscroll-contain"
        >
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = cmd.icon;

              return (
                <div
                  key={cmd.id}
                  onClick={() => cmd.action()}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'bg-[rgba(139,92,246,0.22)] border border-[rgba(184,160,248,0.3)] text-white shadow-[0_4px_16px_rgba(139,92,246,0.18)]'
                      : 'hover:bg-white/[0.03] border border-transparent text-[#D8D2E6]'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected
                          ? 'bg-[#BBA8F1]/20 text-[#E9D5FF]'
                          : 'cosmic-glass-control text-[#BBA8F1]'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="min-w-0 pr-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-sans font-medium truncate text-[#F1EDF8]">
                          {cmd.title}
                        </span>
                        <span className="text-[9px] font-mono uppercase px-2 py-0.2 rounded bg-white/5 text-[#9892AB]">
                          {cmd.category}
                        </span>
                      </div>
                      <p className="text-[11px] font-sans font-light text-[#9E94B3] truncate">
                        {cmd.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {cmd.shortcut && (
                      <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 border border-white/8 text-[#A79BBE]">
                        {cmd.shortcut}
                      </kbd>
                    )}
                    {isSelected && (
                      <CornerDownLeft className="w-3.5 h-3.5 text-[#C4B5FD] animate-pulse" />
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="py-12 px-4 text-center space-y-2">
              <Search className="w-6 h-6 text-[#7E7295] mx-auto opacity-60" />
              <p className="text-xs text-[#E5DDFC] font-medium">No matching commands found</p>
              <p className="text-[11px] text-[#8E83A3]">
                Try searching for "invoices", "upload", "analytics", or "gemini"
              </p>
            </div>
          )}
        </div>

        {/* Palette Footer Hints */}
        <div className="px-4 py-2.5 bg-black/30 border-t border-white/6 flex items-center justify-between text-[11px] font-mono text-[#8E83A3]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white/6 text-[#C4B5FD]">↑↓</kbd> navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white/6 text-[#C4B5FD]">↵</kbd> select
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white/6 text-[#C4B5FD]">esc</kbd> close
            </span>
          </div>
          <span className="text-[10px] text-[#BBA8F1]/70">SMART INVOICE PALETTE</span>
        </div>
      </div>
    </div>
  );
};
