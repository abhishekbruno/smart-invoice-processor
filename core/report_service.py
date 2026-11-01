import io
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from utils.logger import logger


class ReportService:
    """Generates structured financial and audit reports in CSV, Excel (.xlsx), and PDF formats."""

    def __init__(self, database=None, curr_service=None):
        self.db = database or db
        self.currency_service = curr_service or currency_service

    # =========================================================================
    # Report Data Builders
    # =========================================================================

    def build_invoice_summary_report(
        self,
        vendor: Optional[str] = None,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        include_duplicates: bool = True,
        target_currency: str = "INR",
    ) -> pd.DataFrame:
        """
        Builds a comprehensive invoice summary report with original and converted amounts.
        """
        invoices = self.db.get_all_invoices(include_duplicates=include_duplicates)
        records = []

        for inv in invoices:
            # Apply filters
            if vendor and vendor.lower() not in (inv.get("vendor_name") or "").lower():
                continue
            if status and inv.get("status") != status:
                continue
            if currency and inv.get("currency") != currency:
                continue
            inv_date = inv.get("invoice_date") or ""
            if date_from and inv_date and inv_date < date_from:
                continue
            if date_to and inv_date and inv_date > date_to:
                continue

            orig_amt = inv.get("total_amount") or 0.0
            orig_curr = inv.get("currency") or "USD"

            # Compute converted value
            conv_res = self.currency_service.convert_currency(
                amount=orig_amt,
                from_currency=orig_curr,
                to_currency=target_currency,
                date=inv.get("invoice_date"),
                mode="historical",
            )
            conv_amt = float(conv_res.converted_amount)

            records.append({
                "Invoice ID": inv.get("id"),
                "Vendor Name": inv.get("vendor_name") or "Unknown",
                "Invoice Number": inv.get("invoice_number") or "N/A",
                "Invoice Date": inv.get("invoice_date") or "N/A",
                "Due Date": inv.get("due_date") or "N/A",
                "Original Currency": orig_curr,
                "Original Amount": orig_amt,
                f"Converted Amount ({target_currency})": conv_amt,
                "Status": inv.get("status", "processed"),
                "Is Duplicate": "Yes" if inv.get("is_duplicate") else "No",
                "Duplicate Reason": inv.get("duplicate_reason") or "",
            })

        return pd.DataFrame(records)

    def build_monthly_expense_report(
        self,
        target_currency: str = "INR",
        include_duplicates: bool = False,
    ) -> pd.DataFrame:
        """
        Aggregates monthly spending converted to target currency (excluding duplicates by default).
        """
        invoices = self.db.get_all_invoices(include_duplicates=include_duplicates)
        monthly_map: Dict[str, Dict[str, Any]] = {}

        for inv in invoices:
            if not include_duplicates and inv.get("is_duplicate"):
                continue

            date_str = inv.get("invoice_date")
            month_key = date_str[:7] if date_str and len(date_str) >= 7 else "Unknown / Undated"

            orig_amt = inv.get("total_amount") or 0.0
            orig_curr = inv.get("currency") or "USD"

            conv_res = self.currency_service.convert_currency(
                amount=orig_amt,
                from_currency=orig_curr,
                to_currency=target_currency,
                date=date_str,
                mode="historical",
            )
            conv_val = float(conv_res.converted_amount)

            if month_key not in monthly_map:
                monthly_map[month_key] = {
                    "Month": month_key,
                    "Total Invoices": 0,
                    f"Total Spend ({target_currency})": 0.0,
                    "Vendors": set(),
                }

            monthly_map[month_key]["Total Invoices"] += 1
            monthly_map[month_key][f"Total Spend ({target_currency})"] += conv_val
            v_name = inv.get("vendor_name")
            if v_name:
                monthly_map[month_key]["Vendors"].add(v_name)

        rows = []
        for m in sorted(monthly_map.keys()):
            item = monthly_map[m]
            rows.append({
                "Billing Month": item["Month"],
                "Eligible Invoices": item["Total Invoices"],
                f"Total Converted Spend ({target_currency})": round(item[f"Total Spend ({target_currency})"], 2),
                "Active Vendors": len(item["Vendors"]),
                "Vendor Summary": ", ".join(sorted(item["Vendors"])) if item["Vendors"] else "None",
            })

        return pd.DataFrame(rows)

    def build_vendor_spending_report(
        self,
        target_currency: str = "INR",
    ) -> pd.DataFrame:
        """
        Builds per-vendor spending totals, invoice counts, and duplicate review metrics.
        """
        invoices = self.db.get_all_invoices(include_duplicates=True)
        vendor_map: Dict[str, Dict[str, Any]] = {}

        for inv in invoices:
            v_name = inv.get("vendor_name") or "Unknown Vendor"
            is_dup = bool(inv.get("is_duplicate"))
            orig_amt = inv.get("total_amount") or 0.0
            orig_curr = inv.get("currency") or "USD"

            conv_res = self.currency_service.convert_currency(
                amount=orig_amt,
                from_currency=orig_curr,
                to_currency=target_currency,
                date=inv.get("invoice_date"),
                mode="historical",
            )
            conv_val = float(conv_res.converted_amount)

            if v_name not in vendor_map:
                vendor_map[v_name] = {
                    "Vendor Name": v_name,
                    "Eligible Invoices": 0,
                    "Suspected Duplicates": 0,
                    f"Verified Spending ({target_currency})": 0.0,
                    f"Excluded Value ({target_currency})": 0.0,
                }

            if is_dup:
                vendor_map[v_name]["Suspected Duplicates"] += 1
                vendor_map[v_name][f"Excluded Value ({target_currency})"] += conv_val
            else:
                vendor_map[v_name]["Eligible Invoices"] += 1
                vendor_map[v_name][f"Verified Spending ({target_currency})"] += conv_val

        rows = []
        for v in sorted(vendor_map.keys()):
            item = vendor_map[v]
            rows.append({
                "Vendor Name": item["Vendor Name"],
                "Eligible Invoices": item["Eligible Invoices"],
                "Suspected Duplicates": item["Suspected Duplicates"],
                f"Verified Spending ({target_currency})": round(item[f"Verified Spending ({target_currency})"], 2),
                f"Excluded Value ({target_currency})": round(item[f"Excluded Value ({target_currency})"], 2),
            })

        return pd.DataFrame(rows)

    def build_duplicate_review_report(self) -> pd.DataFrame:
        """
        Builds a dedicated report of all flagged duplicate invoices and their audit details.
        """
        invoices = self.db.get_all_invoices(include_duplicates=True)
        duplicates = [inv for inv in invoices if inv.get("is_duplicate") or inv.get("status") == "suspected_duplicate"]

        rows = []
        for inv in duplicates:
            rows.append({
                "Invoice ID": inv.get("id"),
                "Vendor Name": inv.get("vendor_name") or "Unknown",
                "Invoice Number": inv.get("invoice_number") or "N/A",
                "Invoice Date": inv.get("invoice_date") or "N/A",
                "Original Currency": inv.get("currency") or "USD",
                "Total Amount": inv.get("total_amount") or 0.0,
                "Duplicate Of ID": inv.get("duplicate_of_id") or "N/A",
                "Duplicate Reason": inv.get("duplicate_reason") or "Flagged during processing",
                "Current Status": inv.get("status") or "suspected_duplicate",
                "Source File": inv.get("source_file_path", ""),
            })

        return pd.DataFrame(rows)

    # =========================================================================
    # Exporters (CSV, Excel, PDF)
    # =========================================================================

    @staticmethod
    def export_csv(df: pd.DataFrame) -> bytes:
        """Exports DataFrame to raw UTF-8 CSV bytes."""
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")

    @staticmethod
    def export_excel(df: pd.DataFrame, sheet_name: str = "Report") -> bytes:
        """Exports DataFrame to Microsoft Excel (.xlsx) bytes."""
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        return buffer.getvalue()

    @staticmethod
    def export_pdf(
        title: str,
        df: pd.DataFrame,
        subtitle: Optional[str] = None,
        max_rows: int = 100,
    ) -> bytes:
        """
        Generates a clean, professional PDF report document using ReportLab.
        """
        buffer = io.BytesIO()
        # Use landscape orientation for tabular clarity
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
        )
        header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        elements = []
        elements.append(Paragraph(title, title_style))
        if subtitle:
            elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Records: {len(df)}", subtitle_style))
        elements.append(Spacer(1, 14))

        if df.empty:
            elements.append(Paragraph("No records found matching the specified report criteria.", subtitle_style))
        else:
            # Truncate if excessively large for a single PDF export
            sample_df = df.head(max_rows)
            headers = [Paragraph(str(col), header_style) for col in sample_df.columns]
            table_data = [headers]

            for _, row in sample_df.iterrows():
                row_cells = []
                for val in row:
                    text_val = str(val) if pd.notna(val) else ""
                    # Truncate very long cells for PDF layout
                    if len(text_val) > 40:
                        text_val = text_val[:37] + "..."
                    row_cells.append(Paragraph(text_val, cell_style))
                table_data.append(row_cells)

            col_width = (doc.width) / max(1, len(sample_df.columns))
            table = Table(table_data, colWidths=[col_width] * len(sample_df.columns), repeatRows=1)
            table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ])
            )
            elements.append(table)

            if len(df) > max_rows:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"*(Note: PDF view displays first {max_rows} rows. Use CSV or Excel for the full export of {len(df)} records.)*", subtitle_style))

        doc.build(elements)
        return buffer.getvalue()


# Global singleton
report_service = ReportService()
