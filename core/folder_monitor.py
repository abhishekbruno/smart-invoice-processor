import os
import shutil
import threading
import time
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from config.settings import settings
from core.database import db
from core.invoice_parser import invoice_parser
from core.models import ProcessingRecord
from core.pdf_extractor import PDFExtractionError, pdf_extractor
from utils.helpers import get_current_time_str
from utils.logger import logger
from utils.validators import calculate_file_hash, sanitize_filename, validate_pdf_file


class InvoiceProcessingPipeline:
    """Orchestrates PDF validation, duplicate checking, extraction, parsing, and database storage."""

    @staticmethod
    def process_file(
        file_path: Path,
        force_reprocess: bool = False,
        archive_copy: bool = True,
    ) -> Dict:
        """
        Processes an individual PDF invoice file through the full extraction pipeline.
        Returns a result dictionary.
        """
        start_time = time.time()
        file_name = file_path.name
        duration = 0.0

        # 1. Validation check
        is_valid, val_err = validate_pdf_file(file_path)
        if not is_valid:
            duration = time.time() - start_time
            db.log_error(
                stage="validation",
                error_type="ValidationError",
                error_message=val_err,
                file_name=file_name,
            )
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash="",
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                status="failed",
                error_message=val_err,
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {"status": "failed", "error": val_err, "file_name": file_name}

        # 2. Compute SHA-256 Hash
        try:
            file_hash = calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Failed to compute file hash: {str(e)}"
            db.log_error(stage="hashing", error_type="HashError", error_message=err_msg, file_name=file_name)
            return {"status": "failed", "error": err_msg, "file_name": file_name}

        # 3. Duplicate Prevention Check
        if not force_reprocess and db.is_duplicate(file_hash):
            duration = time.time() - start_time
            logger.info(f"Skipping duplicate invoice: {file_name} (Hash: {file_hash[:8]}...)")
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                status="duplicate",
                error_message="File hash already exists in database.",
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {
                "status": "duplicate",
                "message": "Invoice already processed.",
                "file_hash": file_hash,
                "file_name": file_name,
            }

        # 4. Text and Page Extraction
        try:
            extracted_doc = pdf_extractor.extract_from_file(file_path)
        except PDFExtractionError as pe:
            duration = time.time() - start_time
            err_msg = f"PDF extraction error: {str(pe)}"
            logger.error(err_msg)
            db.log_error(
                stage="extraction",
                error_type="PDFExtractionError",
                error_message=err_msg,
                file_name=file_name,
                file_hash=file_hash,
                stack_trace=traceback.format_exc(),
            )
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                status="failed",
                error_message=err_msg,
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {"status": "failed", "error": err_msg, "file_name": file_name}
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Unexpected error during extraction: {str(e)}"
            logger.error(err_msg, exc_info=True)
            db.log_error(
                stage="extraction",
                error_type=type(e).__name__,
                error_message=err_msg,
                file_name=file_name,
                file_hash=file_hash,
                stack_trace=traceback.format_exc(),
            )
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                status="failed",
                error_message=err_msg,
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {"status": "failed", "error": err_msg, "file_name": file_name}

        # 5. Information Parsing
        try:
            invoice_data = invoice_parser.parse(extracted_doc)
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Parsing failure: {str(e)}"
            logger.error(err_msg, exc_info=True)
            db.log_error(
                stage="parsing",
                error_type=type(e).__name__,
                error_message=err_msg,
                file_name=file_name,
                file_hash=file_hash,
                stack_trace=traceback.format_exc(),
            )
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                status="failed",
                error_message=err_msg,
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {"status": "failed", "error": err_msg, "file_name": file_name}

        # 6. Archive copy to processed folder if requested
        dest_path = file_path
        if archive_copy and file_path.resolve() != (settings.PROCESSED_DIR / file_name).resolve():
            try:
                dest_path = settings.PROCESSED_DIR / file_name
                shutil.copy2(file_path, dest_path)
            except Exception as copy_err:
                logger.warning(f"Could not copy file to processed archive: {copy_err}")
                dest_path = file_path

        # 7. Save to SQLite Database
        try:
            invoice_id = db.save_invoice(
                invoice_data=invoice_data,
                source_file_path=str(dest_path),
                file_hash=file_hash,
            )
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"Database save error: {str(e)}"
            logger.error(err_msg, exc_info=True)
            db.log_error(
                stage="database",
                error_type="DatabaseError",
                error_message=err_msg,
                file_name=file_name,
                file_hash=file_hash,
                stack_trace=traceback.format_exc(),
            )
            record = ProcessingRecord(
                file_name=file_name,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                status="failed",
                error_message=err_msg,
                duration_sec=duration,
            )
            db.log_processing_record(record)
            return {"status": "failed", "error": err_msg, "file_name": file_name}

        # 8. Index into Vector Database (ChromaDB)
        try:
            from core.vector_store import vector_store
            full_inv = db.get_invoice_by_id(invoice_id)
            if full_inv:
                pages_data = [
                    {"page_number": p.page_number, "text": p.text}
                    for p in extracted_doc.pages
                ] if hasattr(extracted_doc, "pages") else None
                vector_store.index_invoice(
                    invoice_record=full_inv,
                    raw_text=extracted_doc.cleaned_text,
                    pages_data=pages_data,
                )
        except Exception as v_err:
            logger.warning(f"Vector indexing non-fatal error for invoice #{invoice_id}: {v_err}")

        # 9. Record Successful Audit Log
        duration = time.time() - start_time
        final_status = "needs_review" if invoice_data.needs_review else "success"
        record = ProcessingRecord(
            file_name=file_name,
            file_path=str(dest_path),
            file_hash=file_hash,
            file_size=file_size,
            status=final_status,
            error_message="; ".join(invoice_data.extraction_notes) if invoice_data.needs_review else None,
            duration_sec=duration,
        )
        db.log_processing_record(record)

        logger.info(
            f"Successfully processed invoice #{invoice_data.invoice_number or 'UNKNOWN'} "
            f"from '{invoice_data.vendor_name or 'UNKNOWN'}' ({invoice_data.currency} {invoice_data.total_amount}) "
            f"in {duration:.2f}s [Status: {final_status}]"
        )

        return {
            "status": final_status,
            "invoice_id": invoice_id,
            "invoice_number": invoice_data.invoice_number,
            "vendor_name": invoice_data.vendor_name,
            "total_amount": invoice_data.total_amount,
            "currency": invoice_data.currency,
            "file_hash": file_hash,
            "file_name": file_name,
            "needs_review": invoice_data.needs_review,
            "notes": invoice_data.extraction_notes,
            "duration": duration,
        }


