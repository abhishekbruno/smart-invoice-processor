import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st

from config.settings import settings
from core.database import db
from core.folder_monitor import folder_monitor
from core.gmail_auth_service import gmail_auth_service
from core.gmail_sync_service import gmail_sync_service
from core.vector_store import vector_store

st.set_page_config(page_title="Automation | Smart Invoice Processor", layout="wide")

st.title("RPA & Pipeline Automation")
st.caption("Manage folder watchers, cloud Gmail RPA inbox synchronization, vector database indexing, and audit logs.")

# =============================================================================
# 1. Gmail RPA Automation
# =============================================================================
st.subheader("Gmail RPA Inbox Automation (OAuth 2.0)")
st.caption("Automatically scan your Gmail inbox for supplier invoices, download PDF attachments, and ingest them directly into SQLite and ChromaDB.")

auth_info = gmail_auth_service.get_auth_status()
is_auth = auth_info.get("is_authenticated", False)
is_cfg = auth_info.get("is_configured", False)
conn_email = auth_info.get("connected_email")
last_sync = auth_info.get("last_synced_at")

gmail_col1, gmail_col2 = st.columns([1.5, 2.5])

with gmail_col1:
    if is_auth:
        st.success(f"**Connected to Gmail**\n\n**Account:** `{conn_email or 'Authorized User'}`\n\n**Last Synced:** `{last_sync or 'Never'}`")
        if st.button("Disconnect Gmail Account", key="disconnect_gmail_btn"):
            gmail_auth_service.disconnect()
            st.info("Gmail account disconnected.")
            st.rerun()
    elif not is_cfg:
        st.warning("**OAuth Credentials Missing**")
        st.caption(
            f"Save your desktop client `credentials.json` into `{settings.GMAIL_CREDENTIALS_FILE}` to enable Gmail automation."
        )
    else:
        st.info("**Gmail Disconnected / Authorization Required**")
        if st.button("Authorize Gmail Account", key="auth_gmail_btn"):
            with st.spinner("Opening browser for OAuth consent..."):
                ok, msg = gmail_auth_service.authenticate_desktop_flow()
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

with gmail_col2:
    query_input = st.text_input(
        "Gmail Search Query",
        value=settings.GMAIL_SEARCH_QUERY,
        help="Standard Gmail search syntax (e.g., has:attachment filename:pdf label:invoices)",
    )
    max_msgs = st.slider("Max Messages to Inspect per Run", min_value=5, max_value=100, value=25, step=5)

    g_btn1, g_btn2 = st.columns(2)
    with g_btn1:
        sync_now_disabled = not is_auth or gmail_sync_service.is_running_sync
        if st.button("🔄 Sync Gmail Invoices Now", disabled=sync_now_disabled, key="sync_gmail_now"):
            with st.spinner("Connecting to Gmail and collecting invoice attachments..."):
                res = gmail_sync_service.run_sync(query=query_input, max_messages=max_msgs)
                if res.get("status") in ("success", "partial"):
                    st.success(
                        f"Sync completed! Scanned: {res.get('messages_scanned')}, "
                        f"Found: {res.get('attachments_found')}, "
                        f"Imported: {res.get('invoices_imported')}, "
                        f"Duplicates Skipped: {res.get('duplicates_skipped')}."
                    )
                else:
                    st.error(f"Sync error: {res.get('error', 'Unknown issue')}")
            st.rerun()

    with g_btn2:
        is_bg_on = gmail_sync_service.is_background_sync_running
        if is_bg_on:
            st.caption("Background poller is currently active (every 15 mins).")
            if st.button("Stop Periodic Poller", key="stop_bg_gmail"):
                gmail_sync_service.stop_background_sync()
                st.rerun()
        else:
            st.caption("Background poller is currently idle.")
            if st.button("Start Periodic Poller (15m)", disabled=not is_auth, key="start_bg_gmail"):
                gmail_sync_service.start_background_sync(interval_minutes=15)
                st.rerun()

# Gmail Sync History Table
with st.expander("Recent Gmail Synchronization Runs", expanded=False):
    sync_logs = db.get_recent_sync_history(limit=10)
    if sync_logs:
        df_sync = pd.DataFrame(sync_logs)
        df_sync_display = df_sync[[
            "id", "started_at", "status", "messages_scanned",
            "attachments_found", "invoices_imported", "duplicates_skipped", "failed_count"
        ]].copy()
        df_sync_display.columns = [
            "Run ID", "Started At", "Status", "Messages Scanned",
            "Attachments Found", "Imported", "Duplicates Skipped", "Failures"
        ]
        st.dataframe(df_sync_display, use_container_width=True, hide_index=True)
    else:
        st.caption("No Gmail synchronization events recorded yet.")

st.markdown("---")

