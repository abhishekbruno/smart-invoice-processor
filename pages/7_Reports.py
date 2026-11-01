import sys
from datetime import datetime
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st

from config.settings import settings
from core.database import db
from core.report_service import report_service

st.set_page_config(page_title="Financial Reports | Smart Invoice Processor", layout="wide")

st.title("Financial & Audit Reports")
st.caption("Generate, filter, and export verified financial intelligence reports in CSV, Excel (.xlsx), and PDF formats.")

pref_currency = db.get_setting("preferred_display_currency", "INR")

# Report Category Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Invoice Summary",
    "Monthly Expenses",
    "Vendor Spending",
    "Duplicate Review",
])

# =============================================================================
# TAB 1: Invoice Summary Report
# =============================================================================
with tab1:
    st.subheader("Comprehensive Invoice Summary")
    st.caption("Detailed line-by-line register of all processed invoices with original currency and converted valuation.")

    # Filter controls
    with st.expander("Filter Criteria", expanded=False):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        all_invoices = db.get_all_invoices(include_duplicates=True)
        all_vendors = sorted(list({inv.get("vendor_name") for inv in all_invoices if inv.get("vendor_name")}))
        all_currencies = sorted(list({inv.get("currency") for inv in all_invoices if inv.get("currency")}))

        with f_col1:
            sel_vendor = st.selectbox("Filter Vendor", options=["All"] + all_vendors, key="sum_vend")
        with f_col2:
            sel_curr = st.selectbox("Filter Currency", options=["All"] + all_currencies, key="sum_curr")
        with f_col3:
            sel_status = st.selectbox("Filter Status", options=["All", "verified", "processed", "needs_review", "suspected_duplicate"], key="sum_stat")
        with f_col4:
            inc_dups = st.checkbox("Include Suspected Duplicates", value=True, key="sum_dups")

    vendor_arg = None if sel_vendor == "All" else sel_vendor
    curr_arg = None if sel_curr == "All" else sel_curr
    status_arg = None if sel_status == "All" else sel_status

    df_summary = report_service.build_invoice_summary_report(
        vendor=vendor_arg,
        currency=curr_arg,
        status=status_arg,
        include_duplicates=inc_dups,
        target_currency=pref_currency,
    )

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Records", len(df_summary))
    with m2:
        orig_usd_sum = df_summary[df_summary["Original Currency"] == "USD"]["Original Amount"].sum() if not df_summary.empty else 0.0
        st.metric("Total Original USD", f"${orig_usd_sum:,.2f}")
    with m3:
        target_sum = df_summary[f"Converted Amount ({pref_currency})"].sum() if not df_summary.empty else 0.0
        st.metric(f"Total Valuation ({pref_currency})", f"₹{target_sum:,.2f}" if pref_currency == "INR" else f"{pref_currency} {target_sum:,.2f}")
    with m4:
        dup_cnt = len(df_summary[df_summary["Is Duplicate"] == "Yes"]) if not df_summary.empty else 0
        st.metric("Duplicates in View", dup_cnt)

    # Display Table
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # Export Buttons
    st.markdown("##### 📥 Export Invoice Summary Report")
    exp_col1, exp_col2, exp_col3, _ = st.columns([1.5, 1.5, 1.5, 3.5])
    timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")

    with exp_col1:
        csv_bytes = report_service.export_csv(df_summary)
        st.download_button(
            label="📄 Download CSV",
            data=csv_bytes,
            file_name=f"invoice_summary_{timestamp_slug}.csv",
            mime="text/csv",
            key="dl_sum_csv",
            use_container_width=True,
        )

    with exp_col2:
        excel_bytes = report_service.export_excel(df_summary, sheet_name="InvoiceSummary")
        st.download_button(
            label="Download Excel",
            data=excel_bytes,
            file_name=f"invoice_summary_{timestamp_slug}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_sum_excel",
            use_container_width=True,
        )

    with exp_col3:
        pdf_bytes = report_service.export_pdf(
            title="Invoice Summary Report",
            subtitle=f"Generated from verified records. Target Valuation Currency: {pref_currency}",
            df=df_summary,
        )
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"invoice_summary_{timestamp_slug}.pdf",
            mime="application/pdf",
            key="dl_sum_pdf",
            use_container_width=True,
        )


