import pytest
from core.database import DatabaseManager, normalize_vendor_name, normalize_invoice_number, db
from core.models import InvoiceData, LineItem
from core.query_service import query_service


@pytest.fixture
def test_db(tmp_path):
    """Provides a fresh isolated DatabaseManager instance for duplicate testing."""
    db_file = tmp_path / "test_dup.db"
    manager = DatabaseManager(db_path=db_file)
    return manager


def test_normalization_functions():
    """Tests vendor and invoice number normalization helpers."""
    # Vendor normalization
    assert normalize_vendor_name("Amazon Web Services") == "amazon web services"
    assert normalize_vendor_name("AWS") == "amazon web services"
    assert normalize_vendor_name("Amazon Web Services, Inc.") == "amazon web services"
    assert normalize_vendor_name("TechSolutions, LLC") == "techsolutions"
    assert normalize_vendor_name("Google Cloud Corp") == "google cloud"
    assert normalize_vendor_name("GCP") == "google cloud"

    # Invoice number normalization
    assert normalize_invoice_number("INV-AWS-2024-8192") == "INV-AWS-2024-8192"
    assert normalize_invoice_number("#INV-AWS-2024-8192") == "INV-AWS-2024-8192"
    assert normalize_invoice_number("  inv-aws-2024-8192  ") == "INV-AWS-2024-8192"
    assert normalize_invoice_number(":ACME-88401") == "ACME-88401"


def test_identical_pdf_hash_duplicate_detection(test_db):
    """Tests Requirement 10: identical PDFs with the exact same SHA-256 hash."""
    file_hash = "hash_exact_match_12345"
    inv = InvoiceData(
        invoice_number="INV-001",
        vendor_name="Acme Corp",
        total_amount=100.0,
        currency="USD",
    )
    assert not test_db.is_duplicate(file_hash)

    # First save
    id1 = test_db.save_invoice(inv, "path/to/invoice_1.pdf", file_hash)
    assert id1 > 0
    assert test_db.is_duplicate(file_hash)

    # Re-saving same hash updates existing record rather than creating duplicate row
    id2 = test_db.save_invoice(inv, "path/to/invoice_1.pdf", file_hash)
    assert id1 == id2


def test_regenerated_pdf_different_hash_logical_duplicate(test_db):
    """
    Tests Requirement 10: regenerated PDF with a different SHA-256 hash
    (e.g., ReportLab timestamp change), but identical business invoice fields.
    """
    # 1. First invoice upload
    inv1 = InvoiceData(
        invoice_number="INV-AWS-2024-8192",
        vendor_name="Amazon Web Services",
        invoice_date="2024-01-15",
        subtotal=735.0,
        tax_amount=58.80,
        total_amount=793.80,
        currency="USD",
        line_items=[
            LineItem(description="EC2 instances", quantity=3.0, unit_price=145.0, amount=435.0),
            LineItem(description="S3 storage", quantity=1.0, unit_price=50.0, amount=50.0),
        ],
    )
    hash_run1 = "hash_reportlab_run1_timestamp_140428"
    id1 = test_db.save_invoice(inv1, "data/AWS_INV_2024_8192.pdf", hash_run1)

    rec1 = test_db.get_invoice_by_id(id1)
    assert rec1["is_duplicate"] == 0
    assert rec1["status"] == "processed"
    assert rec1["duplicate_of_id"] is None

    # 2. Regenerated invoice upload (different hash!)
    inv2 = InvoiceData(
        invoice_number="INV-AWS-2024-8192",
        vendor_name="AWS, Inc.",  # slightly different suffix
        invoice_date="2024-01-15",
        subtotal=735.0,
        tax_amount=58.80,
        total_amount=793.80,
        currency="USD",
        line_items=[
            LineItem(description="EC2 instances", quantity=3.0, unit_price=145.0, amount=435.0),
            LineItem(description="S3 storage", quantity=1.0, unit_price=50.0, amount=50.0),
        ],
    )
    hash_run2 = "hash_reportlab_run2_timestamp_140514"
    id2 = test_db.save_invoice(inv2, "data/AWS_INV_2024_8192.pdf", hash_run2)

    # Must be saved as a distinct record (never deleted, auditable)
    assert id2 != id1

    rec2 = test_db.get_invoice_by_id(id2)
    # Must be flagged as suspected duplicate
    assert rec2["is_duplicate"] == 1
    assert rec2["status"] == "suspected_duplicate"
    assert rec2["duplicate_of_id"] == id1
    assert "Suspected duplicate of Invoice #" in rec2["duplicate_reason"]

    # 3. Verify financial totals exclude the duplicate (prevents inflation)
    expenses = test_db.get_total_expenses()
    assert len(expenses) == 1
    # Must be $793.80, NOT $1,587.60!
    assert expenses[0]["total_spent"] == 793.80
    assert expenses[0]["invoice_count"] == 1

    vendor_expenses = test_db.get_expenses_by_vendor()
    assert len(vendor_expenses) == 1
    assert vendor_expenses[0]["total_spent"] == 793.80


