import axios from 'axios';
import type {
  AnalyticsSummary,
  AppSettings,
  AutomationStatus,
  ExpenseAnalytics,
  InvoiceDetail,
  InvoiceListItem,
  MonthlySpending,
  PaginatedInvoices,
  SyncHistoryItem,
  SystemStatus,
  VendorSpending,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Invoices
// ============================================================================

export async function fetchInvoices(params?: {
  page?: number;
  limit?: number;
  vendor?: string;
  status?: string;
  currency?: string;
  include_duplicates?: boolean;
}): Promise<PaginatedInvoices> {
  const res = await apiClient.get<PaginatedInvoices>('/invoices', { params });
  return res.data;
}

export async function fetchDuplicates(): Promise<InvoiceListItem[]> {
  const res = await apiClient.get<InvoiceListItem[]>('/invoices/duplicates');
  return res.data;
}

export async function fetchInvoiceDetail(id: number): Promise<InvoiceDetail> {
  const res = await apiClient.get<InvoiceDetail>(`/invoices/${id}`);
  return res.data;
}

export async function uploadInvoiceFile(file: File): Promise<{
  status: string;
  invoice_id?: number;
  file_name: string;
  file_hash?: string;
  vendor?: string;
  invoice_number?: string;
  total_amount?: number;
  currency?: string;
  is_duplicate?: boolean;
  duplicate_reason?: string;
  message?: string;
}> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await apiClient.post('/invoices/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function updateInvoice(
  id: number,
  data: Partial<InvoiceDetail>
): Promise<{ success: boolean; data: InvoiceDetail }> {
  const res = await apiClient.patch(`/invoices/${id}`, data);
  return res.data;
}

export async function deleteInvoice(id: number): Promise<{ success: boolean }> {
  const res = await apiClient.delete(`/invoices/${id}`);
  return res.data;
}

export async function verifyInvoice(id: number): Promise<{ success: boolean }> {
  const res = await apiClient.post(`/invoices/${id}/verify`);
  return res.data;
}

export async function markInvoiceGenuine(id: number): Promise<{ success: boolean }> {
  const res = await apiClient.post(`/invoices/${id}/mark-genuine`);
  return res.data;
}

export async function confirmInvoiceDuplicate(id: number): Promise<{ success: boolean }> {
  const res = await apiClient.post(`/invoices/${id}/confirm-duplicate`);
  return res.data;
}

export function getInvoiceDocumentUrl(id: number): string {
  return `${API_BASE}/invoices/${id}/document`;
}

// ============================================================================
// Analytics
// ============================================================================

export async function fetchAnalyticsSummary(currency?: string, mode: string = 'historical'): Promise<AnalyticsSummary> {
  const res = await apiClient.get<AnalyticsSummary>('/analytics/summary', {
    params: { currency, mode },
  });
  return res.data;
}

export async function fetchMonthlySpending(currency?: string, mode: string = 'historical'): Promise<MonthlySpending[]> {
  const res = await apiClient.get<MonthlySpending[]>('/analytics/monthly', {
    params: { currency, mode },
  });
  return res.data;
}

export async function fetchVendorSpending(currency?: string, mode: string = 'historical'): Promise<VendorSpending[]> {
  const res = await apiClient.get<VendorSpending[]>('/analytics/vendors', {
    params: { currency, mode },
  });
  return res.data;
}

export async function fetchFullAnalytics(currency?: string, mode: string = 'historical'): Promise<ExpenseAnalytics> {
  const res = await apiClient.get<ExpenseAnalytics>('/analytics/expenses', {
    params: { currency, mode },
  });
  return res.data;
}

export async function fetchRecentActivity(limit: number = 10): Promise<import('../types').ProcessingActivityItem[]> {
  const res = await apiClient.get<import('../types').ProcessingActivityItem[]>('/analytics/activity', {
    params: { limit },
  });
  return res.data;
}

// ============================================================================
// AI Chat & RAG
// ============================================================================

export async function sendChatMessage(query: string, sessionId?: string): Promise<{
  query: string;
  query_type: 'SQL' | 'RAG' | 'Hybrid';
  answer: string;
  citations: Array<{
    filename?: string;
    invoice_number?: string;
    vendor?: string;
    page_number?: number;
    snippet?: string;
  }>;
  verified_totals?: Record<string, any>;
  is_fallback: boolean;
  timestamp: string;
}> {
  const res = await apiClient.post('/chat/query', {
    query,
    session_id: sessionId,
  });
  return res.data;
}

export async function fetchChatStatus(): Promise<{
  is_gemini_available: boolean;
  configured_model: string;
  active_model?: string;
  total_indexed_chunks: number;
  unique_invoices_indexed: number;
  status: string;
}> {
  const res = await apiClient.get('/chat/status');
  return res.data;
}

// ============================================================================
// Automation & RPA
// ============================================================================

export async function fetchAutomationStatus(): Promise<AutomationStatus> {
  const res = await apiClient.get<AutomationStatus>('/automation/status');
  return res.data;
}

export async function triggerFolderScan(): Promise<{
  total_scanned: number;
  new_imported: number;
  duplicates_skipped: number;
  failed_count: number;
}> {
  const res = await apiClient.post('/automation/scan');
  return res.data;
}

export async function triggerGmailSync(query?: string): Promise<{
  status: string;
  messages_scanned: number;
  attachments_found: number;
  invoices_imported: number;
  duplicates_skipped: number;
  failed_count: number;
  error?: string;
}> {
  const res = await apiClient.post('/automation/gmail/sync', null, { params: { query } });
  return res.data;
}

export async function fetchSyncHistory(limit: number = 20): Promise<SyncHistoryItem[]> {
  const res = await apiClient.get<SyncHistoryItem[]>('/automation/history', { params: { limit } });
  return res.data;
}

// ============================================================================
// Reports
// ============================================================================

export async function downloadReportFile(
  type: 'invoices' | 'monthly' | 'vendors',
  format: 'csv' | 'xlsx' | 'pdf',
  params?: Record<string, any>
): Promise<Blob> {
  const res = await apiClient.get(`/reports/${type}`, {
    params: { format, ...params },
    responseType: 'blob',
  });
  return res.data;
}

// ============================================================================
// Settings & System
// ============================================================================

export async function fetchSettings(): Promise<{ success: boolean; data: AppSettings }> {
  const res = await apiClient.get<{ success: boolean; data: AppSettings }>('/settings');
  return res.data;
}

export async function updatePreferredCurrency(currency: string): Promise<{ success: boolean; data: { preferred_display_currency: string } }> {
  const res = await apiClient.post('/settings/currency', { currency });
  return res.data;
}

export async function triggerVectorReindex(): Promise<{ success: boolean; message: string; data: any }> {
  const res = await apiClient.post('/settings/reindex');
  return res.data;
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await apiClient.get<SystemStatus>('/system/status');
  return res.data;
}

