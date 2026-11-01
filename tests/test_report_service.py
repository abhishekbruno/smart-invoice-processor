import io
from pathlib import Path
import pandas as pd
import pytest

from core.report_service import report_service
from core.database import db


def test_build_invoice_summary_report():
    """Tests building the comprehensive invoice summary report."""
    df = report_service.build_invoice_summary_report(target_currency="INR")
    assert not df.empty
    assert "Invoice ID" in df.columns
    assert "Vendor Name" in df.columns
    assert "Converted Amount (INR)" in df.columns
    assert "Original Currency" in df.columns
    assert "Original Amount" in df.columns
    assert "Is Duplicate" in df.columns

    # Verify filtering
    df_aws = report_service.build_invoice_summary_report(vendor="Amazon Web Services", target_currency="INR")
    assert not df_aws.empty
    for v in df_aws["Vendor Name"]:
        assert "Amazon Web Services" in v


def test_build_monthly_expense_report():
    """Tests building the monthly aggregated expense report in INR."""
    df = report_service.build_monthly_expense_report(target_currency="INR", include_duplicates=False)
    assert not df.empty
    assert "Billing Month" in df.columns
    assert "Eligible Invoices" in df.columns
    assert "Total Converted Spend (INR)" in df.columns
    assert "Active Vendors" in df.columns

    # Invoices span 2024 months
    months = df["Billing Month"].tolist()
    assert any("2024-" in m for m in months)


def test_build_vendor_spending_report():
    """Tests building the vendor spending report with duplicate segregation."""
    df = report_service.build_vendor_spending_report(target_currency="INR")
    assert not df.empty
    assert "Vendor Name" in df.columns
    assert "Eligible Invoices" in df.columns
    assert "Suspected Duplicates" in df.columns
    assert "Verified Spending (INR)" in df.columns
    assert "Excluded Value (INR)" in df.columns

    # AWS should show 1 eligible invoice and 1 suspected duplicate
    aws_row = df[df["Vendor Name"] == "Amazon Web Services, Inc."]
    if not aws_row.empty:
        assert aws_row.iloc[0]["Eligible Invoices"] == 1
        assert aws_row.iloc[0]["Suspected Duplicates"] >= 1


def test_build_duplicate_review_report():
    """Tests building the duplicate review report."""
    df = report_service.build_duplicate_review_report()
    assert not df.empty
    assert "Invoice ID" in df.columns
    assert "Vendor Name" in df.columns
    assert "Duplicate Reason" in df.columns
    assert "Current Status" in df.columns
    assert len(df) >= 1


def test_export_csv():
    """Tests exporting report dataframe to CSV bytes."""
    df = pd.DataFrame([{"col1": "test", "col2": 123.45}])
    csv_bytes = report_service.export_csv(df)
    assert isinstance(csv_bytes, bytes)
    assert b"test" in csv_bytes
    assert b"123.45" in csv_bytes


def test_export_excel():
    """Tests exporting report dataframe to openpyxl Excel bytes."""
    df = pd.DataFrame([{"Vendor": "Google Cloud", "Amount": 658.80}])
    excel_bytes = report_service.export_excel(df, sheet_name="TestSheet")
    assert isinstance(excel_bytes, bytes)
    # Excel files start with PK zip header bytes
    assert excel_bytes.startswith(b"PK")


def test_export_pdf():
    """Tests exporting report dataframe to ReportLab PDF bytes."""
    df = pd.DataFrame([
        {"Vendor": "Amazon Web Services", "Invoice #": "INV-101", "Amount": "$793.80"},
        {"Vendor": "Microsoft", "Invoice #": "MSFT-202", "Amount": "$928.80"},
    ])
    pdf_bytes = report_service.export_pdf(
        title="Test Financial Summary",
        subtitle="Verification run",
        df=df,
    )
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

