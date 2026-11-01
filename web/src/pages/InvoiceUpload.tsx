import React, { useState, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';
import { uploadInvoiceFile } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { Link } from 'react-router-dom';
import { CosmicGlassPanel } from '../components/CosmicGlassPanel';
import { CosmicLoader } from '../components/CosmicLoader';

export const InvoiceUpload: React.FC = () => {
  const queryClient = useQueryClient();
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        setSelectedFile(file);
        setUploadError(null);
        setUploadResult(null);
      } else {
        setUploadError('Only PDF documents (.pdf) are supported.');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setUploadError(null);
      setUploadResult(null);
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
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-full'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-page'] });
    } catch (err: any) {
      setUploadError(
        err.response?.data?.detail || err.message || 'Failed to extract invoice.'
      );
    } finally {
      setIsUploading(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setUploadError(null);
    setShowTechnicalDetails(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-0.5 rounded-full cosmic-glass-pill mb-2">
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
                onClick={handleUpload}
                disabled={isUploading}
                className="aovix-gradient-btn px-6 py-2.5 rounded-full text-xs font-semibold tracking-wide disabled:opacity-50 flex items-center gap-2 cursor-pointer shadow-[0_4px_15px_rgba(75,55,178,0.3)]"
              >
                {isUploading ? (
                  <CosmicLoader size="sm" label="Extracting Fields..." />
                ) : (
                  <>
                    <UploadCloud className="w-3.5 h-3.5" />
                    <span>Process Invoice</span>
                  </>
                )}
              </button>
              <button
                onClick={resetUpload}
                disabled={isUploading}
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

      {/* Error Message */}
      {uploadError && (
        <div className="p-4 rounded-2xl bg-[#923F53]/15 border border-[#923F53]/40 text-rose-300 flex items-start gap-3 text-xs cosmic-glass-subtle">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
          <div>
            <span className="font-semibold block">Extraction notice:</span>
            <span>{uploadError}</span>
          </div>
        </div>
      )}

      {/* Extracted Preview Card in Cosmic Violet Glass */}
      {uploadResult && (
        <CosmicGlassPanel className="p-6 sm:p-8 space-y-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)] animate-fade-in">
          <div className="flex items-center justify-between pb-4 border-b border-white/6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-emerald-950/20 text-emerald-400 border border-emerald-800/30">
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
                {uploadResult.currency} {uploadResult.total_amount?.toFixed(2)}
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
              onClick={() => setShowTechnicalDetails((prev) => !prev)}
              className="text-xs text-[#B8B2C8] hover:text-[#F1EDF8] flex items-center gap-1.5 font-medium transition cursor-pointer"
            >
              <span>{showTechnicalDetails ? 'Hide Parsing Details' : 'Show Parsing Details & Diagnostics'}</span>
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5 text-[#BBA8F1]" /> : <ChevronDown className="w-3.5 h-3.5 text-[#8879A7]" />}
            </button>

            {showTechnicalDetails && (
              <div className="mt-3 p-4 cosmic-glass-control rounded-2xl text-[11px] text-[#B8B2C8] space-y-1.5 animate-fade-in font-mono">
                <p>Status: <strong className="text-[#F1EDF8]">{uploadResult.status}</strong></p>
                <p>Indexing: <strong className="text-[#BBA8F1]">ChromaDB Embeddings Synchronized</strong></p>
                <p>Calculation: <strong className="text-[#F1EDF8]">Deterministic Decimal Arithmetic Safe</strong></p>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-white/6">
            <button
              onClick={resetUpload}
              className="text-xs text-[#B8B2C8] hover:text-[#F1EDF8] transition cursor-pointer"
            >
              Upload another invoice
            </button>
            <Link
              to="/invoices"
              className="aovix-gradient-btn inline-flex items-center gap-1.5 px-5 py-2 rounded-full text-xs font-semibold"
            >
              <span>Open in Invoices</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </CosmicGlassPanel>
      )}
    </div>
  );
};
