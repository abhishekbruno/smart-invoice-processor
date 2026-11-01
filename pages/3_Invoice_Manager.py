import base64
import os
import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st
from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from core.folder_monitor import InvoiceProcessingPipeline
from utils.helpers import format_currency_amount

st.set_page_config(page_title="Invoice Manager | Smart Invoice Processor", layout="wide")

st.title("Invoice Manager")
st.caption("Search, filter, inspect, reprocess, and manage your repository of processed invoices.")

# 1. Search and Filtering Bar
filter_c1, filter_c2, filter_c3, filter_c4 = st.columns([2, 1.5, 1.5, 1.5])

with filter_c1:
    search_query = st.text_input("Search by Invoice #, Vendor, or Keyword", value="")

with filter_c2:
    status_filter = st.selectbox("Status", options=["All", "processed", "needs_review", "verified", "suspected_duplicate"])

with filter_c3:
    date_from = st.date_input("From Date", value=None)

with filter_c4:
    date_to = st.date_input("To Date", value=None)

date_from_str = date_from.strftime("%Y-%m-%d") if date_from else None
date_to_str = date_to.strftime("%Y-%m-%d") if date_to else None

# Fetch Invoices
invoices = db.get_all_invoices(
    status=status_filter if status_filter != "All" else None,
    date_from=date_from_str,
    date_to=date_to_str,
    search=search_query if search_query.strip() else None,
)

st.markdown(f"**Found {len(invoices)} invoice(s)**")

