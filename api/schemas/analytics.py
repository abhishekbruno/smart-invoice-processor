from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    total_invoices: int
    eligible_invoices: int
    processed_cleanly: int
    needs_review: int
    verified_invoices: int
    suspected_duplicates: int
    total_spending: float
    display_currency: str = "INR"
    formatted_total: str
    vendor_count: int
    effective_rate_source: str


class MonthlySpendingItem(BaseModel):
    month: str
    converted_spent: float
    invoice_count: int
    display_currency: str = "INR"


class VendorSpendingItem(BaseModel):
    vendor: str
    converted_spent: float
    invoice_count: int
    display_currency: str = "INR"


class CurrencyDistributionItem(BaseModel):
    currency: str
    invoice_count: int
    original_total: float
    converted_total: float
    display_currency: str = "INR"


class ExpenseAnalyticsResponse(BaseModel):
    summary: AnalyticsSummaryResponse
    monthly_spending: List[MonthlySpendingItem]
    vendor_spending: List[VendorSpendingItem]
    currency_distribution: List[CurrencyDistributionItem]

