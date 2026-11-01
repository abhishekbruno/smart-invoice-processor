import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from config.settings import settings
from utils.helpers import clean_extracted_text, format_currency_amount


@dataclass
class DocumentChunk:
    """Represents a text chunk extracted from an invoice for vector indexing."""
    chunk_id: str
    invoice_id: int
    invoice_number: str
    source_filename: str
    page_number: int
    vendor_name: str
    content: str
    file_hash: str
    chunk_type: str = "content"  # "summary", "line_items", "content"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_chroma_metadata(self) -> Dict[str, Any]:
        """Returns flat metadata compatible with ChromaDB."""
        meta = {
            "invoice_id": self.invoice_id,
            "invoice_number": self.invoice_number or "N/A",
            "source_filename": self.source_filename,
            "page_number": self.page_number,
            "vendor_name": self.vendor_name or "Unknown",
            "file_hash": self.file_hash,
            "chunk_type": self.chunk_type,
        }
        for k, v in self.metadata.items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
            elif v is not None:
                meta[k] = str(v)
        return meta


class DocumentChunker:
    """
    Intelligently splits invoice documents into contextual chunks
    preserving document metadata, line items, and financial headers.
    """

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_invoice(
        self,
        invoice_record: Dict[str, Any],
        raw_text: Optional[str] = None,
        pages_data: Optional[List[Dict[str, Any]]] = None,
    ) -> List[DocumentChunk]:
        """
        Creates semantic chunks for an invoice record:
        1. High-density invoice summary chunk (vendor, dates, amounts, status).
        2. Contextual line-item chunks (with line item details, quantities, unit prices).
        3. Page-level content chunks with sliding window for multi-page or long texts.
        """
        invoice_id = int(invoice_record.get("id", 0))
        file_hash = str(invoice_record.get("file_hash", ""))
        inv_number = str(invoice_record.get("invoice_number") or "N/A")
        vendor_name = str(invoice_record.get("vendor_name") or "Unknown")
        source_path = str(invoice_record.get("source_file_path", ""))
        filename = Path(source_path).name if source_path else "invoice.pdf"
        currency = str(invoice_record.get("currency") or "USD")

        chunks: List[DocumentChunk] = []

        # ---------------------------------------------------------------------
        # 1. Invoice Summary Chunk
        # ---------------------------------------------------------------------
        summary_text = self._build_summary_chunk_text(invoice_record)
        summary_id = f"{file_hash[:16]}_summary_1_0"
        chunks.append(
            DocumentChunk(
                chunk_id=summary_id,
                invoice_id=invoice_id,
                invoice_number=inv_number,
                source_filename=filename,
                page_number=1,
                vendor_name=vendor_name,
                content=summary_text,
                file_hash=file_hash,
                chunk_type="summary",
                metadata={
                    "total_amount": float(invoice_record.get("total_amount") or 0.0),
                    "currency": currency,
                    "invoice_date": str(invoice_record.get("invoice_date") or ""),
                    "status": str(invoice_record.get("status") or ""),
                },
            )
        )

        # ---------------------------------------------------------------------
        # 2. Line Items Chunks
        # ---------------------------------------------------------------------
        line_items = invoice_record.get("line_items", [])
        if line_items:
            # Group line items into chunks of up to 6 items to avoid huge lists
            batch_size = 6
            for idx in range(0, len(line_items), batch_size):
                batch = line_items[idx : idx + batch_size]
                items_text_lines = [
                    f"Line Items for Invoice #{inv_number} (Vendor: {vendor_name}, Currency: {currency}):"
                ]
                for item in batch:
                    desc = item.get("description", "Item")
                    qty = item.get("quantity", 1.0)
                    unit = item.get("unit_price", 0.0)
                    amt = item.get("amount", 0.0)
                    amt_str = format_currency_amount(amt, currency)
                    unit_str = format_currency_amount(unit, currency)
                    items_text_lines.append(
                        f"• {desc} | Quantity: {qty} | Unit Price: {unit_str} | Total: {amt_str}"
                    )

                items_content = "\n".join(items_text_lines)
                batch_idx = idx // batch_size
                chunk_id = f"{file_hash[:16]}_lineitems_1_{batch_idx}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        invoice_id=invoice_id,
                        invoice_number=inv_number,
                        source_filename=filename,
                        page_number=1,
                        vendor_name=vendor_name,
                        content=items_content,
                        file_hash=file_hash,
                        chunk_type="line_items",
                        metadata={
                            "currency": currency,
                            "items_count": len(batch),
                        },
                    )
                )

        # ---------------------------------------------------------------------
        # 3. Document Content / Page Chunks
        # ---------------------------------------------------------------------
        doc_text = raw_text or invoice_record.get("raw_text") or ""
        cleaned = clean_extracted_text(doc_text)

        if pages_data:
            # Page-aware chunking
            for page in pages_data:
                p_num = page.get("page_number", 1)
                p_text = clean_extracted_text(page.get("text", ""))
                if not p_text:
                    continue
                page_chunks = self._split_text_with_overlap(p_text)
                for c_idx, c_text in enumerate(page_chunks):
                    chunk_id = f"{file_hash[:16]}_content_{p_num}_{c_idx}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            invoice_id=invoice_id,
                            invoice_number=inv_number,
                            source_filename=filename,
                            page_number=p_num,
                            vendor_name=vendor_name,
                            content=c_text,
                            file_hash=file_hash,
                            chunk_type="content",
                            metadata={"page": p_num},
                        )
                    )
        elif cleaned:
            # Single-pass sliding window
            text_chunks = self._split_text_with_overlap(cleaned)
            for c_idx, c_text in enumerate(text_chunks):
                chunk_id = f"{file_hash[:16]}_content_1_{c_idx}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        invoice_id=invoice_id,
                        invoice_number=inv_number,
                        source_filename=filename,
                        page_number=1,
                        vendor_name=vendor_name,
                        content=c_text,
                        file_hash=file_hash,
                        chunk_type="content",
                    )
                )

        return chunks

    def _build_summary_chunk_text(self, inv: Dict[str, Any]) -> str:
        """Constructs an information-dense summary chunk."""
        currency = inv.get("currency") or "USD"
        inv_num = inv.get("invoice_number") or "Unknown"
        vendor = inv.get("vendor_name") or "Unknown"
        inv_date = inv.get("invoice_date") or "N/A"
        due_date = inv.get("due_date") or "N/A"
        customer = inv.get("customer_name") or "N/A"
        subtotal = format_currency_amount(inv.get("subtotal"), currency)
        tax = format_currency_amount(inv.get("tax_amount"), currency)
        total = format_currency_amount(inv.get("total_amount"), currency)
        status = inv.get("payment_status") or "Unspecified"

        lines = [
            f"Invoice Document Summary: #{inv_num}",
            f"Vendor / Issuer: {vendor}",
            f"Customer / Billed To: {customer}",
            f"Invoice Date: {inv_date}",
            f"Payment Due Date: {due_date}",
            f"Subtotal: {subtotal}",
            f"Tax Amount: {tax}",
            f"Grand Total Amount: {total} ({currency})",
            f"Payment Status: {status}",
        ]
        return "\n".join(lines)

    def _split_text_with_overlap(self, text: str) -> List[str]:
        """
        Splits text into chunks of roughly `chunk_size` characters
        with `chunk_overlap`, breaking at whitespace / sentence boundaries.
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Try to break at a newline or period near the end
            break_point = -1
            for separator in ["\n\n", "\n", ". ", " "]:
                idx = text.rfind(separator, start + (self.chunk_size // 2), end)
                if idx != -1:
                    break_point = idx + len(separator)
                    break

            if break_point == -1 or break_point <= start:
                break_point = end

            chunk = text[start:break_point].strip()
            if chunk:
                chunks.append(chunk)

            # Advance with overlap
            start = max(start + 1, break_point - self.chunk_overlap)

        return chunks


# Global chunker singleton
document_chunker = DocumentChunker()