if invoices:
    # Convert all invoices to INR for preview
    converted_list = [currency_service.convert_invoice(inv, target_currency="INR", mode="historical") for inv in invoices]
    df = pd.DataFrame(converted_list)
    df["Original Total"] = df.apply(
        lambda r: format_currency_amount(r["total_amount"], r["currency"]), axis=1
    )
    df["INR Equivalent"] = df.apply(
        lambda r: currency_service.format_currency(r["converted_amount"], "INR")
        if pd.notna(r.get("converted_amount")) and r.get("converted_amount") is not None
        else "—",
        axis=1,
    )

    # Main interactive table
    cols_to_show = ["id", "invoice_number", "vendor_name", "invoice_date", "due_date", "Original Total", "INR Equivalent", "payment_status", "status"]
    df_display = df[cols_to_show].copy()
    df_display.columns = ["ID", "Invoice #", "Vendor", "Invoice Date", "Due Date", "Original Total", "INR Equivalent", "Payment Status", "Status"]

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Invoice Inspector & Document Actions")

    # Select an invoice to inspect
    def _safe_format_option(r):
        orig = format_currency_amount(r['total_amount'], r['currency'])
        conv = (
            currency_service.format_currency(r['converted_amount'], 'INR')
            if pd.notna(r.get('converted_amount')) and r.get('converted_amount') is not None
            else "—"
        )
        return f"#{r['id']} - {r['invoice_number'] or 'N/A'} ({r['vendor_name'] or 'Unknown'}) [{orig} | {conv}]"

    invoice_options = {
        _safe_format_option(r): r["id"]
        for r in converted_list
    }
    selected_label = st.selectbox("Select an invoice to inspect details & preview:", options=list(invoice_options.keys()))
    selected_id = invoice_options[selected_label]

    invoice = db.get_invoice_by_id(selected_id)
    if invoice:
        detail_c1, detail_c2 = st.columns([1.2, 1])

        with detail_c1:
            st.markdown(f"### Details: {invoice.get('vendor_name') or 'Unknown'}")

            # Duplicate Warning & Review Actions
            if invoice.get("is_duplicate") == 1 or invoice.get("status") == "suspected_duplicate":
                st.warning(
                    f"**SUSPECTED DUPLICATE INVOICE**\n\n"
                    f"**Reason:** {invoice.get('duplicate_reason', 'Flagged as duplicate.')}\n\n"
                    f"- **Original Record ID:** `#{invoice.get('duplicate_of_id') or 'N/A'}`\n"
                    f"- **Financial Reporting:** *Excluded from spending totals to prevent duplicate counting.*\n"
                )
                dup_btn_col1, dup_btn_col2 = st.columns(2)
                with dup_btn_col1:
                    if st.button("Mark as Genuine (Include in Reports)", key=f"gen_{selected_id}", type="primary"):
                        db.mark_invoice_genuine(selected_id)
                        st.success(f"Invoice #{selected_id} marked as genuine and verified.")
                        st.rerun()
                with dup_btn_col2:
                    if st.button("Confirm as Duplicate (Keep Excluded)", key=f"dup_{selected_id}"):
                        db.mark_invoice_duplicate(selected_id, invoice.get("duplicate_of_id"), invoice.get("duplicate_reason"))
                        st.info(f"Invoice #{selected_id} confirmed as duplicate.")
                        st.rerun()
                st.markdown("---")

            # Multi-Currency Valuation Box (INR)
            conv_inv = currency_service.convert_currency(
                amount=invoice.get("total_amount"),
                from_currency=invoice.get("currency", "USD"),
                to_currency="INR",
                date=invoice.get("invoice_date"),
                mode="historical",
            )
            with st.container():
                st.info(
                    f"**Multi-Currency Valuation (INR)**\n\n"
                    f"- **Original Amount:** `{format_currency_amount(invoice.get('total_amount'), invoice.get('currency'))} {invoice.get('currency', 'USD')}`\n"
                    f"- **Converted Amount:** approximately **{currency_service.format_currency(conv_inv.converted_amount, 'INR')} INR**\n"
                    f"- **Exchange Rate:** `1 {conv_inv.from_currency} = {currency_service.format_currency(conv_inv.exchange_rate, 'INR', is_rate=True)}`\n"
                    f"- **Rate Date:** `{invoice.get('invoice_date') or 'N/A'}` (Effective: `{conv_inv.effective_date}`)\n"
                    f"- **Source:** *{conv_inv.source}*\n\n"
                    f"*(Note: Converted values represent estimated reference equivalents and do not represent confirmed settlements unless backed by payment receipts)*"
                )
                if conv_inv.warning:
                    st.warning(conv_inv.warning)

            st.markdown(
                f"""
                - **Invoice Number:** `{invoice.get('invoice_number') or 'N/A'}`
                - **Customer Name:** {invoice.get('customer_name') or 'N/A'}
                - **Invoice Date:** {invoice.get('invoice_date') or 'N/A'}
                - **Payment Due Date:** {invoice.get('due_date') or 'N/A'}
                - **Payment Status:** `{invoice.get('payment_status') or 'Unspecified'}`
                - **Subtotal:** {format_currency_amount(invoice.get('subtotal'), invoice.get('currency'))}
                - **Tax Amount:** {format_currency_amount(invoice.get('tax_amount'), invoice.get('currency'))}
                - **Grand Total:** **{format_currency_amount(invoice.get('total_amount'), invoice.get('currency'))}**
                - **Processing Status:** `{invoice.get('status')}`
                - **Is Duplicate:** `{'Yes (Excluded)' if invoice.get('is_duplicate') else 'No (Eligible)'}`
                - **Source File:** `{Path(invoice.get('source_file_path', '')).name}`
                - **File Hash (SHA-256):** `{invoice.get('file_hash')}`
                """
            )

            # Line Items Table
            line_items = invoice.get("line_items", [])
            if line_items:
                st.markdown("#### Line Items")
                df_items = pd.DataFrame(line_items)[["description", "quantity", "unit_price", "amount"]]
                df_items.columns = ["Description", "Quantity", "Unit Price", "Amount"]
                st.dataframe(df_items, use_container_width=True, hide_index=True)

            # Confidence Scores & Notes
            with st.expander("Confidence Metrics & Extraction Notes"):
                st.json(invoice.get("confidence_scores", {}))
                notes = invoice.get("extraction_notes", [])
                if notes:
                    for note in notes:
                        st.info(note)

            # Action Buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Reprocess This Invoice", key=f"reproc_btn_{selected_id}"):
                    source_path = Path(invoice.get("source_file_path", ""))
                    if source_path.exists():
                        res = InvoiceProcessingPipeline.process_file(source_path, force_reprocess=True)
                        st.success(f"Reprocessed successfully: Status is {res.get('status')}")
                        st.rerun()
                    else:
                        st.error(f"Source file not found at: {source_path}")

            with btn_col2:
                if st.button("Delete Invoice", key=f"del_btn_{selected_id}", type="secondary"):
                    deleted_hash = db.delete_invoice(selected_id)
                    st.warning(f"Deleted invoice #{selected_id} from database.")
                    st.rerun()

        with detail_c2:
            st.markdown("### Document PDF Preview")
            source_file = Path(invoice.get("source_file_path", ""))
            if source_file.exists():
                try:
                    with open(source_file, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Cannot render PDF preview: {e}")
            else:
                st.warning(f"Original PDF file is not present on disk: `{source_file}`")
else:
    st.info("No invoices match your current search or filter criteria.")

