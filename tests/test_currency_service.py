import unittest.mock as mock
from decimal import Decimal
import pytest
from core.currency_service import CurrencyService, currency_service
from core.database import db
from core.query_service import query_service
from core.rag_pipeline import RAGPipeline


def test_usd_to_inr_conversion():
    """Tests Requirement 9: USD to INR historical conversion."""
    res = currency_service.convert_currency(
        amount=Decimal("793.80"),
        from_currency="USD",
        to_currency="INR",
        date="2024-01-15",
    )
    assert res.from_currency == "USD"
    assert res.to_currency == "INR"
    assert res.exchange_rate == Decimal("82.87")
    assert res.effective_date == "2024-01-15"
    assert res.converted_amount == Decimal("65782.21")
    assert "Frankfurter" in res.source or "ECB" in res.source or "Cache" in res.source


def test_eur_to_inr_conversion():
    """Tests Requirement 9: EUR to INR historical conversion."""
    res = currency_service.convert_currency(
        amount=Decimal("6231.50"),
        from_currency="EUR",
        to_currency="INR",
        date="2024-07-15",
    )
    assert res.from_currency == "EUR"
    assert res.to_currency == "INR"
    assert res.exchange_rate == Decimal("91.168")
    assert res.effective_date == "2024-07-15"
    assert res.converted_amount == Decimal("568113.39")


def test_gbp_to_inr_conversion():
    """Tests Requirement 9: GBP to INR historical conversion with weekend date adjustment."""
    # 2024-06-01 is a Saturday; ECB reference date is Friday 2024-05-31
    res = currency_service.convert_currency(
        amount=Decimal("936.00"),
        from_currency="GBP",
        to_currency="INR",
        date="2024-06-01",
    )
    assert res.from_currency == "GBP"
    assert res.to_currency == "INR"
    assert res.exchange_rate == Decimal("106.05")
    assert res.effective_date == "2024-05-31"
    assert res.converted_amount == Decimal("99262.80")


def test_inr_to_inr_identity():
    """Tests Requirement 9: INR to INR conversion is exactly 1:1 with zero network latency."""
    res = currency_service.convert_currency(
        amount=Decimal("206500.00"),
        from_currency="INR",
        to_currency="INR",
        date="2024-09-12",
    )
    assert res.exchange_rate == Decimal("1.0")
    assert res.converted_amount == Decimal("206500.00")
    assert "Same Currency" in res.source


def test_historical_date_conversion_preceding_business_day():
    """Tests Requirement 5: Non-business day uses preceding rate and displays actual effective date."""
    # Saturday 2024-02-10 -> Effective Friday 2024-02-09
    res = currency_service.get_historical_rate("2024-02-10", "USD", "INR")
    assert res.requested_date == "2024-02-10"
    assert res.effective_date == "2024-02-09"
    assert res.rate == Decimal("83.03")


def test_missing_dates_fallback():
    """Tests Requirement 8: Missing or empty dates fall back gracefully to latest rate."""
    res = currency_service.convert_currency(
        amount=Decimal("100.00"),
        from_currency="USD",
        to_currency="INR",
        date=None,
        mode="historical",
    )
    assert res.exchange_rate > Decimal("50.0")
    assert res.converted_amount > Decimal("5000.00")


def test_api_connection_failure_fallback():
    """Tests Requirement 8: API failure falls back safely with audit warning."""
    isolated_svc = CurrencyService()

    with mock.patch("urllib.request.urlopen", side_effect=Exception("Simulated Network Outage")):
        res = isolated_svc.get_exchange_rate("USD", "INR", date="2029-12-31")
        assert res.is_fallback
        assert res.warning is not None
        assert "unavailable" in res.warning.lower() or "unreachable" in res.warning.lower()
        # Still returns a valid positive Decimal rate rather than crashing
        assert res.rate > Decimal("0")


def test_decimal_precision_and_rounding():
    """Tests Requirement 2: Precision arithmetic with Decimal and ROUND_HALF_UP."""
    # 1/3 dollar at rate 82.87
    amt = Decimal("10.005")
    # Verify exact decimal rounding
    res = currency_service.convert_currency(amt, "USD", "INR", date="2024-01-15")
    # 10.005 * 82.87 = 829.11435 -> 829.11
    assert res.converted_amount == Decimal("829.11")


