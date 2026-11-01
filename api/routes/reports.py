from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response, status

from core.database import db
from core.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Executive Reports & Exports"])


def _build_file_response(df, report_name: str, export_format: str, subtitle: Optional[str] = None):
    """Encapsulates report export formatting into standard HTTP file responses."""
    fmt = export_format.lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        content = report_service.export_csv(df)
        media_type = "text/csv; charset=utf-8"
        filename = f"{report_name}_{ts}.csv"
    elif fmt in ("excel", "xlsx"):
        content = report_service.export_excel(df, sheet_name=report_name[:31])
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{report_name}_{ts}.xlsx"
    elif fmt == "pdf":
        content = report_service.export_pdf(
            title=report_name.replace("_", " ").title(),
            subtitle=subtitle,
            df=df,
        )
        media_type = "application/pdf"
        filename = f"{report_name}_{ts}.pdf"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{export_format}'. Choose from 'csv', 'excel', or 'pdf'.",
        )

    headers = {
        "Content-Disposition": f"attachment; filename=\"{filename}\"",
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/invoices")
def export_invoice_summary_report(
    format: str = Query("csv", pattern="^(csv|excel|xlsx|pdf)$", description="Export format"),
    vendor: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    target_currency: Optional[str] = Query(None),
    include_duplicates: bool = Query(True),
):
    """Exports filtered invoice summary register in CSV, Excel, or PDF format."""
    pref_curr = target_currency.upper() if target_currency else db.get_setting("preferred_display_currency", "INR")
    df = report_service.build_invoice_summary_report(
        vendor=vendor,
        status=status,
        currency=currency,
        include_duplicates=include_duplicates,
        target_currency=pref_curr,
    )
    return _build_file_response(
        df=df,
        report_name="invoice_summary_report",
        export_format=format,
        subtitle=f"Target Currency: {pref_curr}",
    )


@router.get("/monthly")
def export_monthly_expense_report(
    format: str = Query("csv", pattern="^(csv|excel|xlsx|pdf)$"),
    target_currency: Optional[str] = Query(None),
    include_duplicates: bool = Query(False),
):
    """Exports monthly spending aggregation report in CSV, Excel, or PDF format."""
    pref_curr = target_currency.upper() if target_currency else db.get_setting("preferred_display_currency", "INR")
    df = report_service.build_monthly_expense_report(
        target_currency=pref_curr,
        include_duplicates=include_duplicates,
    )
    return _build_file_response(
        df=df,
        report_name="monthly_expense_report",
        export_format=format,
        subtitle=f"Monthly aggregations converted to {pref_curr}",
    )


@router.get("/vendors")
def export_vendor_spending_report(
    format: str = Query("csv", pattern="^(csv|excel|xlsx|pdf)$"),
    target_currency: Optional[str] = Query(None),
):
    """Exports supplier expenditure breakdown report in CSV, Excel, or PDF format."""
    pref_curr = target_currency.upper() if target_currency else db.get_setting("preferred_display_currency", "INR")
    df = report_service.build_vendor_spending_report(
        target_currency=pref_curr,
    )
    return _build_file_response(
        df=df,
        report_name="vendor_spending_report",
        export_format=format,
        subtitle=f"Vendor expenditures converted to {pref_curr}",
    )

