import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config.settings import settings
from core.database import db
from core.folder_monitor import InvoiceProcessingPipeline
from core.invoice_parser import invoice_parser
from core.pdf_extractor import pdf_extractor
from utils.helpers import format_currency_amount
from utils.validators import calculate_file_hash, sanitize_filename, validate_pdf_file

st.set_page_config(page_title="Upload Invoices | Smart Invoice Processor", layout="wide")

st.title("Upload & Process Invoices")
st.caption("Upload invoice PDF files for instant text extraction, field detection, and structured storage.")

# File Uploader
uploaded_files = st.file_uploader(
    "Choose PDF invoices to upload",
    type=["pdf"],
    accept_multiple_files=True,
    help=f"Select one or more PDF files (Maximum size: {settings.MAX_FILE_SIZE_MB}MB each).",
)

if uploaded_files:
    st.subheader(f"Processing {len(uploaded_files)} File(s)")

    for uploaded_file in uploaded_files:
        clean_name = sanitize_filename(uploaded_file.name)
        file_bytes = uploaded_file.getvalue()

        # Step 1: Validate file
        is_valid, err_msg = validate_pdf_file(file_bytes, original_name=clean_name)
        if not is_valid:
            st.error(f"❌ **{clean_name}**: Validation failed - {err_msg}")
            continue

        file_hash = calculate_file_hash(file_bytes)

        # Check duplicate
        is_dup = db.is_duplicate(file_hash)
        if is_dup:
            st.warning(f"⚠️ **{clean_name}**: Already processed in the system. (SHA-256: `{file_hash[:10]}...`)")
            col_a, col_b = st.columns([1, 4])
            with col_a:
                reprocess = st.button(f"Force Reprocess {clean_name}", key=f"reproc_{file_hash}")
            if not reprocess:
                continue

        # Save to watch directory / processed directory
        target_path = settings.INVOICE_WATCH_DIR / clean_name
        with open(target_path, "wb") as f:
            f.write(file_bytes)

        with st.spinner(f"Extracting fields from {clean_name}..."):
            result = InvoiceProcessingPipeline.process_file(
                target_path,
                force_reprocess=True if is_dup else False,
            )

        if result["status"] in ("success", "needs_review"):
            invoice_id = result.get("invoice_id")
            invoice_details = db.get_invoice_by_id(invoice_id) if invoice_id else None

            if result["status"] == "needs_review":
                st.warning(f"⚠️ **{clean_name}** processed with review warnings: {', '.join(result.get('notes', []))}")
            else:
                st.success(f"✅ **{clean_name}** successfully extracted & stored (ID: #{invoice_id})!")

            if invoice_details:
                # Invoice Review & Correction Expander
                with st.expander(f"🔍 Preview & Verify Data: {clean_name}", expanded=True):
                    with st.form(key=f"edit_form_{invoice_id}"):
                        st.markdown("#### Verify Extracted Information")
                        c1, c2, c3 = st.columns(3)

                        with c1:
                            val_vendor = st.text_input("Vendor Name", value=invoice_details.get("vendor_name") or "")
                            val_inv_num = st.text_input("Invoice Number", value=invoice_details.get("invoice_number") or "")
                            val_customer = st.text_input("Customer Name", value=invoice_details.get("customer_name") or "")

                        with c2:
                            val_inv_date = st.text_input("Invoice Date (YYYY-MM-DD)", value=invoice_details.get("invoice_date") or "")
                            val_due_date = st.text_input("Due Date (YYYY-MM-DD)", value=invoice_details.get("due_date") or "")
                            val_status = st.selectbox(
                                "Payment Status",
                                options=["PAID", "PENDING", "OVERDUE", "DUE UPON RECEIPT", "UNPAID", "None"],
                                index=["PAID", "PENDING", "OVERDUE", "DUE UPON RECEIPT", "UNPAID", "None"].index(
                                    invoice_details.get("payment_status") or "None"
                                ),
                            )

                        with c3:
                            val_currency = st.selectbox(
                                "Currency",
                                options=["USD", "EUR", "GBP", "INR", "CAD", "AUD"],
                                index=["USD", "EUR", "GBP", "INR", "CAD", "AUD"].index(
                                    invoice_details.get("currency") or "USD"
                                ),
                            )
                            val_subtotal = st.number_input(
                                "Subtotal",
                                value=float(invoice_details.get("subtotal") or 0.0),
                                step=10.0,
                                format="%.2f",
                            )
                            val_tax = st.number_input(
                                "Tax Amount",
                                value=float(invoice_details.get("tax_amount") or 0.0),
                                step=5.0,
                                format="%.2f",
                            )
                            val_total = st.number_input(
                                "Total Amount",
                                value=float(invoice_details.get("total_amount") or 0.0),
                                step=10.0,
                                format="%.2f",
                            )

                        # Line items table display
                        line_items = invoice_details.get("line_items", [])
                        if line_items:
                            st.markdown("##### Extracted Line Items")
                            import pandas as pd
                            df_items = pd.DataFrame(line_items)[["description", "quantity", "unit_price", "amount"]]
                            df_items.columns = ["Description", "Quantity", "Unit Price", "Total Amount"]
                            st.dataframe(df_items, use_container_width=True, hide_index=True)

                        submit_btn = st.form_submit_button("💾 Save Verified Invoice")
                        if submit_btn:
                            update_fields = {
                                "vendor_name": val_vendor,
                                "invoice_number": val_inv_num,
                                "customer_name": val_customer,
                                "invoice_date": val_inv_date,
                                "due_date": val_due_date,
                                "currency": val_currency,
                                "subtotal": val_subtotal,
                                "tax_amount": val_tax,
                                "total_amount": val_total,
                                "payment_status": None if val_status == "None" else val_status,
                                "status": "verified",
                            }
                            db.update_invoice(invoice_id, update_fields)
                            st.success(f"Invoice #{invoice_id} successfully updated and marked as Verified!")
                            st.rerun()
        else:
            st.error(f"❌ Failed to process {clean_name}: {result.get('error')}")

st.markdown("---")
st.subheader("💡 Need sample invoices?")
if st.button("Generate & Load 12 Realistic Sample Invoices into Watch Folder"):
    from scripts.generate_sample_invoices import generate_all_samples
    samples = generate_all_samples(target_dir=settings.INVOICE_WATCH_DIR)
    st.success(f"Generated {len(samples)} sample invoice PDFs in `{settings.INVOICE_WATCH_DIR.name}/`!")
    results = InvoiceProcessingPipeline.process_file(samples[0])
    st.info("Head to the Automation page or Dashboard to view the newly ingested sample invoices.")

