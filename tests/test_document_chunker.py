import pytest
from core.document_chunker import DocumentChunk, DocumentChunker


def test_chunker_creates_summary_and_items():
    chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)

    sample_record = {
        "id": 101,
        "invoice_number": "INV-2024-TEST",
        "vendor_name": "Test Cloud Services",
        "customer_name": "Acme Inc",
        "invoice_date": "2024-04-10",
        "due_date": "2024-05-10",
        "subtotal": 500.0,
        "tax_amount": 50.0,
        "total_amount": 550.0,
        "currency": "USD",
        "payment_status": "PAID",
        "source_file_path": "data/invoices/test_cloud.pdf",
        "file_hash": "a1b2c3d4e5f67890123456789abcdef0",
        "line_items": [
            {"description": "VM Compute Instance", "quantity": 2.0, "unit_price": 150.0, "amount": 300.0},
            {"description": "Block Storage 1TB", "quantity": 1.0, "unit_price": 100.0, "amount": 100.0},
            {"description": "Load Balancer", "quantity": 1.0, "unit_price": 100.0, "amount": 100.0},
        ],
        "raw_text": "This is raw document text content from the original PDF file.\nIt contains multiple lines.",
    }

    chunks = chunker.chunk_invoice(sample_record)

    assert len(chunks) >= 2
    # Verify summary chunk
    summary_chunk = next((c for c in chunks if c.chunk_type == "summary"), None)
    assert summary_chunk is not None
    assert "INV-2024-TEST" in summary_chunk.content
    assert "Test Cloud Services" in summary_chunk.content
    assert "$550.00" in summary_chunk.content
    assert summary_chunk.invoice_id == 101
    assert summary_chunk.source_filename == "test_cloud.pdf"

    # Verify line items chunk
    item_chunk = next((c for c in chunks if c.chunk_type == "line_items"), None)
    assert item_chunk is not None
    assert "VM Compute Instance" in item_chunk.content
    assert "Block Storage 1TB" in item_chunk.content
    assert item_chunk.metadata["currency"] == "USD"


def test_chunker_handles_empty_line_items_and_short_text():
    chunker = DocumentChunker()
    sparse_record = {
        "id": 202,
        "invoice_number": "SPARSE-001",
        "vendor_name": "Simple Vendor",
        "total_amount": 10.0,
        "currency": "EUR",
        "file_hash": "0123456789abcdef0123456789abcdef",
        "source_file_path": "simple.pdf",
        "line_items": [],
        "raw_text": "Simple short receipt text.",
    }

    chunks = chunker.chunk_invoice(sparse_record)
    assert len(chunks) >= 1
    # Check stable ID format
    assert chunks[0].chunk_id.startswith("0123456789abcdef_")
    assert chunks[0].to_chroma_metadata()["invoice_id"] == 202