def test_currency_formatting():
    """Tests Requirement 2 & 9: Currency formatting with Indian Lakhs system and international symbols."""
    # INR formatting with Indian numbering system
    assert currency_service.format_currency(Decimal("175000.00"), "INR") == "₹1,75,000.00"
    assert currency_service.format_currency(Decimal("65782.21"), "INR") == "₹65,782.21"
    assert currency_service.format_currency(Decimal("1664851.55"), "INR") == "₹16,64,851.55"

    # International currencies
    assert currency_service.format_currency(Decimal("793.80"), "USD") == "$793.80"
    assert currency_service.format_currency(Decimal("6231.50"), "EUR") == "€6,231.50"
    assert currency_service.format_currency(Decimal("936.00"), "GBP") == "£936.00"


def test_duplicate_exclusion_in_aggregated_spending():
    """Tests Requirement 4: Aggregated spending converts only eligible non-duplicate invoices."""
    agg = currency_service.get_aggregated_spending(target_currency="INR", mode="historical", include_duplicates=False)
    assert agg["invoice_count"] == 12, f"Expected 12 eligible invoices, got {agg['invoice_count']}"
    assert agg["target_currency"] == "INR"

    # Ground truth calculated from the 12 eligible invoice conversions
    assert agg["total_converted"] == Decimal("1664851.55")
    assert agg["formatted_total"] == "₹16,64,851.55"

    # When duplicates are included, total would be higher
    agg_with_dups = currency_service.get_aggregated_spending(target_currency="INR", mode="historical", include_duplicates=True)
    assert agg_with_dups["invoice_count"] == 22 or agg_with_dups["invoice_count"] == 24
    assert agg_with_dups["total_converted"] > Decimal("1664851.55")


def test_mixed_currency_reporting_query():
    """Tests Requirement 7: Total spending query converted to INR."""
    res = query_service.process_query("What is our total spending in INR?")
    ans = res["answer"]
    assert "Total Spending Converted to Indian Rupees (INR)" in ans
    assert "₹16,64,851.55" in ans
    assert "European Central Bank via Frankfurter API" in ans
    assert "USD" in ans
    assert "EUR" in ans
    assert "GBP" in ans
    assert "INR" in ans
    assert "12 suspected duplicate record(s) excluded" in ans


def test_vendor_inr_query():
    """Tests Requirement 7: Vendor specific spending query converted to INR."""
    res = query_service.process_query("How much did we spend on AWS in INR?")
    ans = res["answer"]
    assert "Amazon Web Services" in ans
    assert "$793.80" in ans
    assert "₹65,782.21" in ans
    assert "1 USD = ₹82.8700" in ans
    assert "Rate Date" in ans
    assert "2024-01-15" in ans


def test_vendor_comparison_in_inr():
    """Tests Requirement 7: Vendor comparison query in Indian Rupees."""
    res = query_service.process_query("Compare Google Cloud and AWS expenses in Indian Rupees.")
    ans = res["answer"]
    assert "Amazon Web Services" in ans
    assert "Google Cloud" in ans
    assert "₹65,782.21" in ans
    assert "₹54,621.11" in ans
    assert "₹11,161.10" in ans
    assert "Frankfurter API" in ans


def test_gemini_hybrid_response_with_inr_conversions():
    """Tests Requirement 7 & 9: Gemini hybrid response preserves verified INR conversions."""
    class MockGeminiService:
        @property
        def is_available(self):
            return True

        def generate(self, prompt, system_prompt=None):
            return (
                "Based on the invoice records, Amazon Web Services charges covered EC2 virtual server hosting, "
                "S3 standard object storage, and RDS relational databases. The currency conversion reflects the "
                "daily ECB exchange rate of 82.87 INR per USD on the invoice date."
            )

    pipeline = RAGPipeline(llm=MockGeminiService())
    response = pipeline.answer_query("How much did we spend on AWS in INR and what services were included?")

    assert response.query_type == "hybrid"
    ans = response.answer
    # Must preserve exact verified SQL metrics with INR conversion
    assert r"\$793.80" in ans or "$793.80" in ans
    assert "₹65,782.21" in ans
    assert "82.87" in ans
    # Must include LLM service explanation
    assert "EC2" in ans
    assert "S3" in ans
    assert "RDS" in ans

