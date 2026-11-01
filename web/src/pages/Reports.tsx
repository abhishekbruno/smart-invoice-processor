import React, { useState } from 'react';
import {
  Download,
  Check,
} from 'lucide-react';
import { downloadReportFile } from '../services/api';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicLoader } from '../components/CosmicLoader';
import { useNotifications } from '../components/NotificationProvider';

export const Reports: React.FC = () => {
  const notify = useNotifications();
  const [reportType, setReportType] = useState<'invoices' | 'monthly' | 'vendors'>('invoices');
  const [exportFormat, setExportFormat] = useState<'csv' | 'xlsx' | 'pdf'>('csv');
  const [targetCurrency, setTargetCurrency] = useState('INR');
  const [includeDuplicates, setIncludeDuplicates] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadSuccess(false);

    try {
      const blob = await downloadReportFile(reportType, exportFormat, {
        target_currency: targetCurrency,
        include_duplicates: includeDuplicates,
      });

      const ext = exportFormat === 'xlsx' ? 'xlsx' : exportFormat === 'pdf' ? 'pdf' : 'csv';
      const filename = `${reportType}_report_${Date.now()}.${ext}`;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      notify.success(`${filename} exported successfully.`, 'Report Generated');
      setTimeout(() => setDownloadSuccess(false), 2500);
    } catch (err: any) {
      console.error('Download failed', err);
      notify.error(err?.message || 'Report export failed. Please verify API server status.', 'Export Failed');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
          <span>Audit & Ledger Reports</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
          Financial Reports
        </h1>
        <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
          Export audit-ready financial statements in CSV, Excel (.xlsx), and PDF formats.
        </p>
      </div>

      {/* Main Generation Card in Cosmic Violet Glass */}
      <CosmicGlassPanel interactive className="p-7 sm:p-8 space-y-6">
        {/* Step 1: Report Type Cards */}
        <div>
          <label className="text-xs font-semibold uppercase font-mono tracking-wider text-[#9892AB] block mb-3.5">
            1. Select Report Type
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
            {[
              {
                id: 'invoices',
                num: '// 01',
                title: 'Invoice Register',
                desc: 'Itemized register with dates, status, and valuations',
              },
              {
                id: 'monthly',
                num: '// 02',
                title: 'Monthly Summary',
                desc: 'Consolidated month-by-month spending aggregations',
              },
              {
                id: 'vendors',
                num: '// 03',
                title: 'Supplier Breakdown',
                desc: 'Supplier rankings, volume, and excluded duplicates',
              },
            ].map((r) => {
              const isSelected = reportType === r.id;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setReportType(r.id as any)}
                  className={`p-5 rounded-2xl text-left transition-all flex flex-col justify-between cursor-pointer ${
                    isSelected
                      ? 'bg-[#4B37B2]/30 border border-[#BBA8F1]/45 text-[#F1EDF8] shadow-[0_0_20px_rgba(75,55,178,0.25)]'
                      : 'cosmic-glass-subtle text-[#B8B2C8] hover:border-white/15 hover:text-[#F1EDF8]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3.5">
                    <span className="text-[10px] font-mono text-[#BBA8F1] font-semibold">{r.num}</span>
                    {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-[#BBA8F1] shadow-[0_0_6px_rgba(187,168,241,0.7)]" />}
                  </div>
                  <div>
                    <h4 className="font-sans font-semibold text-xs text-[#F1EDF8]">{r.title}</h4>
                    <p className="text-[11px] text-[#9892AB] mt-1 leading-relaxed font-sans font-light">{r.desc}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Format & Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-4 border-t border-white/6">
          <div>
            <label className="text-xs font-semibold uppercase font-mono tracking-wider text-[#9892AB] block mb-2.5">
              2. Export Format
            </label>
            <div className="grid grid-cols-3 gap-2.5">
              {[
                { id: 'csv', label: 'CSV' },
                { id: 'xlsx', label: 'Excel' },
                { id: 'pdf', label: 'PDF' },
              ].map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setExportFormat(f.id as any)}
                  className={`py-2 px-3 rounded-xl border text-xs font-sans font-semibold transition cursor-pointer ${
                    exportFormat === f.id
                      ? 'aovix-gradient-btn'
                      : 'cosmic-glass-control text-[#B8B2C8] hover:text-[#F1EDF8]'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase font-mono tracking-wider text-[#9892AB] block mb-2.5">
              3. Target Currency & Filter
            </label>
            <div className="flex items-center gap-3">
              <select
                value={targetCurrency}
                onChange={(e) => setTargetCurrency(e.target.value)}
                className="px-3.5 py-2 cosmic-glass-control rounded-xl text-xs text-[#F1EDF8] focus:outline-none focus:border-[#BBA8F1]/60 transition flex-1 cursor-pointer font-sans"
              >
                <option value="INR" className="bg-[#0B081E]">Indian Rupee (INR ₹)</option>
                <option value="USD" className="bg-[#0B081E]">US Dollar (USD $)</option>
                <option value="EUR" className="bg-[#0B081E]">Euro (EUR €)</option>
                <option value="GBP" className="bg-[#0B081E]">British Pound (GBP £)</option>
              </select>

              <label className="flex items-center gap-2 text-xs text-[#B8B2C8] select-none cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeDuplicates}
                  onChange={(e) => setIncludeDuplicates(e.target.checked)}
                  className="rounded bg-[#0E0C16] border-white/10 text-[#4B37B2] focus:ring-0 cursor-pointer"
                />
                <span className="text-[11px] font-mono">Duplicates</span>
              </label>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-4 border-t border-white/6 flex items-center justify-between">
          <span className="text-[11px] text-[#9892AB] font-mono">
            Deterministic arithmetic safe from SQLite records
          </span>

          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="aovix-gradient-btn px-6 py-2.5 rounded-full text-xs font-sans font-semibold tracking-wide transition flex items-center gap-2 disabled:opacity-50 cursor-pointer shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
          >
            {isDownloading ? (
              <CosmicLoader size="sm" label="Exporting..." />
            ) : downloadSuccess ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-300" />
                <span>Downloaded</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Download Report</span>
              </>
            )}
          </button>
        </div>
      </CosmicGlassPanel>
    </div>
  );
};
