export interface LineItem {
  id?: number;
  description: string;
  quantity?: number;
  unit_price?: number;
  amount?: number;
}

export interface InvoiceListItem {
  id: number;
  invoice_number?: string | null;
  vendor_name?: string | null;
  invoice_date?: string | null;
  due_date?: string | null;
  total_amount?: number | null;
  currency: string;
  converted_amount?: number | null;
  converted_currency?: string | null;
  status: 'processed' | 'needs_review' | 'verified' | 'suspected_duplicate';
  is_duplicate: boolean;
  duplicate_of_id?: number | null;
  duplicate_reason?: string | null;
  created_at: string;
}

export interface InvoiceDetail extends InvoiceListItem {
  customer_name?: string | null;
  subtotal?: number | null;
  tax_amount?: number | null;
  payment_status?: string | null;
  source_file_path?: string | null;
  file_hash: string;
  confidence_scores: Record<string, number>;
  extraction_notes: string[];
  line_items: LineItem[];
  updated_at?: string | null;
}

export interface PaginatedInvoices {
  items: InvoiceListItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AnalyticsSummary {
  total_invoices: number;
  eligible_invoices: number;
  processed_cleanly: number;
  needs_review: number;
  verified_invoices: number;
  suspected_duplicates: number;
  total_spending: number;
  display_currency: string;
  formatted_total: string;
  vendor_count: number;
  effective_rate_source: string;
}

export interface MonthlySpending {
  month: string;
  converted_spent: number;
  invoice_count: number;
  display_currency: string;
}

export interface VendorSpending {
  vendor: string;
  converted_spent: number;
  invoice_count: number;
  display_currency: string;
}

export interface CurrencyDistribution {
  currency: string;
  invoice_count: number;
  original_total: number;
  converted_total: number;
  display_currency: string;
}

export interface ExpenseAnalytics {
  summary: AnalyticsSummary;
  monthly_spending: MonthlySpending[];
  vendor_spending: VendorSpending[];
  currency_distribution: CurrencyDistribution[];
}

export interface CitationItem {
  filename?: string | null;
  invoice_number?: string | null;
  vendor?: string | null;
  page_number?: number | null;
  snippet?: string | null;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  query_type?: 'SQL' | 'RAG' | 'Hybrid';
  citations?: CitationItem[];
  verified_totals?: Record<string, any>;
  is_fallback?: boolean;
  timestamp: string;
}

export interface AutomationStatus {
  folder_monitor_active: boolean;
  watch_directory: string;
  processed_directory: string;
  gmail_configured: boolean;
  gmail_authenticated: boolean;
  gmail_email?: string | null;
  gmail_last_synced_at?: string | null;
  background_poller_running: boolean;
  poller_interval_minutes: number;
}

export interface SyncHistoryItem {
  id: number;
  started_at: string;
  completed_at?: string | null;
  status: string;
  messages_scanned: number;
  attachments_found: number;
  invoices_imported: number;
  duplicates_skipped: number;
  failed_count: number;
  error_details?: string | null;
}

export interface AppSettings {
  preferred_display_currency: string;
  supported_currencies: string[];
  latest_reference_rates_usd: Record<string, number>;
  exchange_rate_source: string;
  storage: {
    watch_dir: string;
    processed_dir: string;
    db_path: string;
    chroma_dir: string;
  };
  ai: {
    gemini_model: string;
    embedding_model: string;
  };
}

export interface ProcessingActivityItem {
  id: number;
  file_name: string;
  file_path: string;
  file_hash: string;
  file_size: number;
  status: 'success' | 'duplicate' | 'failed' | string;
  error_message?: string | null;
  duration_sec?: number | null;
  processed_at: string;
}

export interface SystemStatus {
  status: string;
  environment: string;
  database: {
    status: string;
    path: string;
    counts: Record<string, number>;
  };
  vector_store: {
    status: string;
    collection_name: string;
    total_chunks: number;
    unique_invoices_indexed: number;
    embedding_model: string;
    embedding_dimensions: number;
  };
  ai_service: {
    provider: string;
    is_configured: boolean;
    configured_model: string;
    active_model?: string;
  };
}

