import json
import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from config.settings import settings
from core.models import InvoiceData, LineItem, ProcessingRecord
from utils.helpers import extract_quarter, get_current_time_str
from utils.logger import logger


def normalize_vendor_name(name: Optional[str]) -> str:
    """Normalizes vendor names for robust logical duplicate matching."""
    if not name:
        return ""
    n = name.strip().lower()
    # Remove punctuation
    n = re.sub(r"[^\w\s]", "", n)
    # Strip common corporate legal entity suffixes
    n = re.sub(r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|services|technologies|group|co|company)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    aliases = {
        "aws": "amazon web services",
        "amazon": "amazon web services",
        "amazon web": "amazon web services",
        "gcp": "google cloud",
        "google": "google cloud",
        "msft": "microsoft",
        "azure": "microsoft",
        "do": "digitalocean",
    }
    return aliases.get(n, n)


def normalize_invoice_number(num: Optional[str]) -> str:
    """Normalizes invoice numbers for robust logical duplicate matching."""
    if not num:
        return ""
    n = str(num).strip().upper()
    n = re.sub(r"^[#:\s]+", "", n)
    return n


class DatabaseManager:
    """Manages SQLite storage and queries for invoices and processing records."""

    _local = threading.local()

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Thread-safe connection provider with row factory enabled."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes tables and indexes if they do not already exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Invoices Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT,
                    vendor_name TEXT,
                    invoice_date TEXT,      -- YYYY-MM-DD
                    due_date TEXT,          -- YYYY-MM-DD
                    customer_name TEXT,
                    subtotal REAL,
                    tax_amount REAL,
                    total_amount REAL,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    payment_status TEXT,    -- PAID, PENDING, OVERDUE, etc.
                    source_file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    raw_text TEXT,
                    confidence_scores TEXT, -- JSON
                    extraction_notes TEXT,  -- JSON
                    status TEXT NOT NULL DEFAULT 'processed', -- processed, needs_review, verified, suspected_duplicate
                    is_duplicate INTEGER NOT NULL DEFAULT 0,
                    duplicate_of_id INTEGER,
                    duplicate_reason TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

            # Migration: ensure is_duplicate, duplicate_of_id, duplicate_reason exist
            for col_sql in [
                "ALTER TABLE invoices ADD COLUMN is_duplicate INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE invoices ADD COLUMN duplicate_of_id INTEGER;",
                "ALTER TABLE invoices ADD COLUMN duplicate_reason TEXT;",
            ]:
                try:
                    cursor.execute(col_sql)
                except sqlite3.OperationalError:
                    pass

            # 2. Invoice Line Items Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    quantity REAL DEFAULT 1.0,
                    unit_price REAL DEFAULT 0.0,
                    amount REAL DEFAULT 0.0,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
                );
                """
            )

            # 3. Document Processing Records Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    status TEXT NOT NULL,  -- success, failed, duplicate, needs_review
                    error_message TEXT,
                    duration_sec REAL DEFAULT 0.0,
                    processed_at TEXT NOT NULL
                );
                """
            )

            # 4. File Metadata Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT NOT NULL UNIQUE,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT DEFAULT 'application/pdf',
                    first_seen_at TEXT NOT NULL,
                    last_processed_at TEXT NOT NULL
                );
                """
            )

            # 5. Processing Errors Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT,
                    file_hash TEXT,
                    stage TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

            # 6. Chat History Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

            # 7. Exchange Rate Cache Table (Frankfurter / ECB reference rates)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS exchange_rate_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_currency TEXT NOT NULL,
                    to_currency TEXT NOT NULL,
                    rate_date TEXT NOT NULL,       -- 'latest' or 'YYYY-MM-DD'
                    effective_date TEXT NOT NULL,  -- YYYY-MM-DD
                    rate REAL NOT NULL,
                    rate_decimal TEXT NOT NULL,
                    source TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    UNIQUE(from_currency, to_currency, rate_date)
                );
                """
            )

            # 8. User / System Settings Table (Preferences, Display Currency, etc.)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

            # 9. Gmail Connected Accounts
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gmail_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    connected_at TEXT NOT NULL,
                    last_synced_at TEXT
                );
                """
            )

            # 10. Gmail Sync History
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gmail_sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL, -- running, success, failed, partial
                    messages_scanned INTEGER NOT NULL DEFAULT 0,
                    attachments_found INTEGER NOT NULL DEFAULT 0,
                    invoices_imported INTEGER NOT NULL DEFAULT 0,
                    duplicates_skipped INTEGER NOT NULL DEFAULT 0,
                    failed_count INTEGER NOT NULL DEFAULT 0,
                    error_details TEXT
                );
                """
            )

            # 11. Gmail Processed Messages
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gmail_processed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL UNIQUE,
                    thread_id TEXT,
                    sender TEXT,
                    subject TEXT,
                    date TEXT,
                    processed_at TEXT NOT NULL
                );
                """
            )

            # 12. Gmail Processed Attachments
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gmail_processed_attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    attachment_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT,
                    invoice_id INTEGER,
                    download_status TEXT NOT NULL, -- downloaded, skipped_duplicate, failed
                    downloaded_at TEXT NOT NULL,
                    UNIQUE(message_id, attachment_id)
                );
                """
            )

            # Performance Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_hash ON invoices(file_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_vendor ON invoices(vendor_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_dup ON invoices(is_duplicate);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_dup_of ON invoices(duplicate_of_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_invoice ON invoice_items(invoice_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_hash ON processing_records(file_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_cache ON exchange_rate_cache(from_currency, to_currency, rate_date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gmail_proc_msg ON gmail_processed_messages(message_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gmail_proc_att ON gmail_processed_attachments(message_id, attachment_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gmail_sync_status ON gmail_sync_history(status);")

        # Automatically audit and classify any existing records
        try:
            self.audit_and_flag_duplicates()
        except Exception as e:
            logger.debug(f"Initial duplicate audit notice: {e}")

    # =========================================================================
    # Duplicate Checking & Metadata
    # =========================================================================

    def is_duplicate(self, file_hash: str) -> bool:
        """Checks if a file with the given SHA-256 hash has already been processed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM invoices WHERE file_hash = ?", (file_hash,))
            return cursor.fetchone() is not None

    def get_invoice_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieves an invoice record by its file hash."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE file_hash = ?", (file_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def find_logical_duplicate(
        self,
        vendor_name: Optional[str],
        invoice_number: Optional[str],
        total_amount: Optional[float] = None,
        invoice_date: Optional[str] = None,
        currency: Optional[str] = None,
        exclude_file_hash: Optional[str] = None,
        exclude_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Detects if an invoice logically matches an existing invoice in the database
        based on normalized invoice number, normalized vendor identity, and financial fields.
        """
        norm_inv_num = normalize_invoice_number(invoice_number)
        norm_vendor = normalize_vendor_name(vendor_name)

        if not norm_inv_num:
            return None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM invoices WHERE UPPER(TRIM(invoice_number)) = ?"
            params: List[Any] = [norm_inv_num]

            if exclude_file_hash:
                query += " AND file_hash != ?"
                params.append(exclude_file_hash)
            if exclude_id:
                query += " AND id != ?"
                params.append(exclude_id)

            cursor.execute(query, tuple(params))
            candidates = [dict(r) for r in cursor.fetchall()]

            for cand in candidates:
                cand_vendor = normalize_vendor_name(cand.get("vendor_name"))

                vendor_matches = (
                    norm_vendor == cand_vendor
                    or not norm_vendor
                    or not cand_vendor
                    or norm_vendor in cand_vendor
                    or cand_vendor in norm_vendor
                )

                if not vendor_matches:
                    continue

                cand_tot = cand.get("total_amount")
                cand_date = cand.get("invoice_date")

                amount_matches = False
                if total_amount is not None and cand_tot is not None:
                    amount_matches = abs(float(total_amount) - float(cand_tot)) < 0.01
                elif total_amount is None and cand_tot is None:
                    amount_matches = True

                date_matches = bool(invoice_date and cand_date and invoice_date == cand_date)

                # Logical duplicate confirmation:
                # 1. Matching vendor & invoice number with matching total amount
                # 2. Matching vendor & invoice number with matching date
                # 3. Matching exact normalized vendor & invoice number
                if amount_matches or date_matches or (norm_vendor and norm_vendor == cand_vendor):
                    return cand

            return None

    def audit_and_flag_duplicates(self) -> Dict[str, Any]:
        """
        Audits all invoices in the database and identifies logical duplicates
        where vendor identity and invoice number match across different file hashes.
        Flags duplicates for review and excludes them from spending without deleting records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices ORDER BY id ASC")
            all_invoices = [dict(r) for r in cursor.fetchall()]

            seen: Dict[Tuple[str, str], Dict[str, Any]] = {}
            flagged_count = 0
            flagged_records = []

            for inv in all_invoices:
                norm_vendor = normalize_vendor_name(inv.get("vendor_name"))
                norm_num = normalize_invoice_number(inv.get("invoice_number"))

                if not norm_num:
                    continue

                key = (norm_vendor, norm_num)

                if key in seen:
                    prev = seen[key]
                    # Check if previous was incomplete and current has valid amount
                    if prev.get("total_amount") is None and inv.get("total_amount") is not None:
                        reason = f"Superseded by complete extraction in Invoice #{inv['id']}"
                        cursor.execute(
                            "UPDATE invoices SET is_duplicate = 1, duplicate_of_id = ?, duplicate_reason = ?, status = 'suspected_duplicate' WHERE id = ?",
                            (inv["id"], reason, prev["id"]),
                        )
                        cursor.execute(
                            "UPDATE invoices SET is_duplicate = 0, duplicate_of_id = NULL, duplicate_reason = NULL, status = 'processed' WHERE id = ?",
                            (inv["id"],),
                        )
                        seen[key] = inv
                        flagged_count += 1
                        flagged_records.append({"duplicate_id": prev["id"], "original_id": inv["id"], "reason": reason})
                    else:
                        reason = f"Exact logical duplicate of Invoice #{prev['id']} ({prev['invoice_number']}) from {prev['vendor_name']}"
                        cursor.execute(
                            "UPDATE invoices SET is_duplicate = 1, duplicate_of_id = ?, duplicate_reason = ?, status = 'suspected_duplicate' WHERE id = ?",
                            (prev["id"], reason, inv["id"]),
                        )
                        flagged_count += 1
                        flagged_records.append({"duplicate_id": inv["id"], "original_id": prev["id"], "reason": reason})
                else:
                    seen[key] = inv
                    if inv.get("is_duplicate") == 1:
                        cursor.execute(
                            "UPDATE invoices SET is_duplicate = 0, duplicate_of_id = NULL, duplicate_reason = NULL WHERE id = ?",
                            (inv["id"],),
                        )

            return {
                "total_scanned": len(all_invoices),
                "flagged_duplicates": flagged_count,
                "eligible_invoices": len(seen),
                "records": flagged_records,
            }

    def mark_invoice_genuine(self, invoice_id: int) -> bool:
        """Marks an invoice as genuine/verified, clearing duplicate flag and including in spending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE invoices SET is_duplicate = 0, duplicate_of_id = NULL, duplicate_reason = NULL, status = 'verified', updated_at = ? WHERE id = ?",
                (get_current_time_str(), invoice_id),
            )
            return cursor.rowcount > 0

    def mark_invoice_duplicate(self, invoice_id: int, duplicate_of_id: Optional[int] = None, reason: Optional[str] = None) -> bool:
        """Flags an invoice as a suspected duplicate, excluding it from financial calculations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            reason_str = reason or (f"Flagged as duplicate of Invoice #{duplicate_of_id}" if duplicate_of_id else "Flagged as duplicate")
            cursor.execute(
                "UPDATE invoices SET is_duplicate = 1, duplicate_of_id = ?, duplicate_reason = ?, status = 'suspected_duplicate', updated_at = ? WHERE id = ?",
                (duplicate_of_id, reason_str, get_current_time_str(), invoice_id),
            )
            return cursor.rowcount > 0

    # =========================================================================
    # Invoice CRUD Operations
    # =========================================================================

    def save_invoice(
        self,
        invoice_data: InvoiceData,
        source_file_path: str,
        file_hash: str,
    ) -> int:
        """
        Saves or updates an extracted invoice and its line items in the database.
        Checks for SHA-256 and logical duplicates. Flags duplicates for review.
        Returns the new invoice ID.
        """
        now = get_current_time_str()

        # Check for logical duplicate
        dup_match = self.find_logical_duplicate(
            vendor_name=invoice_data.vendor_name,
            invoice_number=invoice_data.invoice_number,
            total_amount=invoice_data.total_amount,
            invoice_date=invoice_data.invoice_date,
            currency=invoice_data.currency,
            exclude_file_hash=file_hash,
        )

        is_dup = 1 if dup_match else 0
        dup_of_id = dup_match["id"] if dup_match else None
        dup_reason = None

        if dup_match:
            tot_str = f" (${dup_match['total_amount']:.2f})" if dup_match.get("total_amount") is not None else ""
            dup_reason = (
                f"Suspected duplicate of Invoice #{dup_match['id']} "
                f"({dup_match.get('invoice_number', 'N/A')}) from {dup_match.get('vendor_name', 'Unknown')}{tot_str}."
            )
            status = "suspected_duplicate"
            invoice_data.needs_review = True
            invoice_data.is_duplicate = True
            invoice_data.duplicate_of_id = dup_of_id
            invoice_data.duplicate_reason = dup_reason
            if dup_reason not in invoice_data.extraction_notes:
                invoice_data.extraction_notes.append(f"⚠️ {dup_reason}")
        else:
            status = "needs_review" if invoice_data.needs_review else "processed"

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert or replace invoice
            cursor.execute(
                """
                INSERT INTO invoices (
                    invoice_number, vendor_name, invoice_date, due_date,
                    customer_name, subtotal, tax_amount, total_amount,
                    currency, payment_status, source_file_path, file_hash,
                    raw_text, confidence_scores, extraction_notes, status,
                    is_duplicate, duplicate_of_id, duplicate_reason,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                    invoice_number = excluded.invoice_number,
                    vendor_name = excluded.vendor_name,
                    invoice_date = excluded.invoice_date,
                    due_date = excluded.due_date,
                    customer_name = excluded.customer_name,
                    subtotal = excluded.subtotal,
                    tax_amount = excluded.tax_amount,
                    total_amount = excluded.total_amount,
                    currency = excluded.currency,
                    payment_status = excluded.payment_status,
                    source_file_path = excluded.source_file_path,
                    raw_text = excluded.raw_text,
                    confidence_scores = excluded.confidence_scores,
                    extraction_notes = excluded.extraction_notes,
                    status = excluded.status,
                    is_duplicate = excluded.is_duplicate,
                    duplicate_of_id = excluded.duplicate_of_id,
                    duplicate_reason = excluded.duplicate_reason,
                    updated_at = excluded.updated_at;
                """,
                (
                    invoice_data.invoice_number,
                    invoice_data.vendor_name,
                    invoice_data.invoice_date,
                    invoice_data.due_date,
                    invoice_data.customer_name,
                    invoice_data.subtotal,
                    invoice_data.tax_amount,
                    invoice_data.total_amount,
                    invoice_data.currency,
                    invoice_data.payment_status,
                    source_file_path,
                    file_hash,
                    invoice_data.raw_text,
                    json.dumps(invoice_data.confidence_scores),
                    json.dumps(invoice_data.extraction_notes),
                    status,
                    is_dup,
                    dup_of_id,
                    dup_reason,
                    now,
                    now,
                ),
            )

            # Retrieve invoice ID
            cursor.execute("SELECT id FROM invoices WHERE file_hash = ?", (file_hash,))
            row = cursor.fetchone()
            invoice_id = row["id"]

            # Replace line items
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            for item in invoice_data.line_items:
                cursor.execute(
                    """
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (invoice_id, item.description, item.quantity, item.unit_price, item.amount),
                )

            # Update file_metadata
            file_name = Path(source_file_path).name
            file_size = Path(source_file_path).stat().st_size if Path(source_file_path).exists() else 0
            cursor.execute(
                """
                INSERT INTO file_metadata (file_hash, file_name, file_size, mime_type, first_seen_at, last_processed_at)
                VALUES (?, ?, ?, 'application/pdf', ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                    file_name = excluded.file_name,
                    last_processed_at = excluded.last_processed_at;
                """,
                (file_hash, file_name, file_size, now, now),
            )

            return invoice_id

    def update_invoice(self, invoice_id: int, fields: Dict[str, Any]) -> bool:
        """Updates specific fields of an invoice (e.g., during manual verification)."""
        if not fields:
            return False

        allowed_fields = {
            "invoice_number", "vendor_name", "invoice_date", "due_date",
            "customer_name", "subtotal", "tax_amount", "total_amount",
            "currency", "payment_status", "status"
        }

        updates = []
        values = []
        for key, value in fields.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(get_current_time_str())
        values.append(invoice_id)

        sql = f"UPDATE invoices SET {', '.join(updates)} WHERE id = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(values))
            updated = cursor.rowcount > 0

        # Synchronize updated invoice with vector store
        if updated:
            try:
                from core.vector_store import vector_store
                full_inv = self.get_invoice_by_id(invoice_id)
                if full_inv:
                    vector_store.index_invoice(full_inv)
            except Exception as e:
                logger.warning(f"Could not update vector entries for invoice #{invoice_id}: {e}")

        return updated

    def delete_invoice(self, invoice_id: int) -> Optional[str]:
        """
        Deletes an invoice and its line items.
        Returns the file_hash of the deleted invoice (for vector store cleanup), or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_hash FROM invoices WHERE id = ?", (invoice_id,))
            row = cursor.fetchone()
            if not row:
                return None
            file_hash = row["file_hash"]

            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

        # Synchronize deletion with vector store
        try:
            from core.vector_store import vector_store
            vector_store.delete_by_invoice_id(invoice_id)
        except Exception as e:
            logger.warning(f"Could not delete vector entries for invoice #{invoice_id}: {e}")

        return file_hash

    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves full invoice details including line items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            inv_row = cursor.fetchone()
            if not inv_row:
                return None

            inv = dict(inv_row)
            cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            items = [dict(r) for r in cursor.fetchall()]
            inv["line_items"] = items

            # Parse JSON fields safely
            try:
                inv["confidence_scores"] = json.loads(inv["confidence_scores"] or "{}")
            except Exception:
                inv["confidence_scores"] = {}
            try:
                inv["extraction_notes"] = json.loads(inv["extraction_notes"] or "[]")
            except Exception:
                inv["extraction_notes"] = []

            return inv

    def get_all_invoices(
        self,
        vendor: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        include_duplicates: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retrieves invoices filtered by various parameters."""
        query = "SELECT * FROM invoices WHERE 1=1"
        params: List[Any] = []

        if vendor:
            query += " AND vendor_name LIKE ?"
            params.append(f"%{vendor}%")
        if date_from:
            query += " AND invoice_date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND invoice_date <= ?"
            params.append(date_to)
        if status and status != "All":
            query += " AND status = ?"
            params.append(status)
        elif not include_duplicates:
            query += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        if search:
            query += " AND (invoice_number LIKE ? OR vendor_name LIKE ? OR raw_text LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY invoice_date DESC, id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return [dict(r) for r in cursor.fetchall()]

    # =========================================================================
    # Financial Analytics & Aggregations
    # =========================================================================

    def get_total_expenses(self, include_duplicates: bool = False) -> List[Dict[str, Any]]:
        """
        Calculates total spending grouped by currency.
        Prevents adding different currencies together!
        Excludes suspected duplicates by default to prevent silent financial inflation.
        """
        where_clause = "WHERE total_amount IS NOT NULL"
        if not include_duplicates:
            where_clause += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT currency, COUNT(*) as invoice_count, SUM(total_amount) as total_spent
                FROM invoices
                {where_clause}
                GROUP BY currency
                ORDER BY total_spent DESC;
                """
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_expenses_by_vendor(self, include_duplicates: bool = False) -> List[Dict[str, Any]]:
        """Calculates total spending grouped by vendor and currency."""
        where_clause = "WHERE total_amount IS NOT NULL"
        if not include_duplicates:
            where_clause += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT COALESCE(vendor_name, 'Unknown') as vendor,
                       currency,
                       COUNT(*) as invoice_count,
                       SUM(total_amount) as total_spent
                FROM invoices
                {where_clause}
                GROUP BY vendor_name, currency
                ORDER BY total_spent DESC;
                """
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_monthly_expenses(self, include_duplicates: bool = False) -> List[Dict[str, Any]]:
        """Calculates monthly spending grouped by YYYY-MM and currency."""
        where_clause = "WHERE invoice_date IS NOT NULL AND total_amount IS NOT NULL"
        if not include_duplicates:
            where_clause += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT SUBSTR(invoice_date, 1, 7) as month,
                       currency,
                       COUNT(*) as invoice_count,
                       SUM(total_amount) as total_spent
                FROM invoices
                {where_clause}
                GROUP BY SUBSTR(invoice_date, 1, 7), currency
                ORDER BY month ASC;
                """
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_quarterly_expenses(self, include_duplicates: bool = False) -> List[Dict[str, Any]]:
        """Calculates quarterly spending grouped by quarter and currency."""
        where_clause = "WHERE invoice_date IS NOT NULL AND total_amount IS NOT NULL"
        if not include_duplicates:
            where_clause += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT SUBSTR(invoice_date, 1, 4) || '-Q' || ((CAST(SUBSTR(invoice_date, 6, 2) AS INTEGER) - 1) / 3 + 1) as quarter,
                       currency,
                       COUNT(*) as invoice_count,
                       SUM(total_amount) as total_spent
                FROM invoices
                {where_clause}
                GROUP BY quarter, currency
                ORDER BY quarter ASC;
                """
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_invoice_counts(self) -> Dict[str, int]:
        """Returns summary counts of invoices by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'processed' AND is_duplicate = 0 THEN 1 ELSE 0 END) as processed,
                    SUM(CASE WHEN status = 'needs_review' AND is_duplicate = 0 THEN 1 ELSE 0 END) as needs_review,
                    SUM(CASE WHEN status = 'verified' AND is_duplicate = 0 THEN 1 ELSE 0 END) as verified,
                    SUM(CASE WHEN is_duplicate = 1 OR status = 'suspected_duplicate' THEN 1 ELSE 0 END) as suspected_duplicate
                FROM invoices;
                """
            )
            row = cursor.fetchone()
            if row:
                return {
                    "total": row["total"] or 0,
                    "processed": row["processed"] or 0,
                    "needs_review": row["needs_review"] or 0,
                    "verified": row["verified"] or 0,
                    "suspected_duplicate": row["suspected_duplicate"] or 0,
                }
            return {"total": 0, "processed": 0, "needs_review": 0, "verified": 0, "suspected_duplicate": 0}

    def get_highest_value_invoices(self, limit: int = 5, include_duplicates: bool = False) -> List[Dict[str, Any]]:
        """Returns the top highest value invoices."""
        where_clause = "WHERE total_amount IS NOT NULL"
        if not include_duplicates:
            where_clause += " AND is_duplicate = 0 AND status != 'suspected_duplicate'"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT id, invoice_number, vendor_name, invoice_date, total_amount, currency, status
                FROM invoices
                {where_clause}
                ORDER BY total_amount DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]
            return [dict(r) for r in cursor.fetchall()]

    def get_recently_processed_invoices(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recently created or processed invoices."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, invoice_number, vendor_name, invoice_date, total_amount, currency, status, created_at
                FROM invoices
                ORDER BY id DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]

    # =========================================================================
    # Audit & Error Logging
    # =========================================================================

    def log_processing_record(self, record: ProcessingRecord) -> None:
        """Records a file processing event in the audit trail."""
        now = record.processed_at or get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO processing_records (
                    file_name, file_path, file_hash, file_size, status,
                    error_message, duration_sec, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.file_name,
                    record.file_path,
                    record.file_hash,
                    record.file_size,
                    record.status,
                    record.error_message,
                    record.duration_sec,
                    now,
                ),
            )

    def log_error(
        self,
        stage: str,
        error_type: str,
        error_message: str,
        file_name: Optional[str] = None,
        file_hash: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Logs an error into processing_errors."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO processing_errors (
                    file_name, file_hash, stage, error_type, error_message, stack_trace, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (file_name, file_hash, stage, error_type, error_message, stack_trace, now),
            )

    def get_processing_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent processing log entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM processing_records
                ORDER BY id DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]

    # =========================================================================
    # Exchange Rate Caching & User Settings
    # =========================================================================

    def get_cached_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: str,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a cached exchange rate for a currency pair on a specific date or 'latest'."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM exchange_rate_cache
                WHERE from_currency = ? AND to_currency = ? AND rate_date = ?;
                """,
                (from_currency.upper(), to_currency.upper(), rate_date),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_cached_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate_date: str,
        effective_date: str,
        rate: float,
        rate_decimal: str,
        source: str,
    ) -> None:
        """Saves or updates an exchange rate in the SQLite cache."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO exchange_rate_cache (
                    from_currency, to_currency, rate_date, effective_date,
                    rate, rate_decimal, source, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(from_currency, to_currency, rate_date) DO UPDATE SET
                    effective_date = excluded.effective_date,
                    rate = excluded.rate,
                    rate_decimal = excluded.rate_decimal,
                    source = excluded.source,
                    fetched_at = excluded.fetched_at;
                """,
                (
                    from_currency.upper(),
                    to_currency.upper(),
                    rate_date,
                    effective_date,
                    rate,
                    rate_decimal,
                    source,
                    now,
                ),
            )

    def get_all_cached_rates(self) -> List[Dict[str, Any]]:
        """Returns all cached exchange rate rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM exchange_rate_cache ORDER BY rate_date DESC, id DESC;")
            return [dict(r) for r in cursor.fetchall()]

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a user or application setting."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Saves a user or application setting."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at;
                """,
                (key, value, now),
            )

    # =========================================================================
    # GMAIL RPA AUTOMATION HELPERS
    # =========================================================================

    def record_gmail_account(self, email: str) -> None:
        """Records or updates a connected Gmail account as active."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Deactivate other accounts to maintain a clean single active connection
            cursor.execute("UPDATE gmail_accounts SET is_active = 0 WHERE email != ?;", (email,))
            cursor.execute(
                """
                INSERT INTO gmail_accounts (email, is_active, connected_at, last_synced_at)
                VALUES (?, 1, ?, NULL)
                ON CONFLICT(email) DO UPDATE SET
                    is_active = 1,
                    connected_at = excluded.connected_at;
                """,
                (email, now),
            )

    def get_active_gmail_account(self) -> Optional[Dict[str, Any]]:
        """Returns the currently active Gmail account, if any."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gmail_accounts WHERE is_active = 1 ORDER BY id DESC LIMIT 1;")
            row = cursor.fetchone()
            return dict(row) if row else None

    def disconnect_gmail_account(self, email: Optional[str] = None) -> None:
        """Marks Gmail account(s) as disconnected / inactive."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if email:
                cursor.execute("UPDATE gmail_accounts SET is_active = 0 WHERE email = ?;", (email,))
            else:
                cursor.execute("UPDATE gmail_accounts SET is_active = 0;")

    def update_gmail_last_synced(self, email: str, timestamp: Optional[str] = None) -> None:
        """Updates the last_synced_at timestamp for a Gmail account."""
        now = timestamp or get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE gmail_accounts SET last_synced_at = ? WHERE email = ?;",
                (now, email),
            )

    def create_sync_history(self) -> int:
        """Initializes a new sync history record with 'running' status and returns its id."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO gmail_sync_history (started_at, status, messages_scanned, attachments_found, invoices_imported, duplicates_skipped, failed_count)
                VALUES (?, 'running', 0, 0, 0, 0, 0);
                """,
                (now,),
            )
            return cursor.lastrowid

    def update_sync_history(
        self,
        sync_id: int,
        status: str,
        messages_scanned: int = 0,
        attachments_found: int = 0,
        invoices_imported: int = 0,
        duplicates_skipped: int = 0,
        failed_count: int = 0,
        error_details: Optional[str] = None,
    ) -> None:
        """Updates a sync history record upon completion or failure."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE gmail_sync_history
                SET completed_at = ?,
                    status = ?,
                    messages_scanned = ?,
                    attachments_found = ?,
                    invoices_imported = ?,
                    duplicates_skipped = ?,
                    failed_count = ?,
                    error_details = ?
                WHERE id = ?;
                """,
                (
                    now,
                    status,
                    messages_scanned,
                    attachments_found,
                    invoices_imported,
                    duplicates_skipped,
                    failed_count,
                    error_details,
                    sync_id,
                ),
            )

    def get_recent_sync_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the most recent Gmail synchronization logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM gmail_sync_history ORDER BY id DESC LIMIT ?;",
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]

    def is_gmail_message_processed(self, message_id: str) -> bool:
        """Checks if a Gmail message has already been processed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM gmail_processed_messages WHERE message_id = ? LIMIT 1;",
                (message_id,),
            )
            return cursor.fetchone() is not None

    def record_processed_message(
        self,
        message_id: str,
        thread_id: Optional[str] = None,
        sender: Optional[str] = None,
        subject: Optional[str] = None,
        date: Optional[str] = None,
    ) -> None:
        """Records a scanned Gmail message in the database."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO gmail_processed_messages
                (message_id, thread_id, sender, subject, date, processed_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (message_id, thread_id, sender, subject, date, now),
            )

    def is_gmail_attachment_processed(
        self,
        message_id: str,
        attachment_id: str,
        file_hash: Optional[str] = None,
    ) -> bool:
        """Checks if an attachment from a Gmail message has already been processed or downloaded."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM gmail_processed_attachments
                WHERE message_id = ? AND attachment_id = ?
                LIMIT 1;
                """,
                (message_id, attachment_id),
            )
            if cursor.fetchone():
                return True
            if file_hash:
                cursor.execute(
                    "SELECT 1 FROM gmail_processed_attachments WHERE file_hash = ? LIMIT 1;",
                    (file_hash,),
                )
                if cursor.fetchone():
                    return True
            return False

    def record_processed_attachment(
        self,
        message_id: str,
        attachment_id: str,
        file_name: str,
        file_hash: Optional[str] = None,
        invoice_id: Optional[int] = None,
        download_status: str = "downloaded",
    ) -> None:
        """Records a downloaded or skipped Gmail attachment."""
        now = get_current_time_str()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO gmail_processed_attachments
                (message_id, attachment_id, file_name, file_hash, invoice_id, download_status, downloaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id, attachment_id) DO UPDATE SET
                    file_hash = excluded.file_hash,
                    invoice_id = excluded.invoice_id,
                    download_status = excluded.download_status,
                    downloaded_at = excluded.downloaded_at;
                """,
                (message_id, attachment_id, file_name, file_hash, invoice_id, download_status, now),
            )


# Global database singleton
db = DatabaseManager()

