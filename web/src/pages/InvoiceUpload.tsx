import React, { useState, useRef, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Cpu,
  Layers,
} from 'lucide-react';
import { uploadInvoiceFile } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Link } from 'react-router-dom';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { useNotifications } from '../components/NotificationProvider';

interface ProcessingStage {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
}

const STAGES: ProcessingStage[] = [
  { id: 'upload', label: 'Byte Stream Transfer', description: 'Transmitting binary payload to memory buffer', icon: UploadCloud },
  { id: 'read', label: 'Document Layout Extraction', description: 'PyMuPDF text layer and typography scan', icon: Layers },
  { id: 'ai', label: 'Gemini 2.5 Field Synthesis', description: 'Extracting vendors, dates, and line items', icon: Cpu },
  { id: 'math', label: 'Arithmetic & Duplicate Shield', description: 'Validating subtotal math & SHA-256 hash match', icon: ShieldCheck },
  { id: 'index', label: 'Vector Index Synchronization', description: 'Embedding line items in ChromaDB knowledge space', icon: Sparkles },
];

export const InvoiceUpload: React.FC = () => {
  const queryClient = useQueryClient();
  const notify = useNotifications();
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Progressive simulated pipeline milestones while the backend processes
  useEffect(() => {
    if (!isUploading) return;
    setCurrentStageIndex(0);

    const timeouts = [
      setTimeout(() => setCurrentStageIndex(1), 600),
      setTimeout(() => setCurrentStageIndex(2), 1600),
      setTimeout(() => setCurrentStageIndex(3), 2800),
      setTimeout(() => setCurrentStageIndex(4), 3800),
    ];

    return () => timeouts.forEach(clearTimeout);
  }, [isUploading]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateAndSelectFile = (file: File) => {
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    const isSpreadsheet = /\.(xlsx|xls|csv)$/i.test(file.name);

    if (isPdf) {
      setSelectedFile(file);
      setUploadError(null);
      setUploadResult(null);
    } else if (isSpreadsheet) {
      setSelectedFile(null);
      const msg = `Spreadsheet detected (${file.name}). Please save or print your spreadsheet to PDF before uploading, as PyMuPDF OCR and line-item extraction operate on PDF document layouts.`;
      setUploadError(msg);
      notify.info(msg, 'Spreadsheet Format Notice');
    } else {
      setSelectedFile(null);
      const msg = `Unsupported format (${file.name}). Please upload invoices in standard PDF (.pdf) format for automated extraction and duplicate verification.`;
      setUploadError(msg);
      notify.warning(msg, 'Unsupported File Format');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    setUploadResult(null);

    try {
      const res = await uploadInvoiceFile(selectedFile);
      setUploadResult(res);
      setCurrentStageIndex(5); // 100% completed

      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-page'] });
      queryClient.invalidateQueries({ queryKey: ['recent-processing-logs'] });

      notify.success(
        `Invoice #${res.invoice_number || res.invoice_id} successfully processed and indexed!`,
        'Invoice Extracted'
      );
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || err.message || 'Failed to extract invoice.';
      setUploadError(errMsg);
      notify.error(errMsg, 'Processing Failed');
    } finally {
      setIsUploading(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setUploadError(null);
    setShowTechnicalDetails(false);
    setCurrentStageIndex(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const progressPercent = isUploading
    ? Math.min(92, Math.round(((currentStageIndex + 1) / (STAGES.length + 0.5)) * 100))
    : uploadResult
    ? 100
    : 0;

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
          <Sparkles size={12} className="text-[#BBA8F1]" />
          <span>Ingestion Hub</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-semibold tracking-tight text-[#F1EDF8]">
          Upload Invoice
        </h1>
        <p className="text-xs sm:text-sm text-[#B8B2C8] mt-1 font-sans font-light">
          Drop any supplier invoice PDF for automated parsing, duplicate verification, and vector indexing.
        </p>
      </div>

      {/* Upload Zone Card in Cosmic Violet Glass */}
      {!isUploading && !uploadResult && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`cosmic-glass upload-drop-zone border-2 border-dashed rounded-3xl p-6 sm:p-12 text-center transition-all flex flex-col items-center justify-center ${
            isDragging
              ? 'border-[#BBA8F1] bg-[#4B37B2]/20 shadow-[0_0_35px_rgba(107,66,205,0.3)]'
              : selectedFile
              ? 'border-[#BBA8F1]/40 bg-white/[0.03]'
              : 'border-[rgba(184,160,248,0.22)] hover:border-[#BBA8F1]/45'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="application/pdf"
            className="hidden"
          />

          <div className="w-14 h-14 rounded-2xl cosmic-glass-control flex items-center justify-center text-[#B8B2C8] mb-4 shadow-[0_0_20px_rgba(75,55,178,0.2)]">
            {selectedFile ? (
              <FileText className="w-6 h-6 text-[#BBA8F1]" />
            ) : (
              <UploadCloud className="w-6 h-6 text-[#8879A7]" />
            )}
          </div>

          {selectedFile ? (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-sans font-semibold text-[#F1EDF8]">{selectedFile.name}</p>
                <p className="text-xs text-[#9892AB] font-mono mt-0.5">
                  {(selectedFile.size / 1024).toFixed(1)} KB • PDF Document
                </p>
              </div>

              <div className="flex items-center justify-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleUpload}
                  className="aovix-gradient-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wide flex items-center gap-2 cursor-pointer shadow-[0_4px_15px_rgba(75,55,178,0.3)] hover:shadow-[0_6px_20px_rgba(124,58,237,0.4)]"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Process Invoice</span>
                </button>
                <button
                  type="button"
                  onClick={resetUpload}
                  className="px-5 py-2.5 rounded-full cosmic-glass-control text-[#B8B2C8] hover:text-[#F1EDF8] text-xs font-medium transition cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm font-sans font-medium text-[#F1EDF8]">
                Drag invoice PDF here, or{' '}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-[#BBA8F1] hover:text-white font-semibold underline underline-offset-4 decoration-[#BBA8F1]/50 transition cursor-pointer"
                >
                  browse files
                </button>
              </p>
              <p className="text-[11px] text-[#9892AB] font-sans">
                Accepts digital PDFs and receipts up to 25 MB
              </p>
            </div>
          )}
        </div>
      )}

      {/* Multi-Stage Animated Processing Workflow Panel */}
      {isUploading && (
        <CosmicGlassPanel className="p-6 sm:p-8 space-y-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border-[#BBA8F1]/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Minimal cosmic orbital loader */}
              <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
                <div
                  className="absolute inset-0 rounded-full border border-[#BBA8F1]/50 border-t-transparent animate-spin"
                  style={{ animationDuration: '2.4s' }}
                />
                <div
                  className="absolute inset-1.5 rounded-full border border-[#8B5CF6]/60 border-b-transparent animate-spin"
                  style={{ animationDuration: '1.6s', animationDirection: 'reverse' }}
                />
                <div className="w-2.5 h-2.5 rounded-full bg-[#BBA8F1] shadow-[0_0_10px_#BBA8F1] animate-pulse" />
              </div>

              <div>
                <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">
                  Processing Document
                </h3>
                <p className="text-xs text-[#9892AB] font-mono mt-0.5 truncate max-w-xs sm:max-w-md">
                  {selectedFile?.name}
                </p>
              </div>
            </div>

            <span className="text-xs font-mono font-medium text-[#BBA8F1] tabular-nums">
              {progressPercent}%
            </span>
          </div>

          {/* Lavender Progress Track with Glowing Bead */}
          <div className="w-full bg-white/[0.04] h-2 rounded-full overflow-hidden relative border border-white/6">
            <div
              className="h-full bg-gradient-to-r from-[#6366F1] via-[#8B5CF6] to-[#BBA8F1] transition-all duration-400 relative"
              style={{ width: `${progressPercent}%` }}
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_10px_#BBA8F1]" />
            </div>
          </div>

          {/* Milestone Steps */}
          <div className="space-y-2.5 pt-2">
            {STAGES.map((stage, idx) => {
              const StageIcon = stage.icon;
              const isPast = currentStageIndex > idx;
              const isCurrent = currentStageIndex === idx;

              return (
                <div
                  key={stage.id}
                  className={`flex items-center justify-between p-3 rounded-xl transition-all ${
                    isCurrent
                      ? 'bg-[#BBA8F1]/10 border border-[#BBA8F1]/30 shadow-[0_2px_12px_rgba(139,92,246,0.15)]'
                      : isPast
                      ? 'bg-white/[0.02] border border-white/4'
                      : 'opacity-40 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs ${
                        isPast
                          ? 'bg-[#22c55e]/15 text-[#86efac] border border-[#22c55e]/30'
                          : isCurrent
                          ? 'bg-[#8B5CF6]/20 text-[#D8CDF0] border border-[#BBA8F1]/40'
                          : 'bg-white/5 text-[#8879A7]'
                      }`}
                    >
                      {isPast ? <CheckCircle2 size={14} /> : <StageIcon size={14} />}
                    </div>
                    <div>
                      <span
                        className={`text-xs font-medium block ${
                          isCurrent ? 'text-[#F1EDF8]' : isPast ? 'text-[#D8CDF0]' : 'text-[#8879A7]'
                        }`}
                      >
                        {stage.label}
                      </span>
                      <span className="text-[10px] text-[#9892AB] font-sans block">
                        {stage.description}
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono uppercase tracking-wider text-[#9892AB]">
                    {isPast ? 'DONE' : isCurrent ? 'RUNNING' : 'QUEUED'}
                  </span>
                </div>
              );
            })}
          </div>
        </CosmicGlassPanel>
      )}

      {/* Error Message with Actionable Retry */}
      {uploadError && (
        <CosmicGlassPanel className="p-5 rounded-2xl border-rose-500/30 bg-rose-950/20 text-rose-200 space-y-3">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
            <div className="flex-1">
              <span className="font-semibold text-sm text-rose-100 block">Processing Failed</span>
              <p className="text-xs text-rose-300/90 mt-1 leading-relaxed">{uploadError}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2 border-t border-rose-500/20">
            <button
              type="button"
              onClick={handleUpload}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-medium border border-rose-500/30 transition cursor-pointer"
            >
              <RotateCcw size={13} />
              <span>Retry Processing</span>
            </button>
            <button
              type="button"
              onClick={resetUpload}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-[#B8B2C8] transition cursor-pointer"
            >
              Choose different file
            </button>
          </div>
        </CosmicGlassPanel>
      )}

      {/* Extracted Preview Card in Cosmic Violet Glass */}
      {uploadResult && (
        <CosmicGlassPanel interactive className="p-6 sm:p-8 space-y-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)] animate-fade-in border-[#BBA8F1]/30">
          <div className="flex items-center justify-between pb-4 border-b border-white/6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[0_0_12px_rgba(34,197,94,0.2)]">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-display font-semibold text-[#F1EDF8]">
                  Invoice Extracted Successfully
                </h3>
                <p className="text-[11px] text-[#9892AB] font-mono">
                  ID #{uploadResult.invoice_id} • File: {uploadResult.file_name}
                </p>
              </div>
            </div>
            <StatusBadge status={uploadResult.status} />
          </div>

          {/* Core Extracted Overview */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="cosmic-glass-subtle p-4 rounded-2xl">
              <span className="text-[10px] uppercase font-mono text-[#9892AB] block tracking-wider">Vendor</span>
              <span className="font-sans font-semibold text-[#F1EDF8] mt-1 block truncate">
                {uploadResult.vendor || 'Unknown'}
              </span>
            </div>
            <div className="cosmic-glass-subtle p-4 rounded-2xl">
              <span className="text-[10px] uppercase font-mono text-[#9892AB] block tracking-wider">Invoice Number</span>
              <span className="font-mono text-[#B8B2C8] mt-1 block truncate">
                {uploadResult.invoice_number || 'N/A'}
              </span>
            </div>
            <div className="cosmic-glass-subtle p-4 rounded-2xl">
              <span className="text-[10px] uppercase font-mono text-[#9892AB] block tracking-wider">Total Amount</span>
              <span className="font-mono font-bold text-[#F1EDF8] mt-1 block tabular-nums">
                {uploadResult.currency ? `${uploadResult.currency} ` : ''}
                {uploadResult.total_amount != null ? uploadResult.total_amount.toFixed(2) : '—'}
              </span>
            </div>
            <div className="cosmic-glass-subtle p-4 rounded-2xl">
              <span className="text-[10px] uppercase font-mono text-[#9892AB] block tracking-wider">Deduplication</span>
              <span className={`font-semibold mt-1 block ${uploadResult.is_duplicate ? 'text-rose-400' : 'text-emerald-400'}`}>
                {uploadResult.is_duplicate ? 'Duplicate Flagged' : 'Unique Record'}
              </span>
            </div>
          </div>

          {/* Expandable Technical Details */}
          <div className="border-t border-white/6 pt-3">
            <button
              type="button"
              onClick={() => setShowTechnicalDetails((prev) => !prev)}
              className="text-xs text-[#B8B2C8] hover:text-[#F1EDF8] flex items-center gap-1.5 font-medium transition cursor-pointer"
            >
              <span>{showTechnicalDetails ? 'Hide Parsing Details' : 'Show Parsing Details & Diagnostics'}</span>
              {showTechnicalDetails ? (
                <ChevronUp className="w-3.5 h-3.5 text-[#BBA8F1]" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5 text-[#8879A7]" />
              )}
            </button>

            {showTechnicalDetails && (
              <div className="mt-3 p-4 cosmic-glass-control rounded-2xl text-[11px] text-[#B8B2C8] space-y-1.5 animate-fade-in font-mono">
                <p>Status: <strong className="text-[#F1EDF8]">{uploadResult.status}</strong></p>
                <p>Indexing: <strong className="text-[#BBA8F1]">ChromaDB Embeddings Synchronized</strong></p>
                <p>Calculation: <strong className="text-[#F1EDF8]">Deterministic Decimal Arithmetic Safe</strong></p>
                {uploadResult.duplicate_reason && (
                  <p className="text-amber-300">Duplicate Reason: {uploadResult.duplicate_reason}</p>
                )}
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/6">
            <button
              type="button"
              onClick={resetUpload}
              className="text-xs text-[#B8B2C8] hover:text-[#F1EDF8] transition cursor-pointer"
            >
              Upload another invoice
            </button>
            <div className="flex items-center gap-2">
              <Link
                to={`/chat`}
                className="px-4 py-2 rounded-full cosmic-glass-control text-xs text-[#D8CDF0] hover:text-white transition flex items-center gap-1.5"
              >
                <Sparkles size={12} className="text-[#A78BFA]" />
                <span>Ask AI about this</span>
              </Link>
              <Link
                to={`/invoices?invoice=${uploadResult.invoice_id}`}
                className="aovix-gradient-btn inline-flex items-center gap-1.5 px-5 py-2 rounded-full text-xs font-semibold"
              >
                <span>View in Invoices</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </CosmicGlassPanel>
      )}
    </div>
  );
};
