import os
import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config.settings import settings
from core.database import db
from core.folder_monitor import folder_monitor
from utils.helpers import format_currency_amount

st.set_page_config(
    page_title="Smart Invoice Processor",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling - High contrast dark & light mode friendly
st.markdown(
    """
    <style>
    /* Aovix Dark Obsidian & Violet Theme */
    .stApp {
        background-color: #020203;
        color: #F1F1F1;
        background-image: radial-gradient(circle at 50% 0%, rgba(75, 55, 178, 0.08) 0%, transparent 60%);
        background-repeat: no-repeat;
    }
    [data-testid="stSidebar"] {
        background-color: #040406;
        border-right: 1px solid #1A1625;
    }
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F1F1F1;
        letter-spacing: -0.03em;
        margin-bottom: 0.35rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #72707D;
        margin-bottom: 1.75rem;
        font-weight: 400;
    }
    .metric-card {
        background-color: #08070B;
        border: 1px solid #1A1625;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        border-color: #2D2740;
    }
    .metric-title {
        font-size: 0.72rem;
        color: #72707D;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .metric-value {
        font-size: 1.85rem;
        color: #F1F1F1;
        font-weight: 700;
        margin-top: 6px;
        font-feature-settings: "tnum";
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-warning {
        background-color: rgba(146, 63, 83, 0.18);
        color: #F43F5E;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-running {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .status-stopped {
        background-color: rgba(114, 112, 125, 0.15);
        color: #B7B7B9;
        border: 1px solid #1A1625;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar System Health & Info
with st.sidebar:
    st.markdown("### System Overview")
    monitor_active = folder_monitor.is_running
    if monitor_active:
        st.markdown(
            '<div class="status-pill status-running">● Folder Monitor Active</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-pill status-stopped">○ Folder Monitor Idle</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    counts = db.get_invoice_counts()
    st.metric("Total Invoices", counts["total"])
    st.metric("Needs Review", counts["needs_review"])

    st.markdown("---")
    st.caption(f"Watch Folder: `{settings.INVOICE_WATCH_DIR.name}/`")
    st.caption(f"Database: `{settings.DB_PATH.name}`")
    st.caption(f"Timezone: `{settings.TIMEZONE}`")

# Main Page Header
st.markdown('<div class="main-header">Smart Invoice Processor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated Robotic Process Automation (RPA), Document Intelligence & Natural Language Analytics</div>',
    unsafe_allow_html=True,
)

# Quick Metric Highlights
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Invoices</div>
            <div class="metric-value">{counts["total"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Processed</div>
            <div class="metric-value">{counts["processed"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Needs Review</div>
            <div class="metric-value" style="color: {'#ef4444' if counts['needs_review'] > 0 else 'var(--text-color, #f8fafc)'};">
                {counts["needs_review"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Verified</div>
            <div class="metric-value">{counts["verified"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Quick Action Cards
st.markdown("### Quick Navigation")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.info("**Dashboard**\n\nMonthly spending trends, vendor distribution, and INR valuation.")
    st.page_link("pages/1_Dashboard.py", label="Open Dashboard")

with nav_col2:
    st.success("**Ask AI & RAG**\n\nNatural language invoice Q&A with grounded citations.")
    st.page_link("pages/4_Ask_AI.py", label="Chat with Invoices")

with nav_col3:
    st.warning("**RPA Automation**\n\nGmail inbox synchronization and local folder monitoring.")
    st.page_link("pages/5_Automation.py", label="Manage Automation")

with nav_col4:
    st.info("**Reports & Export**\n\nDownload CSV, Excel, and PDF financial summary reports.")
    st.page_link("pages/7_Reports.py", label="Generate Reports")

st.markdown("---")

# Recent Processing Summary
st.markdown("### Recently Processed Invoices")
recent_invoices = db.get_recently_processed_invoices(limit=5)
if recent_invoices:
    import pandas as pd
    df_recent = pd.DataFrame(recent_invoices)
    df_recent["Amount"] = df_recent.apply(
        lambda r: format_currency_amount(r["total_amount"], r["currency"]), axis=1
    )
    df_display = df_recent[["invoice_number", "vendor_name", "invoice_date", "Amount", "status", "created_at"]]
    df_display.columns = ["Invoice #", "Vendor", "Invoice Date", "Amount", "Status", "Processed At"]
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No invoices processed yet. Navigate to 'Upload Invoices' or copy PDFs into `data/invoices/`.")

