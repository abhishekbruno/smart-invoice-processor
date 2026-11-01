import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from api.schemas.common import APIResponse, PaginatedResponse
from api.schemas.invoice import (
    InvoiceDetailResponse,
    InvoiceListItem,
    InvoiceUpdateRequest,
    InvoiceUploadResponse,
    LineItemResponse,
)
from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from core.folder_monitor import InvoiceProcessingPipeline
from core.vector_store import vector_store
from utils.logger import logger
from utils.validators import sanitize_filename, validate_pdf_file

router = APIRouter(prefix="/invoices", tags=["Invoices & Documents"])


def _format_invoice_item(inv: dict, target_currency: str = "INR") -> InvoiceListItem:
    """Helper to convert database invoice row to API item with converted currency amount."""
    orig_amt = inv.get("total_amount") or 0.0
    orig_curr = inv.get("currency") or "USD"

    conv_res = currency_service.convert_currency(
        amount=orig_amt,
        from_currency=orig_curr,
        to_currency=target_currency,
        date=inv.get("invoice_date"),
        mode="historical",
    )

    return InvoiceListItem(
        id=inv["id"],
        invoice_number=inv.get("invoice_number"),
        vendor_name=inv.get("vendor_name"),
        invoice_date=inv.get("invoice_date"),
        due_date=inv.get("due_date"),
        total_amount=orig_amt,
        currency=orig_curr,
        converted_amount=float(conv_res.converted_amount),
        converted_currency=target_currency,
        status=inv.get("status", "processed"),
        is_duplicate=bool(inv.get("is_duplicate")),
        duplicate_of_id=inv.get("duplicate_of_id"),
        duplicate_reason=inv.get("duplicate_reason"),
        created_at=inv.get("created_at", ""),
    )


# =============================================================================
# 1. Invoice Listing & Pagination
# =============================================================================

