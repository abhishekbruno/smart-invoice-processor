import pytest
from core.database import db
from core.models import InvoiceData
from core.query_service import query_service


def test_query_total_spending():
    res = query_service.process_query("What did we spend in total?")
    assert "answer" in res
    assert "sources" in res
    assert "Overall Spending Summary" in res["answer"] or "spending" in res["answer"].lower()


def test_query_vendor_spending():
    res = query_service.process_query("What did we spend on AWS?")
    assert "answer" in res
    assert "Amazon Web Services" in res["answer"] or "AWS" in res["answer"]


def test_query_highest_invoices():
    res = query_service.process_query("Which vendor charged the highest amount?")
    assert "answer" in res
    assert "Highest-Value Invoices" in res["answer"]


def test_query_vendor_comparison():
    res = query_service.process_query("Compare spending between AWS and Google Cloud")
    assert "answer" in res
    assert "Comparison" in res["answer"]


def test_query_specific_invoice():
    res = query_service.process_query("What services were billed on invoice INV-AWS-2024-8192?")
    assert "answer" in res
    assert "Amazon Elastic Compute Cloud" in res["answer"] or "EC2" in res["answer"]

