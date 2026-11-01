import os
import shutil
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
from core.embedding_service import embedding_service
from core.gemini_service import gemini_service
from core.gmail_auth_service import gmail_auth_service
from core.pdf_extractor import pdf_extractor
from core.vector_store import vector_store

st.set_page_config(page_title="Settings | Smart Invoice Processor", layout="wide")

st.title("System Configuration & Diagnostics")
st.caption("Review storage engines, vector indexing health, Google Gemini API status, OCR capabilities, and upcoming integrations.")

# 1. Directories & Storage Paths
st.subheader("Storage Directories")
col1, col2 = st.columns(2)

with col1:
    st.text_input("Watch Directory (`INVOICE_WATCH_DIR`)", value=str(settings.INVOICE_WATCH_DIR.resolve()), disabled=True)
    st.text_input("Archive Directory (`PROCESSED_DIR`)", value=str(settings.PROCESSED_DIR.resolve()), disabled=True)
    st.text_input("Samples Directory", value=str(settings.SAMPLES_DIR.resolve()), disabled=True)

with col2:
    st.text_input("SQLite Database File (`DB_PATH`)", value=str(settings.DB_PATH.resolve()), disabled=True)
    st.text_input("ChromaDB Vector Store (`CHROMA_DIR`)", value=str(settings.CHROMA_DIR.resolve()), disabled=True)
    st.text_input("Log Directory (`LOGS_DIR`)", value=str(settings.LOGS_DIR.resolve()), disabled=True)

st.markdown("---")

# 2. Multi-Currency Preferences & Exchange Rate Diagnostics
st.subheader("Multi-Currency & Valuation Preferences")
curr_c1, curr_c2 = st.columns([1.5, 2.5])

with curr_c1:
    saved_pref = db.get_setting("preferred_display_currency", "INR")
    pref_options = ["INR", "USD", "EUR", "GBP"]
    selected_pref = st.selectbox(
        "Preferred Display Currency",
        options=pref_options,
        index=pref_options.index(saved_pref) if saved_pref in pref_options else 0,
        help="Controls the primary currency used for converted dashboard summaries and reports.",
    )
    if selected_pref != saved_pref:
        db.set_setting("preferred_display_currency", selected_pref)
        st.success(f"Preferred currency updated to {selected_pref}!")
        st.rerun()

with curr_c2:
    cached_rates = db.get_all_cached_rates()
    st.markdown(
        f"""
        - **Active API Provider:** `Frankfurter API v2 (api.frankfurter.dev)`
        - **Benchmark Authority:** `European Central Bank (ECB) Reference Rates`
        - **Persistent SQLite Cache:** `{len(cached_rates)} daily reference rates stored`
        - **Offline Fallback Guarantee:** `Active (safe ECB baseline)`
        """
    )

# Latest Reference Rates Table
st.markdown("##### Live Reference Exchange Rates (Base: USD)")
try:
    latest_info = currency_service.get_latest_rates(base_currency="USD")
    rates_data = [
        {"Currency": curr, "Rate per 1 USD": float(rate), "Effective Date": latest_info["effective_date"], "Source": latest_info["source"]}
        for curr, rate in latest_info["rates"].items()
    ]
    st.dataframe(pd.DataFrame(rates_data), use_container_width=True, hide_index=True)
except Exception as e:
    st.warning(f"Could not load live rates: {e}")

st.markdown("---")

# 2. Vector Store & Embedding Status
st.subheader("Vector Database & Embedding Diagnostics")
v_stats = vector_store.get_stats()
ai_col1, ai_col2 = st.columns(2)

with ai_col1:
    st.markdown("##### Embedding Model (Sentence Transformers)")
    st.text_input("Model Identifier", value=settings.EMBEDDING_MODEL, disabled=True)
    st.markdown(
        f"""
        - **Embedding Dimension:** `{embedding_service.dimension}`
        - **Model Loaded in Memory:** `{'Yes' if embedding_service.is_loaded else 'Lazy (loads on first search/index)'}`
        - **Execution Hardware:** `CPU (optimized for cloud & local compatibility)`
        """
    )

with ai_col2:
    st.markdown("##### ChromaDB Collection Metrics")
    st.text_input("Collection Name", value=vector_store.collection_name, disabled=True)
    st.markdown(
        f"""
        - **Total Stored Chunks:** `{v_stats.get('total_chunks', 0)}`
        - **Unique Invoices Indexed:** `{v_stats.get('unique_invoices_indexed', 0)}`
        - **ChromaDB Path:** `{v_stats.get('storage_directory', '')}`
        """
    )

