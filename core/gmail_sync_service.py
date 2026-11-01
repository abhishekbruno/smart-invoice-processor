import threading
import time
from typing import Any, Dict, Optional

from config.settings import settings
from core.database import db
from core.gmail_attachment_service import GmailAttachmentService, gmail_attachment_service
from core.gmail_auth_service import GmailAuthService, gmail_auth_service
from core.gmail_service import GmailService, gmail_service
from utils.logger import logger


class GmailSyncService:
    """Orchestrates manual and scheduled synchronization of invoice PDF attachments from Gmail."""

    def __init__(
        self,
        auth_service: Optional[GmailAuthService] = None,
        api_service: Optional[GmailService] = None,
        attachment_service: Optional[GmailAttachmentService] = None,
    ):
        self.auth_service = auth_service or gmail_auth_service
        self.api_service = api_service or gmail_service
        self.attachment_service = attachment_service or gmail_attachment_service
        self._sync_lock = threading.Lock()
        self._bg_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._interval_minutes = settings.GMAIL_SYNC_INTERVAL_MINUTES

    @property
    def is_running_sync(self) -> bool:
        """Returns True if a synchronization run is actively in progress."""
        return self._sync_lock.locked()

    @property
    def is_background_sync_running(self) -> bool:
        """Returns True if the background scheduler daemon is running."""
        return self._bg_thread is not None and self._bg_thread.is_alive()

    def run_sync(
        self,
        query: Optional[str] = None,
        max_messages: int = 50,
    ) -> Dict[str, Any]:
        """
        Executes a synchronization cycle: queries messages, extracts PDF attachments,
        deduplicates, saves, and ingests them into the invoice processing pipeline.
        """
        if not self.auth_service.is_authenticated():
            msg = "Gmail is not authenticated. Please connect your Google account in Settings or Automation."
            logger.warning(msg)
            return {"status": "error", "error": msg}

        if not self._sync_lock.acquire(blocking=False):
            msg = "A Gmail synchronization is already in progress. Please wait for it to complete."
            logger.info(msg)
            return {"status": "in_progress", "message": msg}

        sync_query = query or settings.GMAIL_SEARCH_QUERY
        sync_id = db.create_sync_history()

        messages_scanned = 0
        attachments_found = 0
        invoices_imported = 0
        duplicates_skipped = 0
        failed_count = 0
        error_details = None

        try:
            logger.info(f"Starting Gmail sync (Query: '{sync_query}', Max: {max_messages})")
            messages = self.api_service.search_messages(query=sync_query, max_results=max_messages)
            messages_scanned = len(messages)

            for msg_meta in messages:
                msg_id = msg_meta.get("id")
                thread_id = msg_meta.get("threadId")
                if not msg_id:
                    continue

                # Fetch full message payload
                msg_details = self.api_service.get_message_details(msg_id)
                if not msg_details:
                    failed_count += 1
                    continue

                headers = self.api_service.extract_headers(msg_details)
                sender = headers.get("from")
                subject = headers.get("subject")
                date_str = headers.get("date")

                # Find all PDF attachments in message structure
                pdf_attachments = self.api_service.find_pdf_attachments(msg_details)

                for att in pdf_attachments:
                    attachments_found += 1
                    att_id = att.get("attachment_id")
                    att_name = att.get("filename")

                    # Stage 1 duplicate check: Has this attachment ID already been handled?
                    if db.is_gmail_attachment_processed(msg_id, att_id):
                        logger.info(f"Attachment {att_name} already registered for msg {msg_id}. Skipping.")
                        duplicates_skipped += 1
                        continue

                    # Download raw content bytes
                    att_bytes = self.api_service.download_attachment_bytes(msg_id, att_id)
                    if not att_bytes:
                        logger.warning(f"Failed to download bytes for attachment {att_name} in msg {msg_id}.")
                        failed_count += 1
                        continue

                    # Validate, deduplicate, save, and process
                    proc_res = self.attachment_service.process_attachment(
                        content_bytes=att_bytes,
                        filename=att_name,
                        attachment_id=att_id,
                        message_id=msg_id,
                        sender=sender,
                        subject=subject,
                        date_str=date_str,
                    )

                    status = proc_res.get("status")
                    if status in ("skipped_duplicate", "duplicate"):
                        duplicates_skipped += 1
                    elif status in ("success", "needs_review"):
                        invoices_imported += 1
                    else:
                        failed_count += 1

                # Record message scan completion
                db.record_processed_message(
                    message_id=msg_id,
                    thread_id=thread_id,
                    sender=sender,
                    subject=subject,
                    date=date_str,
                )

            # Record success
            active_acc = db.get_active_gmail_account()
            if active_acc:
                db.update_gmail_last_synced(active_acc.get("email"))

            final_status = "success" if failed_count == 0 else "partial"
            db.update_sync_history(
                sync_id=sync_id,
                status=final_status,
                messages_scanned=messages_scanned,
                attachments_found=attachments_found,
                invoices_imported=invoices_imported,
                duplicates_skipped=duplicates_skipped,
                failed_count=failed_count,
            )

            res = {
                "status": final_status,
                "messages_scanned": messages_scanned,
                "attachments_found": attachments_found,
                "invoices_imported": invoices_imported,
                "duplicates_skipped": duplicates_skipped,
                "failed_count": failed_count,
            }
            logger.info(f"Gmail sync finished: {res}")
            return res

        except Exception as e:
            error_details = str(e)
            logger.error(f"Gmail sync execution failed: {e}", exc_info=True)
            db.update_sync_history(
                sync_id=sync_id,
                status="failed",
                messages_scanned=messages_scanned,
                attachments_found=attachments_found,
                invoices_imported=invoices_imported,
                duplicates_skipped=duplicates_skipped,
                failed_count=failed_count + 1,
                error_details=error_details,
            )
            return {
                "status": "failed",
                "error": error_details,
                "messages_scanned": messages_scanned,
                "attachments_found": attachments_found,
                "invoices_imported": invoices_imported,
            }
        finally:
            self._sync_lock.release()

    def start_background_sync(self, interval_minutes: Optional[int] = None) -> bool:
        """Starts periodic background polling thread if not already running."""
        if interval_minutes:
            self._interval_minutes = interval_minutes

        if self.is_background_sync_running:
            logger.info("Background Gmail sync worker is already running.")
            return True

        self._stop_event.clear()

        def _worker_loop():
            logger.info(f"Gmail background sync worker started (Interval: {self._interval_minutes}m).")
            while not self._stop_event.is_set():
                try:
                    if self.auth_service.is_authenticated():
                        self.run_sync()
                except Exception as loop_err:
                    logger.error(f"Error in background sync worker loop: {loop_err}")

                # Sleep in short increments to allow responsive shutdown
                sleep_seconds = self._interval_minutes * 60
                for _ in range(int(sleep_seconds)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)

            logger.info("Gmail background sync worker terminated.")

        self._bg_thread = threading.Thread(target=_worker_loop, name="GmailSyncWorker", daemon=True)
        self._bg_thread.start()
        return True

    def stop_background_sync(self) -> None:
        """Signals the background sync worker to shut down."""
        if self._bg_thread and self._bg_thread.is_alive():
            self._stop_event.set()
            self._bg_thread.join(timeout=3.0)
            self._bg_thread = None
            logger.info("Gmail background sync stopped.")


# Global singleton
gmail_sync_service = GmailSyncService()

