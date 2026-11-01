from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AutomationStatusResponse(BaseModel):
    folder_monitor_active: bool
    watch_directory: str
    processed_directory: str
    gmail_configured: bool
    gmail_authenticated: bool
    gmail_email: Optional[str] = None
    gmail_last_synced_at: Optional[str] = None
    background_poller_running: bool
    poller_interval_minutes: int


class FolderScanResponse(BaseModel):
    total_scanned: int
    new_imported: int
    duplicates_skipped: int
    failed_count: int
    timestamp: str


class GmailSyncResponse(BaseModel):
    status: str
    messages_scanned: int
    attachments_found: int
    invoices_imported: int
    duplicates_skipped: int
    failed_count: int
    error: Optional[str] = None


class SyncHistoryItem(BaseModel):
    id: int
    started_at: str
    completed_at: Optional[str] = None
    status: str
    messages_scanned: int
    attachments_found: int
    invoices_imported: int
    duplicates_skipped: int
    failed_count: int
    error_details: Optional[str] = None

