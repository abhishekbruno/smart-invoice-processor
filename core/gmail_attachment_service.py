import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings
from core.database import db
from core.folder_monitor import InvoiceProcessingPipeline
from utils.logger import logger
from utils.validators import sanitize_filename


class GmailAttachmentService:
    """Validates, deduplicates, saves, and ingests PDF invoice attachments downloaded from Gmail."""

    def __init__(self, watch_dir: Optional[Path] = None):
        self.watch_dir = watch_dir or settings.INVOICE_WATCH_DIR
        self.watch_dir.mkdir(parents=True, exist_ok=True)

    def process_attachment(
        self,
        content_bytes: bytes,
        filename: str,
        attachment_id: str,
        message_id: str,
        sender: Optional[str] = None,
        subject: Optional[str] = None,
        date_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates raw attachment bytes, enforces Stage 1 duplicate prevention,
        saves to the ingestion watch folder, and passes to the invoice processing pipeline.
        """
        # 1. Validation: Size check
        file_size = len(content_bytes)
        if file_size == 0:
            err = "Attachment is empty (0 bytes)."
            logger.warning(f"Gmail attachment {filename} rejected: {err}")
            db.record_processed_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                file_name=filename,
                download_status="failed",
            )
            return {"status": "failed", "error": err, "file_name": filename}

        if file_size > settings.MAX_FILE_SIZE_BYTES:
            err = f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds maximum allowed {settings.MAX_FILE_SIZE_MB} MB."
            logger.warning(f"Gmail attachment {filename} rejected: {err}")
            db.record_processed_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                file_name=filename,
                download_status="failed",
            )
            return {"status": "failed", "error": err, "file_name": filename}

        # 2. Validation: Magic bytes (PDF header check)
        if not content_bytes.startswith(b"%PDF-"):
            err = "Invalid PDF file structure. File magic bytes do not begin with %PDF-."
            logger.warning(f"Gmail attachment {filename} rejected: {err}")
            db.record_processed_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                file_name=filename,
                download_status="failed",
            )
            return {"status": "failed", "error": err, "file_name": filename}

        # 3. Compute SHA-256 hash
        file_hash = hashlib.sha256(content_bytes).hexdigest()

        # 4. Stage 1 Deduplication Check:
        # Check if already processed in Gmail attachments or already indexed by hash in SQLite
        if db.is_gmail_attachment_processed(message_id, attachment_id, file_hash=file_hash) or db.is_duplicate(file_hash):
            logger.info(f"Skipping duplicate Gmail attachment: {filename} (Hash: {file_hash[:8]}...)")
            db.record_processed_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                file_name=filename,
                file_hash=file_hash,
                download_status="skipped_duplicate",
            )
            return {
                "status": "skipped_duplicate",
                "file_name": filename,
                "file_hash": file_hash,
                "message": "Attachment or identical content already processed in database.",
            }

        # 5. Sanitize and generate unique safe destination filename
        clean_name = sanitize_filename(filename)
        if not clean_name.lower().endswith(".pdf"):
            clean_name += ".pdf"

        # Prefix with gmail identifier to track provenance and prevent collisions
        safe_prefix = f"gmail_{message_id[:6]}_"
        target_name = safe_prefix + clean_name
        dest_path = self.watch_dir / target_name

        # If a file with that name already exists on disk, add disambiguation
        counter = 1
        stem = Path(target_name).stem
        while dest_path.exists():
            dest_path = self.watch_dir / f"{stem}_{counter}.pdf"
            counter += 1

        # 6. Save PDF to watch folder
        try:
            dest_path.write_bytes(content_bytes)
            logger.info(f"Saved Gmail attachment to: {dest_path}")
        except Exception as e:
            err = f"Failed writing attachment to disk: {str(e)}"
            logger.error(err)
            db.record_processed_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                file_name=filename,
                download_status="failed",
            )
            return {"status": "failed", "error": err, "file_name": filename}

        # 7. Ingest through standard InvoiceProcessingPipeline
        pipeline_res = InvoiceProcessingPipeline.process_file(dest_path, force_reprocess=False, archive_copy=True)

        inv_id = None
        if pipeline_res.get("status") in ("success", "needs_review", "duplicate"):
            inv_row = db.get_invoice_by_hash(file_hash)
            if inv_row:
                inv_id = inv_row.get("id")

        # 8. Record attachment history in SQLite
        db.record_processed_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            file_name=dest_path.name,
            file_hash=file_hash,
            invoice_id=inv_id,
            download_status="downloaded",
        )

        return {
            "status": pipeline_res.get("status", "success"),
            "file_name": dest_path.name,
            "file_hash": file_hash,
            "invoice_id": inv_id,
            "details": pipeline_res,
        }


# Global singleton
gmail_attachment_service = GmailAttachmentService()

