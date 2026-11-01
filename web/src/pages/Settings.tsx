import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Coins,
  Cpu,
  RefreshCw,
  CheckCircle2,
  Check,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  fetchSettings,
  updatePreferredCurrency,
  triggerVectorReindex,
  fetchSystemStatus,
} from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { useEffects } from '../components/EffectsProvider';

export const Settings: React.FC = () => {
  const { reduced, reducedEffects, mode, setMode } = useEffects();
  const queryClient = useQueryClient();
  const [currencySuccess, setCurrencySuccess] = useState(false);
  const [reindexSuccess, setReindexSuccess] = useState(false);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  const { data: settingsData } = useQuery({
    queryKey: ['settings'],
    queryFn: fetchSettings,
    staleTime: 60000,
  });

  const { data: systemStatus } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchSystemStatus,
    staleTime: 30000,
  });

  const currencyMutation = useMutation({
    mutationFn: updatePreferredCurrency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      setCurrencySuccess(true);
      setTimeout(() => setCurrencySuccess(false), 2500);
    },
  });

  const reindexMutation = useMutation({
    mutationFn: triggerVectorReindex,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-status'] });
      queryClient.invalidateQueries({ queryKey: ['chat-status'] });
      setReindexSuccess(true);
      setTimeout(() => setReindexSuccess(false), 2500);
    },
  });

  const settings = settingsData?.data;
  const rates = settings?.latest_reference_rates_usd || {};

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
          <span>System Parameters</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
          Settings & Preferences
        </h1>
        <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
          Configure multi-currency valuation defaults and monitor underlying system storage.
        </p>
      </div>

      <CosmicGlassPanel className="p-6 flex items-center justify-between gap-5">
        <div><h2 className="text-sm font-medium">Visual Effects</h2><p id="effects-description" className="text-xs text-[#B8B2C8] mt-2">Balanced uses fewer particles and lighter glass. Full adds richer motion; Reduced removes continuous animation. Your system motion preference is always respected.</p>{reduced && !reducedEffects && <p className="text-xs text-[#BBA8F1] mt-2">Reduced motion is enabled by your device.</p>}</div>
        <select aria-label="Visual Effects" value={mode} onChange={event => setMode(event.target.value as 'full' | 'balanced' | 'reduced')} className="cosmic-glass-control p-2 text-xs"><option value="full">Full</option><option value="balanced">Balanced</option><option value="reduced">Reduced</option></select>
      </CosmicGlassPanel>

      {/* Section 1: Valuation Currency in Cosmic Violet Glass */}
      <CosmicGlassPanel className="p-6 sm:p-7 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl cosmic-glass-control text-[#BBA8F1]">
              <Coins className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">Preferred Valuation Currency</h3>
              <p className="text-[11px] text-[#9892AB] font-sans">
                Default currency for dashboard KPIs, summaries, and mobile views
              </p>
            </div>
          </div>
          {currencySuccess && (
            <span className="inline-flex items-center gap-1.5 text-[11px] text-emerald-400 font-medium font-sans">
              <Check className="w-3.5 h-3.5" /> Saved
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { code: 'INR', symbol: '₹', label: 'Indian Rupee' },
            { code: 'USD', symbol: '$', label: 'US Dollar' },
            { code: 'EUR', symbol: '€', label: 'Euro' },
            { code: 'GBP', symbol: '£', label: 'British Pound' },
          ].map((c) => {
            const isSelected = settings?.preferred_display_currency === c.code;
            return (
              <button
                key={c.code}
                onClick={() => currencyMutation.mutate(c.code)}
                disabled={currencyMutation.isPending}
                className={`p-4 rounded-2xl border text-center transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#4B37B2]/30 border-[#BBA8F1]/45 text-[#F1EDF8] shadow-[0_0_15px_rgba(75,55,178,0.25)] font-semibold'
                    : 'cosmic-glass-control text-[#B8B2C8] hover:border-white/20 hover:text-[#F1EDF8]'
                }`}
              >
                <span className="text-lg font-bold block">{c.symbol}</span>
                <span className="text-xs font-mono font-semibold block mt-1">{c.code}</span>
                <span className="text-[10px] text-[#9892AB] block mt-0.5 font-sans">{c.label}</span>
              </button>
            );
          })}
        </div>

        {/* Live Reference Rates */}
        <div className="pt-4 border-t border-white/6">
          <div className="flex items-center justify-between text-[11px] text-[#9892AB] font-mono mb-2.5">
            <span>Reference Rates (Base: USD 1.00)</span>
            <span>Source: {settings?.exchange_rate_source || 'Frankfurter / ECB'}</span>
          </div>
          <div className="grid grid-cols-3 gap-2.5 text-xs">
            <div className="p-3 cosmic-glass-subtle rounded-xl">
              <span className="text-[10px] text-[#9892AB] font-mono block uppercase tracking-wider">INR</span>
              <span className="font-mono text-[#BBA8F1] font-semibold block mt-1">
                {rates['INR'] != null ? '₹' + rates['INR'].toFixed(2) : '—'}
              </span>
            </div>
            <div className="p-3 cosmic-glass-subtle rounded-xl">
              <span className="text-[10px] text-[#9892AB] font-mono block uppercase tracking-wider">EUR</span>
              <span className="font-mono text-[#8879A7] font-semibold block mt-1">
                {rates['EUR'] != null ? '€' + rates['EUR'].toFixed(4) : '—'}
              </span>
            </div>
            <div className="p-3 cosmic-glass-subtle rounded-xl">
              <span className="text-[10px] text-[#9892AB] font-mono block uppercase tracking-wider">GBP</span>
              <span className="font-mono text-[#F1EDF8] font-semibold block mt-1">
                {rates['GBP'] != null ? '£' + rates['GBP'].toFixed(4) : '—'}
              </span>
            </div>
          </div>
        </div>
      </CosmicGlassPanel>

      {/* Section 2: ChromaDB Vector Reindexing */}
      <CosmicGlassPanel className="p-6 sm:p-7 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">Chroma Vector Database</h3>
            <p className="text-[11px] text-[#9892AB] mt-0.5 font-sans font-light">
              Re-chunks SQLite invoices and refreshes all document embeddings
            </p>
          </div>
          <button
            onClick={() => reindexMutation.mutate()}
            disabled={reindexMutation.isPending}
            className="aovix-gradient-btn px-5 py-2.5 rounded-full disabled:opacity-40 text-xs font-sans font-semibold tracking-wide transition flex items-center gap-2 cursor-pointer shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
          >
            {reindexMutation.isPending ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Re-indexing...</span>
              </>
            ) : reindexSuccess ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
                <span>Synchronized</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reindex Now</span>
              </>
            )}
          </button>
        </div>
      </CosmicGlassPanel>

      {/* Section 3: Expandable System Diagnostics */}
      <CosmicGlassPanel variant="subtle" className="rounded-2xl overflow-hidden p-0">
        <button
          onClick={() => setShowDiagnostics((prev) => !prev)}
          className="w-full px-6 py-4 flex items-center justify-between text-xs font-medium text-[#B8B2C8] hover:text-[#F1EDF8] transition cursor-pointer font-sans"
        >
          <div className="flex items-center gap-2.5">
            <Cpu className="w-4 h-4 text-[#8879A7]" />
            <span>System Architecture & Storage Diagnostics</span>
          </div>
          <div className="flex items-center gap-2.5">
            <StatusBadge status={systemStatus?.status || 'online'} size="sm" />
            {showDiagnostics ? <ChevronUp className="w-4 h-4 text-[#BBA8F1]" /> : <ChevronDown className="w-4 h-4 text-[#8879A7]" />}
          </div>
        </button>

        {showDiagnostics && (
          <div className="p-6 border-t border-white/6 space-y-4 text-xs animate-fade-in font-mono">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div className="p-4 cosmic-glass-subtle rounded-xl">
                <span className="text-[10px] text-[#9892AB] uppercase font-mono block tracking-wider">SQLite Database</span>
                <span className="font-mono text-[#F1EDF8] text-[11px] block truncate mt-1">
                  {systemStatus?.database?.path || 'storage/database/invoices.db'}
                </span>
                <span className="text-[10px] text-[#9892AB] block mt-1.5">
                  Total records: {systemStatus?.database?.counts?.total ?? 0}
                </span>
              </div>
              <div className="p-4 cosmic-glass-subtle rounded-xl">
                <span className="text-[10px] text-[#9892AB] uppercase font-mono block tracking-wider">ChromaDB Collection</span>
                <span className="font-mono text-[#F1EDF8] text-[11px] block mt-1">invoice_documents</span>
                <span className="text-[10px] text-[#9892AB] block mt-1.5">
                  Indexed chunks: {systemStatus?.vector_store?.total_chunks ?? 0}
                </span>
              </div>
            </div>
            <div className="p-4 cosmic-glass-subtle rounded-xl text-[11px] text-[#B8B2C8] font-sans">
              AI Provider: <strong className="text-[#F1EDF8]">Google Gemini API (gemini-2.5-flash)</strong> • Embeddings: <strong className="text-[#BBA8F1]">all-MiniLM-L6-v2 (384d)</strong>
            </div>
          </div>
        )}
      </CosmicGlassPanel>
    </div>
  );
};
