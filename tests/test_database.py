import pytest
from pathlib import Path
from core.database import DatabaseManager
from core.models import InvoiceData, LineItem, ProcessingRecord


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_invoices.db"
    return DatabaseManager(db_file)


def test_db_initialization(temp_db):
    assert temp_db.db_path.exists()
    counts = temp_db.get_invoice_counts()
    assert counts["total"] == 0


def test_save_and_retrieve_invoice(temp_db):
    inv_data = InvoiceData(
        invoice_number="INV-TEST-001",
        vendor_name="Test Cloud Inc",
        invoice_date="2024-03-01",
        due_date="2024-03-31",
        customer_name="Client Corp",
        subtotal=200.0,
        tax_amount=20.0,
        total_amount=220.0,
        currency="USD",
        payment_status="PAID",
        line_items=[
            LineItem(description="Server Hosting", quantity=1.0, unit_price=200.0, amount=200.0)
        ],
    )

    file_hash = "abcdef1234567890abcdef1234567890"
    inv_id = temp_db.save_invoice(inv_data, "data/test.pdf", file_hash)
    assert inv_id > 0

    # Retrieve
    retrieved = temp_db.get_invoice_by_id(inv_id)
    assert retrieved is not None
    assert retrieved["invoice_number"] == "INV-TEST-001"
    assert retrieved["vendor_name"] == "Test Cloud Inc"
    assert retrieved["total_amount"] == 220.0
    assert len(retrieved["line_items"]) == 1
    assert retrieved["line_items"][0]["description"] == "Server Hosting"


def test_duplicate_detection(temp_db):
    inv_data = InvoiceData(
        invoice_number="INV-DUP-01",
        vendor_name="Dup Corp",
        total_amount=50.0,
        currency="USD",
    )
    file_hash = "unique_hash_99999"
    assert not temp_db.is_duplicate(file_hash)

    temp_db.save_invoice(inv_data, "data/dup.pdf", file_hash)
    assert temp_db.is_duplicate(file_hash)


def test_currency_totals_separation(temp_db):
    # Save 1 USD and 1 EUR invoice
    inv_usd = InvoiceData(invoice_number="U1", vendor_name="US Vendor", total_amount=100.0, currency="USD")
    inv_eur = InvoiceData(invoice_number="E1", vendor_name="EU Vendor", total_amount=50.0, currency="EUR")

    temp_db.save_invoice(inv_usd, "u.pdf", "hash_usd")
    temp_db.save_invoice(inv_eur, "e.pdf", "hash_eur")

    totals = temp_db.get_total_expenses()
    assert len(totals) == 2
    currencies = {t["currency"]: t["total_spent"] for t in totals}
    assert currencies["USD"] == 100.0
    assert currencies["EUR"] == 50.0

