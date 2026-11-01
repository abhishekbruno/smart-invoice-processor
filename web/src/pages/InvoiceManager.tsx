import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Search,
  CheckCircle2,
  Trash2,
  AlertTriangle,
  FileText,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import {
  fetchInvoices,
  fetchInvoiceDetail,
  verifyInvoice,
  markInvoiceGenuine,
  confirmInvoiceDuplicate,
  deleteInvoice,
  getInvoiceDocumentUrl,
} from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicLoader, CosmicTableSkeleton } from '../components/CosmicLoader';
import { useNotifications } from '../components/NotificationProvider';

export const InvoiceManager: React.FC = () => {
  const notify = useNotifications();
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const statusParam = searchParams.get('status') ?? '';
  const statusFilter = ['processed', 'needs_review', 'verified', 'suspected_duplicate'].includes(statusParam) ? statusParam : '';
  const setStatusFilter = (value: string) => setSearchParams(previous => { const next = new URLSearchParams(previous); if (value) next.set('status', value); else next.delete('status'); return next; });
  const [currencyFilter, setCurrencyFilter] = useState('');
  const [includeDuplicates, setIncludeDuplicates] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const idParam = Number(searchParams.get('invoice'));
  const selectedInvoiceId = Number.isSafeInteger(idParam) && idParam > 0 ? idParam : null;
  const setSelectedInvoiceId = (value: number | null) => setSearchParams(previous => { const next = new URLSearchParams(previous); if (value !== null) next.set('invoice', String(value)); else next.delete('invoice'); return next; });
  const [activeTab, setActiveTab] = useState<'overview' | 'items' | 'technical'>('overview');

  // Queries
  const { data: invoicesData, isLoading } = useQuery({
    queryKey: ['invoices', currentPage, searchTerm, statusFilter, currencyFilter, includeDuplicates],
    queryFn: () =>
      fetchInvoices({
        page: currentPage,
        limit: 10,
        vendor: searchTerm || undefined,
        status: statusFilter || undefined,
        currency: currencyFilter || undefined,
        include_duplicates: includeDuplicates,
      }),
    staleTime: 10000,
  });

  const { data: detailData, isLoading: detailLoading } = useQuery({
    queryKey: ['invoice-detail', selectedInvoiceId],
    queryFn: () => (selectedInvoiceId ? fetchInvoiceDetail(selectedInvoiceId) : null),
    enabled: !!selectedInvoiceId,
  });

  // Mutations
  const verifyMutation = useMutation({
    mutationFn: verifyInvoice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['invoice-detail'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      notify.success('Invoice verified and approved for ledger.', 'Invoice Verified');
    },
    onError: (err: any) => {
      notify.error(err?.response?.data?.detail || err?.message || 'Verification failed', 'Action Failed');
    },
  });

  const genuineMutation = useMutation({
    mutationFn: markInvoiceGenuine,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['invoice-detail'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      notify.success('Invoice marked as genuine and cleared.', 'Status Updated');
    },
    onError: (err: any) => {
      notify.error(err?.response?.data?.detail || err?.message || 'Action failed', 'Action Failed');
    },
  });

  const duplicateMutation = useMutation({
    mutationFn: confirmInvoiceDuplicate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['invoice-detail'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      notify.warning('Invoice confirmed as duplicate and payment blocked.', 'Duplicate Flagged');
    },
    onError: (err: any) => {
      notify.error(err?.response?.data?.detail || err?.message || 'Action failed', 'Action Failed');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteInvoice,
    onSuccess: () => {
      setSelectedInvoiceId(null);
      setConfirmDeleteId(null);
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      notify.success('Invoice record permanently deleted.', 'Invoice Deleted');
    },
    onError: (err: any) => {
      notify.error(err?.response?.data?.detail || err?.message || 'Delete failed', 'Action Failed');
    },
  });

  const items = invoicesData?.items || [];
  const totalPages = invoicesData?.total_pages || 1;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
            <span>Repository Ledger</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
            Invoice Repository
          </h1>
          <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
            Search, inspect, and verify invoices across your enterprise repository.
          </p>
        </div>
      </div>

      {/* Minimal Filter and Search Bar in Cosmic Violet Glass */}
      <CosmicGlassPanel className="p-4 sm:flex sm:items-center sm:gap-3 space-y-3 sm:space-y-0 shadow-[0_10px_30px_rgba(0,0,0,0.4)]">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-[#9892AB] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search supplier or vendor..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 cosmic-glass-control rounded-xl text-xs text-[#F1EDF8] placeholder-[#9892AB] focus:outline-none focus:border-[#BBA8F1]/60 transition font-sans font-light"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 cosmic-glass-control rounded-xl text-xs text-[#B8B2C8] focus:outline-none focus:border-[#BBA8F1]/60 cursor-pointer font-sans"
          >
            <option value="" className="bg-[#0B081E]">All Statuses</option>
            <option value="processed" className="bg-[#0B081E]">Processed</option>
            <option value="verified" className="bg-[#0B081E]">Verified</option>
            <option value="needs_review" className="bg-[#0B081E]">Needs Review</option>
            <option value="suspected_duplicate" className="bg-[#0B081E]">Duplicates</option>
          </select>

          <select
            value={currencyFilter}
            onChange={(e) => {
              setCurrencyFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 cosmic-glass-control rounded-xl text-xs text-[#B8B2C8] focus:outline-none focus:border-[#BBA8F1]/60 cursor-pointer font-sans"
          >
            <option value="" className="bg-[#0B081E]">All Currencies</option>
            <option value="USD" className="bg-[#0B081E]">USD ($)</option>
            <option value="EUR" className="bg-[#0B081E]">EUR (€)</option>
            <option value="GBP" className="bg-[#0B081E]">GBP (£)</option>
            <option value="INR" className="bg-[#0B081E]">INR (₹)</option>
          </select>

          <label className="flex items-center gap-2 text-xs text-[#B8B2C8] select-none cursor-pointer pl-1">
            <input
              type="checkbox"
              checked={includeDuplicates}
              onChange={(e) => setIncludeDuplicates(e.target.checked)}
              className="rounded bg-[#0E0C16] border-white/10 text-[#4B37B2] focus:ring-0 cursor-pointer"
            />
            <span className="text-[11px] font-mono">Show Duplicates</span>
          </label>
        </div>
      </CosmicGlassPanel>

      {/* Clean Modern List in Cosmic Violet Glass */}
      <CosmicGlassPanel className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/[0.015] text-[#9892AB] uppercase tracking-wider text-[10px] border-b border-white/6 font-mono">
              <tr>
                <th className="px-6 py-3.5 font-semibold">Vendor</th>
                <th className="px-6 py-3.5 font-semibold">Invoice #</th>
                <th className="px-6 py-3.5 font-semibold">Date</th>
                <th className="px-6 py-3.5 font-semibold">Original Total</th>
                <th className="px-6 py-3.5 font-semibold">Converted (INR)</th>
                <th className="px-6 py-3.5 font-semibold">Status</th>
                <th className="px-6 py-3.5 font-semibold text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/4 text-[#B8B2C8]">
              {isLoading ? (
                <CosmicTableSkeleton rows={5} cols={7} />
              ) : items.length > 0 ? (
                items.map((inv) => (
                  <tr
                    key={inv.id}
                    onClick={() => {
                      setSelectedInvoiceId(inv.id);
                      setActiveTab('overview');
                    }}
                    className="hover:bg-white/[0.02] cursor-pointer transition"
                  >
                    <td className="px-6 py-4 font-sans font-medium text-[#F1EDF8]">
                      {inv.vendor_name || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 font-mono text-[#B8B2C8]">
                      {inv.invoice_number || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-[#9892AB]">
                      {inv.invoice_date || 'N/A'}
                    </td>
                    <td className="px-6 py-4 font-mono text-[#F1EDF8]">
                      {inv.currency} {inv.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-6 py-4 font-semibold text-[#BBA8F1] tabular-nums font-mono">
                      {inv.converted_amount != null
                        ? `₹${inv.converted_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
                        : '—'}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={inv.status} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedInvoiceId(inv.id);
                          setActiveTab('overview');
                        }}
                        className="px-3 py-1 rounded-full cosmic-glass-control text-[11px] font-medium text-[#BBA8F1] hover:text-white transition cursor-pointer"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-[#9892AB]">
                    No matching invoices found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Minimal Pagination */}
        <div className="px-6 py-4 border-t border-white/6 flex items-center justify-between text-[11px] text-[#9892AB] font-mono">
          <span>
            Page <strong className="text-[#F1EDF8]">{currentPage}</strong> of{' '}
            <strong className="text-[#F1EDF8]">{totalPages}</strong> ({invoicesData?.total || 0} total)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-lg cosmic-glass-control disabled:opacity-30 text-[#B8B2C8] hover:text-white transition cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-lg cosmic-glass-control disabled:opacity-30 text-[#B8B2C8] hover:text-white transition cursor-pointer"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </CosmicGlassPanel>

      {/* Structured Invoice Detail Modal */}
      <Modal
        isOpen={!!selectedInvoiceId}
        onClose={() => setSelectedInvoiceId(null)}
        title={detailData ? `${detailData.vendor_name || 'Invoice'} (#${detailData.invoice_number || detailData.id})` : 'Invoice Details'}
        subtitle={detailData ? `Registered ${detailData.created_at}` : undefined}
        maxWidth="3xl"
      >
        {detailLoading ? (
          <div className="py-12 flex justify-center">
            <CosmicLoader size="md" label="Fetching invoice details…" />
          </div>
        ) : detailData ? (
          <div className="space-y-6">
            {/* Duplicate Notice */}
            {detailData.is_duplicate && (
              <div className="p-4 rounded-2xl bg-[#923F53]/15 border border-[#923F53]/40 text-rose-300 text-xs flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <span className="font-semibold block">Suspected Duplicate Flagged</span>
                  <p className="text-[#B8B2C8]">{detailData.duplicate_reason || 'Matches identical vendor and invoice parameters.'}</p>
                </div>
              </div>
            )}

            {/* Modal Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-white/6 pb-3 text-xs">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-3.5 py-1.5 rounded-xl font-medium transition cursor-pointer font-sans ${
                  activeTab === 'overview'
                    ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
                    : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
                }`}
              >
                Overview & Financials
              </button>
              <button
                onClick={() => setActiveTab('items')}
                className={`px-3.5 py-1.5 rounded-xl font-medium transition cursor-pointer font-sans ${
                  activeTab === 'items'
                    ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
                    : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
                }`}
              >
                Line Items ({detailData.line_items.length})
              </button>
              <button
                onClick={() => setActiveTab('technical')}
                className={`px-3.5 py-1.5 rounded-xl font-medium transition cursor-pointer font-sans ${
                  activeTab === 'technical'
                    ? 'bg-[#4B37B2]/30 text-[#BBA8F1] border border-[#BBA8F1]/40 shadow-[0_0_12px_rgba(75,55,178,0.25)]'
                    : 'text-[#B8B2C8] hover:text-[#F1EDF8]'
                }`}
              >
                Metadata & Hash
              </button>
            </div>

            {/* Tab 1: Overview & Financials */}
            {activeTab === 'overview' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Vendor</span>
                    <span className="font-sans font-semibold text-[#F1EDF8] mt-1 block truncate">{detailData.vendor_name || 'N/A'}</span>
                  </div>
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Issue Date</span>
                    <span className="font-sans font-semibold text-[#F1EDF8] mt-1 block">{detailData.invoice_date || 'N/A'}</span>
                  </div>
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Original Total</span>
                    <span className="font-semibold text-[#F1EDF8] mt-1 block font-mono">
                      {detailData.currency} {detailData.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Converted (INR)</span>
                    <span className="font-bold text-[#BBA8F1] mt-1 block font-mono">
                      ₹{detailData.converted_amount?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Customer / Billed To</span>
                    <span className="font-medium text-[#B8B2C8] mt-1 block">{detailData.customer_name || 'N/A'}</span>
                  </div>
                  <div className="p-3.5 cosmic-glass-subtle rounded-xl">
                    <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Due Date</span>
                    <span className="font-medium text-[#B8B2C8] mt-1 block">{detailData.due_date || 'N/A'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Tab 2: Line Items */}
            {activeTab === 'items' && (
              <div className="cosmic-glass-subtle rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-white/2 text-[#9892AB] uppercase font-mono text-[10px] border-b border-white/6">
                    <tr>
                      <th className="px-5 py-3">Item Description</th>
                      <th className="px-5 py-3 text-center">Qty</th>
                      <th className="px-5 py-3 text-right">Unit Price</th>
                      <th className="px-5 py-3 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/4 text-[#B8B2C8]">
                    {detailData.line_items.length > 0 ? (
                      detailData.line_items.map((item, idx) => (
                        <tr key={idx}>
                          <td className="px-5 py-3 font-sans font-medium text-[#F1EDF8]">{item.description}</td>
                          <td className="px-5 py-3 text-center text-[#9892AB] font-mono">{item.quantity ?? 1}</td>
                          <td className="px-5 py-3 text-right font-mono text-[#9892AB]">
                            {detailData.currency} {item.unit_price?.toFixed(2)}
                          </td>
                          <td className="px-5 py-3 text-right font-mono font-medium text-[#F1EDF8]">
                            {detailData.currency} {item.amount?.toFixed(2)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-5 py-6 text-center text-[#9892AB]">
                          No line items itemized.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 3: Technical & Metadata */}
            {activeTab === 'technical' && (
              <div className="space-y-3 text-xs">
                <div className="p-4 cosmic-glass-subtle rounded-xl">
                  <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">SHA-256 Digest</span>
                  <span className="font-mono text-[#B8B2C8] text-[11px] block break-all mt-1">{detailData.file_hash}</span>
                </div>
                <div className="p-4 cosmic-glass-subtle rounded-xl">
                  <span className="text-[#9892AB] text-[10px] uppercase font-mono block tracking-wider">Source File Location</span>
                  <span className="font-mono text-[#9892AB] text-[11px] block truncate mt-1">{detailData.source_file_path || 'Local archive'}</span>
                </div>
              </div>
            )}

            {/* Modal Bottom Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-white/6">
              <div className="flex items-center gap-2">
                <a
                  href={getInvoiceDocumentUrl(detailData.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl cosmic-glass-control text-[#F1EDF8] text-xs font-medium hover:text-white transition"
                >
                  <FileText className="w-3.5 h-3.5 text-[#BBA8F1]" />
                  <span>Original PDF</span>
                  <ExternalLink className="w-3 h-3 text-[#9892AB]" />
                </a>

                {confirmDeleteId === detailData.id ? (
                  <div className="inline-flex items-center gap-1.5 p-1 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs">
                    <span className="text-rose-200 px-1 text-[11px]">Confirm delete?</span>
                    <button
                      type="button"
                      onClick={() => deleteMutation.mutate(detailData.id)}
                      disabled={deleteMutation.isPending}
                      className="px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium text-[11px] transition cursor-pointer"
                    >
                      {deleteMutation.isPending ? 'Deleting...' : 'Yes, delete'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmDeleteId(null)}
                      className="px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-[#C4B5FD] text-[11px] transition cursor-pointer"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirmDeleteId(detailData.id)}
                    disabled={deleteMutation.isPending}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#923F53]/15 hover:bg-[#923F53]/25 text-rose-300 text-xs font-medium border border-[#923F53]/30 transition cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Delete</span>
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2">
                {detailData.is_duplicate ? (
                  <>
                    <button
                      onClick={() => genuineMutation.mutate(detailData.id)}
                      disabled={genuineMutation.isPending}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-700/80 hover:bg-emerald-600 text-white text-xs font-semibold shadow-sm transition cursor-pointer font-sans"
                    >
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Mark Genuine</span>
                    </button>
                    <button
                      onClick={() => duplicateMutation.mutate(detailData.id)}
                      disabled={duplicateMutation.isPending}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-700/80 hover:bg-amber-600 text-white text-xs font-semibold shadow-sm transition cursor-pointer font-sans"
                    >
                      <ShieldAlert className="w-3.5 h-3.5" />
                      <span>Confirm Duplicate</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => verifyMutation.mutate(detailData.id)}
                    disabled={verifyMutation.isPending || detailData.status === 'verified'}
                    className="aovix-gradient-btn inline-flex items-center gap-1.5 px-5 py-2 rounded-full text-xs font-semibold shadow-sm transition disabled:opacity-40 cursor-pointer"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{detailData.status === 'verified' ? 'Verified' : 'Verify Invoice'}</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};