class InvoiceFolderHandler(FileSystemEventHandler):
    """Watchdog event handler for monitoring newly added and modified invoice PDF files."""

    def __init__(self, callback: Optional[Callable[[Path], None]] = None):
        super().__init__()
        self.callback = callback or InvoiceProcessingPipeline.process_file
        self._processing_lock = threading.Lock()
        self._recently_handled: Dict[str, float] = {}

    def _should_process(self, file_path_str: str) -> bool:
        """Debounces events and filters non-PDFs."""
        path = Path(file_path_str)
        if not path.is_file():
            return False
        if not path.name.lower().endswith(".pdf"):
            return False

        # Debounce: avoid duplicate processing within 3 seconds
        now = time.time()
        last_time = self._recently_handled.get(file_path_str, 0)
        if (now - last_time) < 3.0:
            return False

        self._recently_handled[file_path_str] = now
        return True

    def _wait_for_file_settle(self, path: Path, max_wait: float = 3.0) -> bool:
        """Waits until the file size stops changing (e.g., during write/copy operation)."""
        start = time.time()
        last_size = -1
        while (time.time() - start) < max_wait:
            if not path.exists():
                return False
            try:
                curr_size = path.stat().st_size
                if curr_size > 0 and curr_size == last_size:
                    return True
                last_size = curr_size
            except Exception:
                pass
            time.sleep(0.3)
        return path.exists() and path.stat().st_size > 0

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            self._handle_file(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            self._handle_file(Path(event.src_path))

    def _handle_file(self, path: Path) -> None:
        # Run processing in a background worker thread to prevent blocking the watchdog observer loop
        def worker():
            with self._processing_lock:
                if self._wait_for_file_settle(path):
                    logger.info(f"Folder Monitor detected new/modified file: {path.name}")
                    try:
                        self.callback(path)
                    except Exception as e:
                        logger.error(f"Error handling file {path.name}: {e}", exc_info=True)

        threading.Thread(target=worker, daemon=True).start()


class FolderMonitorService:
    """Service to control start/stop of folder monitoring and manual scan execution."""

    def __init__(self, watch_dir: Optional[Path] = None):
        self.watch_dir = watch_dir or settings.INVOICE_WATCH_DIR
        self.observer: Optional[Observer] = None
        self._is_running = False
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        return self._is_running and self.observer is not None and self.observer.is_alive()

    def start(self) -> bool:
        """Starts the background directory watcher."""
        with self._lock:
            if self.is_running:
                logger.info("Folder monitor is already active.")
                return True

            self.watch_dir.mkdir(parents=True, exist_ok=True)
            handler = InvoiceFolderHandler()
            self.observer = Observer()
            self.observer.schedule(handler, str(self.watch_dir), recursive=False)
            self.observer.start()
            self._is_running = True
            logger.info(f"Folder monitor started watching: {self.watch_dir}")
            return True

    def stop(self) -> bool:
        """Stops the background directory watcher safely."""
        with self._lock:
            if not self.is_running:
                return True

            if self.observer:
                try:
                    self.observer.stop()
                    self.observer.join(timeout=3.0)
                except Exception as e:
                    logger.warning(f"Error stopping observer: {e}")
                finally:
                    self.observer = None
                    self._is_running = False

            logger.info("Folder monitor stopped.")
            return True

    def scan_folder_now(self, force_reprocess: bool = False) -> List[Dict]:
        """Manually scans the watched folder and processes any detected PDF files."""
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        results = []
        pdf_files = sorted(list(self.watch_dir.glob("*.pdf")) + list(self.watch_dir.glob("*.PDF")))
        logger.info(f"Manual scan discovered {len(pdf_files)} PDF file(s) in {self.watch_dir}")

        for pdf_path in pdf_files:
            try:
                res = InvoiceProcessingPipeline.process_file(pdf_path, force_reprocess=force_reprocess)
                results.append(res)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name} in manual scan: {e}")
                results.append({"status": "failed", "file_name": pdf_path.name, "error": str(e)})

        return results


# Global folder monitor singleton
folder_monitor = FolderMonitorService()

