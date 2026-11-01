import pytest
from pathlib import Path
from core.invoice_parser import InvoiceParser
from core.pdf_extractor import ExtractedDocument, PageData


def test_parser_extracts_all_fields_from_text():
    parser = InvoiceParser()
    sample_text = (
        "Acme Corp Inc.\n"
        "123 Industrial Rd\n"
        "INVOICE\n"
        "Invoice #: INV-9901\n"
        "Invoice Date: 2024-05-15\n"
        "Due Date: 2024-06-15\n"
        "Status: PAID\n"
        "BILL TO:\n"
        "Global Tech Ltd\n"
        "Description Qty Unit Price Amount\n"
        "Cloud Hosting 2 $50.00 $100.00\n"
        "Subtotal: $100.00\n"
        "Tax Amount: $8.00\n"
        "Total (USD): $108.00\n"
    )

    doc = ExtractedDocument(
        raw_text=sample_text,
        cleaned_text=sample_text,
        pages=[PageData(page_number=1, text=sample_text, word_count=40)],
        page_count=1,
    )

    data = parser.parse(doc)
    assert data.invoice_number == "INV-9901"
    assert "Acme" in (data.vendor_name or "")
    assert data.invoice_date == "2024-05-15"
    assert data.due_date == "2024-06-15"
    assert data.customer_name == "Global Tech Ltd"
    assert data.subtotal == 100.00
    assert data.tax_amount == 8.00
    assert data.total_amount == 108.00
    assert data.currency == "USD"
    assert data.payment_status == "PAID"
    assert not data.needs_review


def test_parser_does_not_invent_missing_values():
    parser = InvoiceParser()
    sparse_text = "Some random letter without invoice details."
    doc = ExtractedDocument(
        raw_text=sparse_text,
        cleaned_text=sparse_text,
        pages=[PageData(page_number=1, text=sparse_text, word_count=5)],
        page_count=1,
    )

    data = parser.parse(doc)
    assert data.invoice_number is None
    assert data.total_amount is None
    assert data.payment_status is None
    assert data.needs_review is True  # missing total flags for review


def test_level3_gemini_assisted_extraction_mock():
    """Tests Level 3 Gemini structured JSON extraction fallback with mathematical consistency validation."""
    from unittest.mock import patch, MagicMock
    from core.models import InvoiceData

    parser = InvoiceParser()
    sparse_text = "Vendor is Oracle Cloud Infrastructure. Reference is OCI-77881. Total due is $550.00."
    doc = ExtractedDocument(
        raw_text=sparse_text,
        cleaned_text=sparse_text,
        pages=[PageData(page_number=1, text=sparse_text, word_count=10)],
        page_count=1,
    )

    mock_json = """
    {
      "vendor_name": "Oracle Cloud Infrastructure",
      "invoice_number": "OCI-77881",
      "invoice_date": "2024-04-10",
      "due_date": "2024-05-10",
      "customer_name": "Enterprise Client",
      "subtotal": 500.0,
      "tax_amount": 50.0,
      "discount": 0.0,
      "total_amount": 550.0,
      "currency": "USD",
      "payment_status": "DUE",
      "line_items": [
        {"description": "Compute Units", "quantity": 10.0, "unit_price": 50.0, "amount": 500.0}
      ]
    }
    """

    from core.gemini_service import gemini_service

    with patch.object(gemini_service, "_api_key", "test_key"):
        with patch.object(gemini_service, "generate", return_value=mock_json):
            data = parser.parse(doc, use_gemini_fallback=True)
            assert data.vendor_name == "Oracle Cloud Infrastructure"
            assert data.invoice_number == "OCI-77881"
            assert data.total_amount == 550.0
            assert data.subtotal == 500.0
            assert data.tax_amount == 50.0
            assert len(data.line_items) == 1
            assert not data.needs_review


def test_level3_gemini_math_inconsistency_flags_review():
    """Tests that AI extracted amounts that fail subtotal + tax = total keep needs_review=True."""
    from unittest.mock import patch
    from core.gemini_service import gemini_service

    parser = InvoiceParser()
    sparse_text = "Unstructured invoice receipt."
    doc = ExtractedDocument(
        raw_text=sparse_text,
        cleaned_text=sparse_text,
        pages=[PageData(page_number=1, text=sparse_text, word_count=3)],
        page_count=1,
    )

    # Inconsistent amounts: subtotal 100 + tax 10 != total 250
    inconsistent_json = """
    {
      "vendor_name": "Mystery Vendor",
      "invoice_number": "INV-999",
      "invoice_date": "2024-01-01",
      "subtotal": 100.0,
      "tax_amount": 10.0,
      "total_amount": 250.0,
      "currency": "USD"
    }
    """

    with patch.object(gemini_service, "_api_key", "test_key"):
        with patch.object(gemini_service, "generate", return_value=inconsistent_json):
            data = parser.parse(doc, use_gemini_fallback=True)
            assert data.vendor_name == "Mystery Vendor"
            assert data.needs_review is True  # Math discrepancy flags review

