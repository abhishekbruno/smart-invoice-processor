from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from api.schemas.analytics import (
    AnalyticsSummaryResponse,
    CurrencyDistributionItem,
    ExpenseAnalyticsResponse,
    MonthlySpendingItem,
    VendorSpendingItem,
)
from core.currency_service import currency_service
from core.database import db

router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    currency: Optional[str] = Query(None, description="Preferred display currency (INR, USD, EUR, GBP)"),
    mode: str = Query("historical", pattern="^(historical|latest)$", description="Valuation mode"),
):
    """Returns top-level financial metrics, eligible invoice totals, and currency valuation summary."""
    pref_curr = currency.upper() if currency else db.get_setting("preferred_display_currency", "INR")
    counts = db.get_invoice_counts()

    agg = currency_service.get_aggregated_spending(
        target_currency=pref_curr,
        mode=mode,
        include_duplicates=False,
    )

    all_invoices = db.get_all_invoices(include_duplicates=False)
    vendor_set = {inv.get("vendor_name") for inv in all_invoices if inv.get("vendor_name")}

    return AnalyticsSummaryResponse(
        total_invoices=counts["total"],
        eligible_invoices=agg["invoice_count"],
        processed_cleanly=counts["processed"],
        needs_review=counts["needs_review"],
        verified_invoices=counts["verified"],
        suspected_duplicates=counts.get("suspected_duplicate", 0),
        total_spending=float(agg.get("total_converted_float", agg.get("total_converted", 0.0))),
        display_currency=pref_curr,
        formatted_total=agg["formatted_total"],
        vendor_count=len(vendor_set),
        effective_rate_source=currency_service.SOURCE_LABEL,
    )


@router.get("/monthly", response_model=List[MonthlySpendingItem])
def get_monthly_spending(
    currency: Optional[str] = Query(None, description="Target currency"),
    mode: str = Query("historical", pattern="^(historical|latest)$"),
):
    """Returns month-by-month spending trends converted to preferred currency."""
    pref_curr = currency.upper() if currency else db.get_setting("preferred_display_currency", "INR")
    agg = currency_service.get_aggregated_spending(
        target_currency=pref_curr,
        mode=mode,
        include_duplicates=False,
    )

    all_invoices = db.get_all_invoices(include_duplicates=False)
    month_counts = {}
    for inv in all_invoices:
        d = inv.get("invoice_date")
        if d and len(d) >= 7:
            m_key = d[:7]
            month_counts[m_key] = month_counts.get(m_key, 0) + 1

    return [
        MonthlySpendingItem(
            month=m["month"],
            converted_spent=m["converted_spent"],
            invoice_count=m.get("invoice_count", month_counts.get(m["month"], 1)),
            display_currency=pref_curr,
        )
        for m in agg.get("monthly_spending", [])
    ]


@router.get("/vendors", response_model=List[VendorSpendingItem])
def get_vendor_spending(
    currency: Optional[str] = Query(None, description="Target currency"),
    mode: str = Query("historical", pattern="^(historical|latest)$"),
):
    """Returns aggregated spending per vendor converted to preferred currency."""
    pref_curr = currency.upper() if currency else db.get_setting("preferred_display_currency", "INR")
    agg = currency_service.get_aggregated_spending(
        target_currency=pref_curr,
        mode=mode,
        include_duplicates=False,
    )

    all_invoices = db.get_all_invoices(include_duplicates=False)
    vendor_counts = {}
    for inv in all_invoices:
        v = inv.get("vendor_name")
        if v:
            vendor_counts[v] = vendor_counts.get(v, 0) + 1

    return [
        VendorSpendingItem(
            vendor=v["vendor"],
            converted_spent=v["converted_spent"],
            invoice_count=v.get("invoice_count", vendor_counts.get(v["vendor"], 1)),
            display_currency=pref_curr,
        )
        for v in agg.get("vendor_spending", [])
    ]


@router.get("/currencies", response_model=List[CurrencyDistributionItem])
def get_currency_distribution(
    currency: Optional[str] = Query(None, description="Target valuation currency"),
    mode: str = Query("historical", pattern="^(historical|latest)$"),
):
    """Returns distribution of expenses by original invoice currency."""
    pref_curr = currency.upper() if currency else db.get_setting("preferred_display_currency", "INR")
    agg = currency_service.get_aggregated_spending(
        target_currency=pref_curr,
        mode=mode,
        include_duplicates=False,
    )

    return [
        CurrencyDistributionItem(
            currency=c["currency"],
            invoice_count=c["invoice_count"],
            original_total=c["original_total"],
            converted_total=c["converted_total"],
            display_currency=pref_curr,
        )
        for c in agg.get("original_currencies", [])
    ]


@router.get("/expenses", response_model=ExpenseAnalyticsResponse)
def get_full_expense_analytics(
    currency: Optional[str] = Query(None, description="Target currency"),
    mode: str = Query("historical", pattern="^(historical|latest)$"),
):
    """Returns comprehensive analytics payload combining summary, monthly, vendor, and currency metrics."""
    pref_curr = currency.upper() if currency else db.get_setting("preferred_display_currency", "INR")
    summary = get_analytics_summary(currency=pref_curr, mode=mode)
    monthly = get_monthly_spending(currency=pref_curr, mode=mode)
    vendors = get_vendor_spending(currency=pref_curr, mode=mode)
    currencies = get_currency_distribution(currency=pref_curr, mode=mode)

    return ExpenseAnalyticsResponse(
        summary=summary,
        monthly_spending=monthly,
        vendor_spending=vendors,
        currency_distribution=currencies,
    )