# =============================================================================
# TAB 2: Monthly Expense Report
# =============================================================================
with tab2:
    st.subheader("Monthly Expense Aggregation")
    st.caption("Month-by-month spending trends converted to reference currency with duplicate separation.")

    m_opt1, m_opt2 = st.columns([2, 4])
    with m_opt1:
        month_inc_dups = st.checkbox("Include suspected duplicates in monthly totals", value=False, key="m_inc_dups")

    df_monthly = report_service.build_monthly_expense_report(
        target_currency=pref_currency,
        include_duplicates=month_inc_dups,
    )

    st.dataframe(df_monthly, use_container_width=True, hide_index=True)

    st.markdown("##### Export Monthly Expense Report")
    m_exp1, m_exp2, m_exp3, _ = st.columns([1.5, 1.5, 1.5, 3.5])

    with m_exp1:
        m_csv = report_service.export_csv(df_monthly)
        st.download_button(
            label="Download CSV",
            data=m_csv,
            file_name=f"monthly_expenses_{timestamp_slug}.csv",
            mime="text/csv",
            key="dl_m_csv",
            use_container_width=True,
        )
    with m_exp2:
        m_excel = report_service.export_excel(df_monthly, sheet_name="MonthlyExpenses")
        st.download_button(
            label="Download Excel",
            data=m_excel,
            file_name=f"monthly_expenses_{timestamp_slug}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_m_excel",
            use_container_width=True,
        )
    with m_exp3:
        m_pdf = report_service.export_pdf(
            title="Monthly Expense Aggregation Report",
            subtitle=f"Aggregated verified spending per billing month (Currency: {pref_currency})",
            df=df_monthly,
        )
        st.download_button(
            label="Download PDF",
            data=m_pdf,
            file_name=f"monthly_expenses_{timestamp_slug}.pdf",
            mime="application/pdf",
            key="dl_m_pdf",
            use_container_width=True,
        )


# =============================================================================
# TAB 3: Vendor Spending Report
# =============================================================================
with tab3:
    st.subheader("Vendor Spending & Audit Overview")
    st.caption("Aggregated verified expenditures broken down by supplier alongside excluded duplicate allocations.")

    df_vendor = report_service.build_vendor_spending_report(target_currency=pref_currency)
    st.dataframe(df_vendor, use_container_width=True, hide_index=True)

    st.markdown("##### Export Vendor Spending Report")
    v_exp1, v_exp2, v_exp3, _ = st.columns([1.5, 1.5, 1.5, 3.5])

    with v_exp1:
        v_csv = report_service.export_csv(df_vendor)
        st.download_button(
            label="Download CSV",
            data=v_csv,
            file_name=f"vendor_spending_{timestamp_slug}.csv",
            mime="text/csv",
            key="dl_v_csv",
            use_container_width=True,
        )
    with v_exp2:
        v_excel = report_service.export_excel(df_vendor, sheet_name="VendorSpending")
        st.download_button(
            label="Download Excel",
            data=v_excel,
            file_name=f"vendor_spending_{timestamp_slug}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_v_excel",
            use_container_width=True,
        )
    with v_exp3:
        v_pdf = report_service.export_pdf(
            title="Vendor Spending Breakdown Report",
            subtitle=f"Verified expenditures per supplier with duplicate safeguards ({pref_currency})",
            df=df_vendor,
        )
        st.download_button(
            label="📑 Download PDF",
            data=v_pdf,
            file_name=f"vendor_spending_{timestamp_slug}.pdf",
            mime="application/pdf",
            key="dl_v_pdf",
            use_container_width=True,
        )


# =============================================================================
# TAB 4: Duplicate Review Report
# =============================================================================
with tab4:
    st.subheader("⚠️ Duplicate Invoice Audit Report")
    st.caption("Complete register of suspected and confirmed duplicate invoice submissions and their audit trail.")

    df_dups = report_service.build_duplicate_review_report()
    if df_dups.empty:
        st.success("🎉 No suspected or confirmed duplicate invoices in the database.")
    else:
        st.dataframe(df_dups, use_container_width=True, hide_index=True)

    st.markdown("##### 📥 Export Duplicate Review Report")
    d_exp1, d_exp2, d_exp3, _ = st.columns([1.5, 1.5, 1.5, 3.5])

    with d_exp1:
        d_csv = report_service.export_csv(df_dups)
        st.download_button(
            label="📄 Download CSV",
            data=d_csv,
            file_name=f"duplicate_review_{timestamp_slug}.csv",
            mime="text/csv",
            key="dl_d_csv",
            use_container_width=True,
        )
    with d_exp2:
        d_excel = report_service.export_excel(df_dups, sheet_name="DuplicateAudit")
        st.download_button(
            label="📊 Download Excel",
            data=d_excel,
            file_name=f"duplicate_review_{timestamp_slug}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_d_excel",
            use_container_width=True,
        )
    with d_exp3:
        d_pdf = report_service.export_pdf(
            title="Duplicate Invoice Audit Report",
            subtitle="Flagged duplicate invoices with audit reasons and reference IDs",
            df=df_dups,
        )
        st.download_button(
            label="📑 Download PDF",
            data=d_pdf,
            file_name=f"duplicate_review_{timestamp_slug}.pdf",
            mime="application/pdf",
            key="dl_d_pdf",
            use_container_width=True,
        )