# Vector synchronization actions
v_btn1, v_btn2 = st.columns([1.5, 3])
with v_btn1:
    if st.button("Sync & Reindex All into ChromaDB"):
        with st.spinner("Reindexing invoices..."):
            res = vector_store.reindex_all(db, force=True)
            st.success(f"Indexed {res.get('invoices_indexed')} invoices ({res.get('total_chunks')} chunks)!")
            st.rerun()

st.markdown("---")

# 3. Google Gemini API Status
st.subheader("Google Gemini API Integration")
gemini_health = gemini_service.check_health()
g_col1, g_col2 = st.columns([1.2, 1.8])

with g_col1:
    if gemini_health.get("is_available"):
        active_m = gemini_health.get("active_model") or gemini_health.get("configured_model")
        st.success(f"**Gemini API Online & Authenticated**\n\nActive Model: `{active_m}`")
    elif gemini_health.get("status") == "missing_key":
        st.warning("**Gemini API Key Missing**\n\nAdd `GEMINI_API_KEY=...` to your `.env` file.")
    else:
        st.error(f"**Connection Error**\n\n{gemini_health.get('error', 'Unable to reach Gemini API.')}")

with g_col2:
    st.text_input("Configured Model", value=settings.GEMINI_MODEL, disabled=True)
    key_configured = gemini_service.is_configured
    st.text_input("API Key Status", value="Configured (Hidden for security)" if key_configured else "Not Set", disabled=True)

    test_conn_btn = st.button("Test Gemini API Connection", key="test_gemini_btn")
    if test_conn_btn:
        with st.spinner("Pinging Google Gemini API..."):
            test_health = gemini_service.check_health()
            if test_health.get("is_available"):
                try:
                    resp = gemini_service.generate("Say Connected in one word.")
                    st.success(f"Connection successful! Model response: *{resp}*")
                except Exception as test_e:
                    st.error(f"API call failed: {test_e}")
            else:
                st.error(f"Test failed: {test_health.get('error')}")

st.markdown("---")

# 4. OCR Diagnostics
st.subheader("OCR Engine Status")
ocr_c1, ocr_c2 = st.columns([1, 2])

with ocr_c1:
    if pdf_extractor.is_ocr_supported:
        st.success("✅ **Tesseract OCR Found & Ready**")
    else:
        st.warning("⚠️ **Tesseract OCR Not Detected**")
        st.caption("Standard text-based PDFs extract directly via PyMuPDF. For scanned image-only PDFs, install Tesseract OCR on Windows.")

with ocr_c2:
    st.markdown(
        """
        - **OCR Enabled in Config:** `{}`
        - **Configured Tesseract Path:** `{}`
        - **Auto-detected binary:** `{}`
        """.format(
            settings.OCR_ENABLED,
            settings.TESSERACT_PATH or "Default PATH lookup",
            shutil.which("tesseract") or "None",
        )
    )

st.markdown("---")

# 5. Gmail RPA Automation Diagnostics
st.subheader("📬 Gmail RPA Automation Diagnostics")
st.caption("Official Google Workspace Gmail API integration using Desktop OAuth 2.0 with read-only scopes.")

g_status = gmail_auth_service.get_auth_status()
g_col1, g_col2 = st.columns([1.2, 1.8])

with g_col1:
    if g_status.get("is_authenticated"):
        st.success(f"🟢 **Gmail Authenticated**\n\nConnected: `{g_status.get('connected_email') or 'Authorized Account'}`")
        if st.button("🔌 Disconnect Gmail Account", key="settings_disconnect_gmail"):
            gmail_auth_service.disconnect()
            st.rerun()
    elif not g_status.get("is_configured"):
        st.warning("⚠️ **Credentials File Not Found**\n\nPlace your OAuth 2.0 Desktop credentials at `config/credentials.json`.")
    else:
        st.info("⚪ **Configured, Pending Authorization**")
        if st.button("🔐 Authorize Gmail (Desktop Flow)", key="settings_auth_gmail"):
            with st.spinner("Starting OAuth flow..."):
                ok, msg = gmail_auth_service.authenticate_desktop_flow()
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

with g_col2:
    st.text_input("OAuth Scope", value=g_status.get("scope", "https://www.googleapis.com/auth/gmail.readonly"), disabled=True)
    st.text_input("Credentials Path", value=g_status.get("credentials_path", ""), disabled=True)
    st.text_input("Token Path", value=g_status.get("token_path", ""), disabled=True)

    if g_status.get("is_authenticated"):
        if st.button("🧪 Test Gmail API Connection", key="test_gmail_api"):
            with st.spinner("Testing Gmail connection..."):
                profile = gmail_auth_service.get_user_profile()
                if profile:
                    st.success(f"✅ Connection verified! Email: {profile.get('emailAddress')} (Total Messages: {profile.get('messagesTotal', 'N/A')})")
                else:
                    st.error("Failed to fetch Gmail profile.")