def test_genuinely_different_invoices_not_flagged(test_db):
    """Tests Requirement 10: genuinely different invoices are not flagged as duplicates."""
    # Invoice A from AWS in January
    inv_a = InvoiceData(
        invoice_number="INV-AWS-2024-001",
        vendor_name="Amazon Web Services",
        invoice_date="2024-01-15",
        total_amount=500.0,
        currency="USD",
    )
    id_a = test_db.save_invoice(inv_a, "aws_jan.pdf", "hash_aws_jan")

    # Invoice B from AWS in February (different invoice number)
    inv_b = InvoiceData(
        invoice_number="INV-AWS-2024-002",
        vendor_name="Amazon Web Services",
        invoice_date="2024-02-15",
        total_amount=620.0,
        currency="USD",
    )
    id_b = test_db.save_invoice(inv_b, "aws_feb.pdf", "hash_aws_feb")

    # Invoice C from Google Cloud (different vendor)
    inv_c = InvoiceData(
        invoice_number="INV-GCP-2024-001",
        vendor_name="Google Cloud",
        invoice_date="2024-01-20",
        total_amount=450.0,
        currency="USD",
    )
    id_c = test_db.save_invoice(inv_c, "gcp_jan.pdf", "hash_gcp_jan")

    rec_a = test_db.get_invoice_by_id(id_a)
    rec_b = test_db.get_invoice_by_id(id_b)
    rec_c = test_db.get_invoice_by_id(id_c)

    assert rec_a["is_duplicate"] == 0
    assert rec_b["is_duplicate"] == 0
    assert rec_c["is_duplicate"] == 0

    assert rec_a["status"] == "processed"
    assert rec_b["status"] == "processed"
    assert rec_c["status"] == "processed"

    # All three must be included in financial calculations
    expenses = test_db.get_total_expenses()
    assert len(expenses) == 1
    assert expenses[0]["total_spent"] == 1570.0  # 500 + 620 + 450
    assert expenses[0]["invoice_count"] == 3


def test_manual_review_workflow(test_db):
    """Tests marking an invoice as genuine vs confirming as duplicate."""
    # Create original
    inv1 = InvoiceData(invoice_number="INV-REV-01", vendor_name="Vendor A", total_amount=100.0, currency="USD")
    id1 = test_db.save_invoice(inv1, "file1.pdf", "hash_rev1")

    # Create suspected duplicate
    inv2 = InvoiceData(invoice_number="INV-REV-01", vendor_name="Vendor A", total_amount=100.0, currency="USD")
    id2 = test_db.save_invoice(inv2, "file2.pdf", "hash_rev2")

    assert test_db.get_invoice_by_id(id2)["is_duplicate"] == 1
    assert test_db.get_total_expenses()[0]["total_spent"] == 100.0

    # User reviews and marks invoice #2 as genuine (e.g., vendor issued duplicate invoice number legitimately)
    success = test_db.mark_invoice_genuine(id2)
    assert success
    rec2_updated = test_db.get_invoice_by_id(id2)
    assert rec2_updated["is_duplicate"] == 0
    assert rec2_updated["status"] == "verified"
    assert rec2_updated["duplicate_of_id"] is None

    # Now both invoices are included in spending
    assert test_db.get_total_expenses()[0]["total_spent"] == 200.0

    # User re-flags invoice #2 as duplicate
    success2 = test_db.mark_invoice_duplicate(id2, duplicate_of_id=id1, reason="Confirmed duplicate by manager")
    assert success2
    rec2_reflagged = test_db.get_invoice_by_id(id2)
    assert rec2_reflagged["is_duplicate"] == 1
    assert rec2_reflagged["status"] == "suspected_duplicate"
    assert test_db.get_total_expenses()[0]["total_spent"] == 100.0


def test_active_database_has_no_deleted_records():
    """Confirms Requirement 9: Exactly 24 records preserved in data/invoices.db, with 12 duplicates correctly flagged."""
    counts = db.get_invoice_counts()
    assert counts["total"] == 24, f"Expected 24 total records preserved, found {counts['total']}"
    assert counts["suspected_duplicate"] == 12, f"Expected 12 flagged duplicates, found {counts['suspected_duplicate']}"

    # Verify AWS ID 2 is eligible and AWS ID 14 is flagged
    aws_invoices = db.get_all_invoices(vendor="Amazon Web Services")
    assert len(aws_invoices) == 2

    inv2 = next(i for i in aws_invoices if i["id"] == 2)
    inv14 = next(i for i in aws_invoices if i["id"] == 14)

    assert inv2["is_duplicate"] == 0
    assert inv2["status"] == "processed"
    assert inv14["is_duplicate"] == 1
    assert inv14["status"] == "suspected_duplicate"
    assert inv14["duplicate_of_id"] == 2