@router.get("", response_model=PaginatedResponse[InvoiceListItem])
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    vendor: Optional[str] = Query(None, description="Filter by vendor name substring"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (processed, needs_review, verified, suspected_duplicate)"),
    currency_filter: Optional[str] = Query(None, alias="currency", description="Filter by original currency code"),
    include_duplicates: bool = Query(True, description="Whether to include suspected duplicate records"),
):
    """Retrieves paginated invoices with optional filtering and automatic target currency conversion."""
    pref_curr = db.get_setting("preferred_display_currency", "INR")
    all_invoices = db.get_all_invoices(include_duplicates=include_duplicates)

    filtered = []
    for inv in all_invoices:
        if vendor and vendor.lower() not in (inv.get("vendor_name") or "").lower():
            continue
        if status_filter and inv.get("status") != status_filter:
            continue
        if currency_filter and inv.get("currency") != currency_filter.upper():
            continue
        filtered.append(inv)

    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items = filtered[start_idx:end_idx]

    formatted_items = [_format_invoice_item(item, target_currency=pref_curr) for item in page_items]
    total_pages = max(1, (total + limit - 1) // limit)

    return PaginatedResponse(
        items=formatted_items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


# =============================================================================
# 2. Duplicate Review Listing (BEFORE /{id} to prevent path collision)
# =============================================================================

@router.get("/duplicates", response_model=List[InvoiceListItem])
def list_duplicate_invoices():
    """Lists all invoices flagged as duplicates or suspected duplicates requiring operator review."""
    pref_curr = db.get_setting("preferred_display_currency", "INR")
    all_invoices = db.get_all_invoices(include_duplicates=True)
    duplicates = [inv for inv in all_invoices if inv.get("is_duplicate") or inv.get("status") == "suspected_duplicate"]
    return [_format_invoice_item(item, target_currency=pref_curr) for item in duplicates]


# =============================================================================
# 3. Single Invoice Details & Document Access
# =============================================================================

@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice_detail(invoice_id: int):
    """Retrieves full invoice details including extracted line items and extraction notes."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    pref_curr = db.get_setting("preferred_display_currency", "INR")
    formatted_base = _format_invoice_item(inv, target_currency=pref_curr)

    raw_items = inv.get("line_items", [])
    line_items = [
        LineItemResponse(
            id=item.get("id"),
            description=item.get("description", ""),
            quantity=item.get("quantity", 1.0),
            unit_price=item.get("unit_price", 0.0),
            amount=item.get("amount", 0.0),
        )
        for item in raw_items
    ]

    return InvoiceDetailResponse(
        **formatted_base.model_dump(),
        customer_name=inv.get("customer_name"),
        subtotal=inv.get("subtotal"),
        tax_amount=inv.get("tax_amount"),
        payment_status=inv.get("payment_status"),
        source_file_path=inv.get("source_file_path"),
        file_hash=inv.get("file_hash", ""),
        confidence_scores=inv.get("confidence_scores", {}),
        extraction_notes=inv.get("extraction_notes", []),
        line_items=line_items,
        updated_at=inv.get("updated_at"),
    )


@router.get("/{invoice_id}/document")
def download_invoice_document(invoice_id: int):
    """Streams the original source PDF invoice file for in-browser or in-app preview."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    file_path_str = inv.get("source_file_path")
    if not file_path_str:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No source document associated with this record")

    pdf_path = Path(file_path_str)
    # If moved or relative, attempt resolution
    if not pdf_path.exists():
        fallback_path = settings.BASE_DIR / pdf_path
        if fallback_path.exists():
            pdf_path = fallback_path
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source PDF file is missing from local disk")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )


# =============================================================================
# 4. Upload & Processing
# =============================================================================

@router.post("/upload", response_model=InvoiceUploadResponse)
async def upload_invoice(file: UploadFile = File(...)):
    """
    Accepts an invoice PDF upload, validates structure, prevents duplicates,
    runs automated extraction, and catalogs into SQLite and ChromaDB.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF invoice files (.pdf) are supported.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty (0 bytes).")

    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB} MB.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF file. Header missing %PDF- magic bytes.")

    safe_name = sanitize_filename(file.filename)
    dest_path = settings.INVOICE_WATCH_DIR / safe_name

    # Handle local naming collisions
    counter = 1
    stem = Path(safe_name).stem
    while dest_path.exists():
        dest_path = settings.INVOICE_WATCH_DIR / f"{stem}_{counter}.pdf"
        counter += 1

    try:
        dest_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save uploaded file: {str(e)}")

    # Ingest through InvoiceProcessingPipeline
    result = InvoiceProcessingPipeline.process_file(dest_path, force_reprocess=False, archive_copy=True)
    file_hash = result.get("file_hash")

    inv_id = None
    is_dup = False
    dup_reason = None

    if file_hash:
        existing = db.get_invoice_by_hash(file_hash)
        if existing:
            inv_id = existing.get("id")
            is_dup = bool(existing.get("is_duplicate"))
            dup_reason = existing.get("duplicate_reason")

    if result.get("status") == "duplicate":
        is_dup = True
        dup_reason = result.get("message", "File hash already exists in database.")

    return InvoiceUploadResponse(
        status=result.get("status", "success"),
        invoice_id=inv_id,
        file_name=dest_path.name,
        file_hash=file_hash,
        is_duplicate=is_dup,
        duplicate_reason=dup_reason,
        message="Invoice uploaded and cataloged successfully." if result.get("status") in ("success", "needs_review") else result.get("error", "Processed with notice."),
    )


# =============================================================================
# 5. Modification, Verification & Reprocessing Actions
# =============================================================================

@router.patch("/{invoice_id}", response_model=APIResponse[dict])
def update_invoice(invoice_id: int, payload: InvoiceUpdateRequest):
    """Updates editable invoice fields (vendor, invoice number, dates, amounts, status)."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        return APIResponse(success=True, message="No changes provided", data={"invoice_id": invoice_id})

    # Apply database updates
    set_clauses = []
    params = []
    for col, val in updates.items():
        set_clauses.append(f"{col} = ?")
        params.append(val)
    params.append(invoice_id)

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE invoices SET {', '.join(set_clauses)}, updated_at = datetime('now') WHERE id = ?;", tuple(params))

    # Re-audit duplicate flags if vendor/number/total was updated
    if any(k in updates for k in ("vendor_name", "invoice_number", "total_amount")):
        db.audit_and_flag_duplicates()

    return APIResponse(success=True, message=f"Invoice #{invoice_id} updated successfully", data={"invoice_id": invoice_id, "updated_fields": list(updates.keys())})


@router.post("/{invoice_id}/verify", response_model=APIResponse[dict])
def verify_invoice(invoice_id: int):
    """Marks an invoice as verified by an operator."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE invoices SET status = 'verified', updated_at = datetime('now') WHERE id = ?;", (invoice_id,))

    return APIResponse(success=True, message=f"Invoice #{invoice_id} marked as verified", data={"invoice_id": invoice_id, "status": "verified"})


@router.post("/{invoice_id}/mark-genuine", response_model=APIResponse[dict])
def mark_invoice_genuine(invoice_id: int):
    """Reclassifies a suspected duplicate as a verified genuine invoice, including it in financial spending."""
    success = db.mark_invoice_genuine(invoice_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    return APIResponse(success=True, message=f"Invoice #{invoice_id} cleared and confirmed as genuine", data={"invoice_id": invoice_id, "is_duplicate": False, "status": "verified"})


@router.post("/{invoice_id}/confirm-duplicate", response_model=APIResponse[dict])
def confirm_invoice_duplicate(invoice_id: int):
    """Confirms that an invoice is a duplicate, ensuring it is excluded from financial analytics."""
    success = db.mark_invoice_duplicate(invoice_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    return APIResponse(success=True, message=f"Invoice #{invoice_id} confirmed as duplicate", data={"invoice_id": invoice_id, "is_duplicate": True, "status": "suspected_duplicate"})


@router.post("/{invoice_id}/reprocess", response_model=APIResponse[dict])
def reprocess_invoice(invoice_id: int):
    """Forces re-parsing and re-indexing of an invoice document."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    file_path = Path(inv["source_file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source file missing on disk")

    res = InvoiceProcessingPipeline.process_file(file_path, force_reprocess=True, archive_copy=False)
    return APIResponse(success=True, message=f"Reprocessed invoice #{invoice_id}", data=res)


@router.delete("/{invoice_id}", response_model=APIResponse[dict])
def delete_invoice(invoice_id: int):
    """Deletes an invoice record and removes its vector chunks from ChromaDB."""
    inv = db.get_invoice_by_id(invoice_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice #{invoice_id} not found")

    file_hash = inv.get("file_hash")

    # Remove from ChromaDB
    try:
        vector_store.delete_invoice_chunks(invoice_id)
    except Exception as e:
        logger.warning(f"Error removing vector chunks for #{invoice_id}: {e}")

    # Remove from SQLite
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?;", (invoice_id,))
        cursor.execute("DELETE FROM invoices WHERE id = ?;", (invoice_id,))

    return APIResponse(success=True, message=f"Invoice #{invoice_id} deleted successfully", data={"invoice_id": invoice_id, "file_hash": file_hash})