# =============================================================================
# 2. Local Folder Monitoring Controls
# =============================================================================
st.subheader("Monitored Folder Configuration (RPA Watcher)")
st.write(f"**Target Watch Folder:** `{settings.INVOICE_WATCH_DIR.resolve()}`")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1.5, 3])

with col_ctrl1:
    is_running = folder_monitor.is_running
    if is_running:
        st.success("**Monitoring Active** (Watchdog running)")
        if st.button("Stop Folder Monitor", key="stop_monitor_btn"):
            folder_monitor.stop()
            st.rerun()
    else:
        st.warning("**Monitoring Idle** (Not watching)")
        if st.button("Start Folder Monitor", key="start_monitor_btn"):
            folder_monitor.start()
            st.rerun()

with col_ctrl2:
    if st.button("Run Folder Scan Now", help="Scans the watch directory for any un-processed or newly added PDFs"):
        with st.spinner("Scanning watch folder..."):
            results = folder_monitor.scan_folder_now()
        successes = sum(1 for r in results if r.get("status") == "success")
        dups = sum(1 for r in results if r.get("status") == "duplicate")
        fails = sum(1 for r in results if r.get("status") == "failed")
        st.success(f"Scan complete: {successes} new, {dups} duplicates, {fails} failed.")
        st.rerun()

with col_ctrl3:
    st.info(
        "When active, any PDF dropped into `data/invoices/` is automatically detected, "
        "validated, extracted, and cataloged into SQLite and ChromaDB without manual intervention."
    )

st.markdown("---")

# =============================================================================
# 3. Vector Index Management (ChromaDB)
# =============================================================================
st.subheader("Vector Database Index Management")
st.caption("Synchronize extracted invoices with the persistent ChromaDB collection for semantic RAG retrieval.")

v_stats = vector_store.get_stats()
all_invoices = db.get_all_invoices(include_duplicates=False)
total_inv_count = len(all_invoices)
indexed_inv_count = v_stats.get("unique_invoices_indexed", 0)
total_chunks = v_stats.get("total_chunks", 0)

v_col1, v_col2, v_col3, v_col4 = st.columns(4)
with v_col1:
    st.metric("Eligible Invoices in SQLite", total_inv_count)
with v_col2:
    st.metric("Invoices Indexed in ChromaDB", indexed_inv_count)
with v_col3:
    st.metric("Total Vector Chunks", total_chunks)
with v_col4:
    unindexed_cnt = max(0, total_inv_count - indexed_inv_count)
    st.metric(
        "Unindexed Invoices",
        unindexed_cnt,
        delta=f"{unindexed_cnt} pending" if unindexed_cnt > 0 else "Fully synced",
        delta_color="inverse" if unindexed_cnt > 0 else "normal",
    )

btn_c1, btn_c2, btn_c3 = st.columns([1.5, 1.5, 3])

with btn_c1:
    if st.button("Index Unindexed Invoices", help="Indexes any database invoices not yet in ChromaDB"):
        with st.spinner("Indexing unindexed invoices..."):
            res = vector_store.index_unindexed(db)
            st.success(f"Indexed {res.get('invoices_indexed', 0)} invoice(s) ({res.get('total_chunks', 0)} chunks).")
            st.rerun()

with btn_c2:
    if st.button("Reindex All Invoices", help="Rebuilds vector chunks for all database invoices"):
        with st.spinner("Reindexing all invoices into ChromaDB..."):
            res = vector_store.reindex_all(db, force=True)
            st.success(f"Reindexed {res.get('invoices_indexed', 0)} invoices ({res.get('total_chunks', 0)} chunks).")
            st.rerun()

with btn_c3:
    st.caption(
        "Indexed vector chunks allow natural-language questions (e.g., 'What services did AWS bill for?') "
        "to retrieve precise line items and invoice clauses."
    )

st.markdown("---")

# =============================================================================
# 4. Automation Activity & Processing Logs
# =============================================================================
st.subheader("📋 Processing Audit Trail")
filter_col1, filter_col2 = st.columns([1, 3])

with filter_col1:
    log_status = st.selectbox("Filter Status", options=["All", "success", "duplicate", "needs_review", "failed"])

logs = db.get_processing_logs(limit=100)
if logs:
    df_logs = pd.DataFrame(logs)
    if log_status != "All":
        df_logs = df_logs[df_logs["status"] == log_status]

    if not df_logs.empty:
        df_logs["duration_sec"] = df_logs["duration_sec"].apply(lambda d: f"{d:.2f}s")
        df_logs_display = df_logs[["id", "file_name", "status", "duration_sec", "error_message", "processed_at"]].copy()
        df_logs_display.columns = ["Log ID", "File Name", "Status", "Duration", "Notes / Error", "Timestamp"]
        st.dataframe(df_logs_display, use_container_width=True, hide_index=True)
    else:
        st.info(f"No log records with status '{log_status}'.")
else:
    st.info("No processing events recorded yet.")
