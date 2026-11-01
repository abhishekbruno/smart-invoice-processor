import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  fetchAutomationStatus,
  triggerFolderScan,
  triggerGmailSync,
  fetchSyncHistory,
} from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicLoader } from '../components/CosmicLoader';

export const Automation: React.FC = () => {
  const queryClient = useQueryClient();
  const [gmailQuery, setGmailQuery] = useState('');
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [syncResult, setSyncResult] = useState<any | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  const { data: status } = useQuery({
    queryKey: ['automation-status'],
    queryFn: fetchAutomationStatus,
    staleTime: 15000,
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['sync-history'],
    queryFn: () => fetchSyncHistory(10),
    staleTime: 15000,
  });

  const folderScanMutation = useMutation({
    mutationFn: triggerFolderScan,
    onSuccess: (data) => {
      setScanResult(data);
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      queryClient.invalidateQueries({ queryKey: ['automation-status'] });
    },
  });

  const gmailSyncMutation = useMutation({
    mutationFn: (q?: string) => triggerGmailSync(q),
    onSuccess: (data) => {
      setSyncResult(data);
      queryClient.invalidateQueries({ queryKey: ['sync-history'] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      queryClient.invalidateQueries({ queryKey: ['automation-status'] });
    },
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
          <span>Robotic Process Automation</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
          Ingestion Control Center
        </h1>
        <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
          Autonomous background ingestion via local folder watchdog and Gmail RPA attachment polling.
        </p>
      </div>

      {/* Primary 2 Ingestion Control Cards in Cosmic Violet Glass */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Local Folder Watcher */}
        <CosmicGlassPanel interactive className="p-6 sm:p-7 flex flex-col justify-between space-y-5 transition-all">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-mono text-[#BBA8F1] font-semibold">// 01</span>
                <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">Local Folder Monitor</h3>
              </div>
              <StatusBadge status={status?.folder_monitor_active ? 'online' : 'idle'} />
            </div>

            <p className="text-xs text-[#B8B2C8] leading-relaxed font-sans font-light">
              Monitors <code className="text-[#BBA8F1] cosmic-glass-control px-2 py-0.5 rounded-md font-mono text-[11px]">{status?.watch_directory || 'data/invoices/'}</code> for digital invoices.
            </p>

            {scanResult && (
              <div className="p-3.5 bg-emerald-950/20 border border-emerald-800/30 rounded-2xl text-xs text-emerald-300 font-mono">
                Scanned {scanResult.total_scanned} files • {scanResult.new_imported} imported • {scanResult.duplicates_skipped} duplicates skipped
              </div>
            )}
          </div>

          <button
            onClick={() => folderScanMutation.mutate()}
            disabled={folderScanMutation.isPending}
            className="aovix-gradient-btn w-full py-2.5 rounded-full font-sans font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
          >
            {folderScanMutation.isPending ? (
              <CosmicLoader size="sm" label="Scanning Directory..." />
            ) : (
              <span>Scan Watch Folder Now</span>
            )}
          </button>
        </CosmicGlassPanel>

        {/* Gmail RPA Poller */}
        <CosmicGlassPanel interactive className="p-6 sm:p-7 flex flex-col justify-between space-y-5 transition-all">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-mono text-[#BBA8F1] font-semibold">// 02</span>
                <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">Gmail Attachment Bot</h3>
              </div>
              <StatusBadge
                status={status?.gmail_authenticated ? 'online' : status?.gmail_configured ? 'active' : 'idle'}
              />
            </div>

            <p className="text-xs text-[#B8B2C8] leading-relaxed font-sans font-light">
              {status?.gmail_email ? `Connected to ${status.gmail_email}` : 'OAuth 2.0 read-only integration standby on backend'}
            </p>

            {syncResult && (
              <div className="p-3.5 bg-emerald-950/20 border border-emerald-800/30 rounded-2xl text-xs text-emerald-300 font-mono">
                Imported {syncResult.invoices_imported} invoices from {syncResult.attachments_found} attachments
              </div>
            )}
          </div>

          <button
            onClick={() => gmailSyncMutation.mutate(gmailQuery || undefined)}
            disabled={gmailSyncMutation.isPending}
            className="aovix-gradient-btn w-full py-2.5 rounded-full font-sans font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
          >
            {gmailSyncMutation.isPending ? (
              <CosmicLoader size="sm" label="Synchronizing Gmail..." />
            ) : (
              <span>Trigger Gmail Sync Now</span>
            )}
          </button>
        </CosmicGlassPanel>
      </div>

      {/* Expandable Configuration Drawer in Subtle Glass */}
      <CosmicGlassPanel variant="subtle" className="rounded-2xl overflow-hidden p-0">
        <button
          onClick={() => setShowConfig((prev) => !prev)}
          className="w-full px-6 py-4 flex items-center justify-between text-xs font-medium text-[#B8B2C8] hover:text-[#F1EDF8] transition cursor-pointer font-sans"
        >
          <span>{showConfig ? 'Hide Advanced Configuration' : 'Advanced Configuration & Gmail Query Filter'}</span>
          {showConfig ? <ChevronUp className="w-4 h-4 text-[#BBA8F1]" /> : <ChevronDown className="w-4 h-4 text-[#8879A7]" />}
        </button>

        {showConfig && (
          <div className="p-6 border-t border-white/6 space-y-4 text-xs animate-fade-in font-sans">
            <div>
              <label className="text-[#B8B2C8] block mb-1.5 font-medium">Custom Gmail Search Filter:</label>
              <input
                type="text"
                placeholder="has:attachment filename:pdf invoice..."
                value={gmailQuery}
                onChange={(e) => setGmailQuery(e.target.value)}
                className="w-full px-4 py-2.5 cosmic-glass-control rounded-xl text-xs text-[#F1EDF8] placeholder-[#9892AB] focus:outline-none focus:border-[#BBA8F1]/60 font-light"
              />
            </div>
            <div className="text-[11px] text-[#9892AB] font-mono">
              Last synced: {status?.gmail_last_synced_at || 'Never'} • Poller Interval: {status?.poller_interval_minutes || 15}m
            </div>
          </div>
        )}
      </CosmicGlassPanel>

      {/* Recent Activity List in Violet Glass */}
      <CosmicGlassPanel className="overflow-hidden p-0">
        <div className="px-6 py-4 border-b border-white/6 flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase font-mono tracking-wider text-[#9892AB]">Recent Sync Activity</h2>
          <span className="text-[11px] text-[#9892AB] font-mono">Last 10 executions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/[0.015] text-[#9892AB] uppercase font-mono text-[10px] border-b border-white/6">
              <tr>
                <th className="px-6 py-3.5 font-semibold">Timestamp</th>
                <th className="px-6 py-3.5 font-semibold">Status</th>
                <th className="px-6 py-3.5 font-semibold text-center">Messages</th>
                <th className="px-6 py-3.5 font-semibold text-center">Imported</th>
                <th className="px-6 py-3.5 font-semibold">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/4 text-[#B8B2C8]">
              {historyLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[#9892AB]">
                    Loading activity...
                  </td>
                </tr>
              ) : history && history.length > 0 ? (
                history.map((h) => (
                  <tr key={h.id} className="hover:bg-white/[0.02] transition">
                    <td className="px-6 py-4 text-[#B8B2C8] font-mono text-[11px]">{h.started_at}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={h.status} size="sm" />
                    </td>
                    <td className="px-6 py-4 text-center text-[#9892AB] font-mono">{h.messages_scanned}</td>
                    <td className="px-6 py-4 text-center font-semibold text-[#BBA8F1] font-mono">
                      +{h.invoices_imported}
                    </td>
                    <td className="px-6 py-4 text-[#9892AB] text-[11px] truncate max-w-xs font-mono">
                      {h.error_details || 'Success'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[#9892AB]">
                    No sync activity recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CosmicGlassPanel>
    </div>
  );
};
