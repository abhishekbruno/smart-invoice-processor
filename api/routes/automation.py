from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from api.schemas.automation import (
    AutomationStatusResponse,
    FolderScanResponse,
    GmailSyncResponse,
    SyncHistoryItem,
)
from config.settings import settings
from core.database import db
from core.folder_monitor import folder_monitor
from core.gmail_auth_service import gmail_auth_service
from core.gmail_sync_service import gmail_sync_service

router = APIRouter(prefix="/automation", tags=["RPA & Automation"])


@router.get("/status", response_model=AutomationStatusResponse)
def get_automation_status():
    """Returns real-time status of folder monitoring and Gmail RPA automation."""
    auth_status = gmail_auth_service.get_auth_status()

    return AutomationStatusResponse(
        folder_monitor_active=folder_monitor.is_running,
        watch_directory=str(settings.INVOICE_WATCH_DIR),
        processed_directory=str(settings.PROCESSED_DIR),
        gmail_configured=auth_status.get("is_configured", False),
        gmail_authenticated=auth_status.get("is_authenticated", False),
        gmail_email=auth_status.get("connected_email"),
        gmail_last_synced_at=auth_status.get("last_synced_at"),
        background_poller_running=gmail_sync_service.is_background_sync_running,
        poller_interval_minutes=settings.GMAIL_SYNC_INTERVAL_MINUTES,
    )


@router.post("/scan", response_model=FolderScanResponse)
def trigger_folder_scan():
    """Triggers an on-demand scan of the local invoice watch folder."""
    results = folder_monitor.scan_folder_now()
    new_imported = sum(1 for r in results if r.get("status") == "success")
    duplicates_skipped = sum(1 for r in results if r.get("status") == "duplicate")
    failed_count = sum(1 for r in results if r.get("status") == "failed")

    return FolderScanResponse(
        total_scanned=len(results),
        new_imported=new_imported,
        duplicates_skipped=duplicates_skipped,
        failed_count=failed_count,
        timestamp=datetime.now().isoformat(),
    )


@router.post("/gmail/sync", response_model=GmailSyncResponse)
def trigger_gmail_sync(query: Optional[str] = Query(None, description="Optional custom Gmail search filter")):
    """Triggers an on-demand scan of Gmail inbox for invoice PDF attachments."""
    res = gmail_sync_service.run_sync(query=query)

    return GmailSyncResponse(
        status=res.get("status", "error"),
        messages_scanned=res.get("messages_scanned", 0),
        attachments_found=res.get("attachments_found", 0),
        invoices_imported=res.get("invoices_imported", 0),
        duplicates_skipped=res.get("duplicates_skipped", 0),
        failed_count=res.get("failed_count", 0),
        error=res.get("error"),
    )


@router.get("/history", response_model=List[SyncHistoryItem])
def get_sync_history(limit: int = Query(20, ge=1, le=100)):
    """Returns recent Gmail RPA synchronization audit history."""
    history = db.get_recent_sync_history(limit=limit)
    return [
        SyncHistoryItem(
            id=h["id"],
            started_at=h["started_at"],
            completed_at=h.get("completed_at"),
            status=h["status"],
            messages_scanned=h.get("messages_scanned", 0),
            attachments_found=h.get("attachments_found", 0),
            invoices_imported=h.get("invoices_imported", 0),
            duplicates_skipped=h.get("duplicates_skipped", 0),
            failed_count=h.get("failed_count", 0),
            error_details=h.get("error_details"),
        )
        for h in history
    ]

