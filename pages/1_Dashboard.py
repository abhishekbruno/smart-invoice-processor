import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from utils.helpers import format_currency_amount

st.set_page_config(page_title="Dashboard | Smart Invoice Processor", layout="wide")

st.title("Financial & Extraction Dashboard")
st.caption("Real-time expense intelligence, vendor breakdowns, and document status metrics.")

# 1. Currency Conversion Controls & Preferences
pref_curr_saved = db.get_setting("preferred_display_currency", "INR")
ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1.5, 2.5, 2])

with ctrl_c1:
    display_currency = st.selectbox(
        "Preferred Display Currency",
        options=["INR", "USD", "EUR", "GBP"],
        index=["INR", "USD", "EUR", "GBP"].index(pref_curr_saved) if pref_curr_saved in ["INR", "USD", "EUR", "GBP"] else 0,
        key="dashboard_display_currency",
    )

with ctrl_c2:
    mode_selection = st.radio(
        "Conversion Rate Mode",
        options=["Historical Rate (Invoice Date)", "Latest Available Rate"],
        index=0,
        horizontal=True,
        key="dashboard_rate_mode",
    )
    mode = "historical" if "Historical" in mode_selection else "latest"

with ctrl_c3:
    st.caption("Exchange Rate Source:")
    st.markdown(f"**{currency_service.SOURCE_LABEL}**")

# Calculate Aggregated Converted Analytics
agg_spending = currency_service.get_aggregated_spending(
    target_currency=display_currency,
    mode=mode,
    include_duplicates=False,
)

# 2. Converted Grand Total & Exchange Rate Information Banner
banner_c1, banner_c2 = st.columns([1.8, 3.2])

with banner_c1:
    st.metric(
        label=f"Total Eligible Spend ({display_currency}) — {mode.capitalize()} Rates",
        value=agg_spending["formatted_total"],
        delta=f"{agg_spending['invoice_count']} eligible invoices",
        delta_color="normal",
    )

with banner_c2:
    eff_note = "daily reference rates on each invoice's issue date" if mode == "historical" else "the latest available European Central Bank daily rates"
    st.info(
        f"**Multi-Currency Valuation Notice ({display_currency}):**\n"
        f"All {agg_spending['invoice_count']} eligible non-duplicate invoices are converted using {eff_note}. "
        f"Suspected duplicates are excluded from calculations. "
        f"*Note: Converted values represent estimated reference equivalents and do not represent confirmed transaction settlements unless backed by payment receipts.*"
    )

st.markdown("---")

# 3. KPI Cards Row
counts = db.get_invoice_counts()
totals_by_curr = db.get_total_expenses()

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric(label="Total Invoices in DB", value=counts["total"])

with kpi_col2:
    st.metric(label="Processed Cleanly", value=counts["processed"])

with kpi_col3:
    st.metric(
        label="Requires Manual Review",
        value=counts["needs_review"],
        delta=f"{counts['needs_review']} items" if counts["needs_review"] > 0 else "All clear",
        delta_color="inverse",
    )

with kpi_col4:
    dup_cnt = counts.get("suspected_duplicate", 0)
    st.metric(
        label="Suspected Duplicates",
        value=dup_cnt,
        delta=f"{dup_cnt} excluded" if dup_cnt > 0 else "0",
        delta_color="inverse" if dup_cnt > 0 else "normal",
    )

if counts.get("suspected_duplicate", 0) > 0:
    st.warning(
        f"**{counts['suspected_duplicate']} Suspected Duplicate Invoice(s)** detected and excluded from spending totals. "
        "Review them in the **Invoice Manager** to confirm or verify."
    )

st.markdown("---")

# 4. Total Recorded Spending by Original Currency
st.subheader("Original Currency Breakdown")
st.caption("Original invoice amounts and currencies are preserved unblended in SQLite.")

if totals_by_curr:
    curr_cols = st.columns(len(totals_by_curr))
    for i, curr_info in enumerate(totals_by_curr):
        with curr_cols[i]:
            curr_code = curr_info["currency"]
            spent = curr_info["total_spent"]
            cnt = curr_info["invoice_count"]
            # Show original and converted amount
            conv_part = next((item for item in agg_spending["original_currencies"] if item["currency"] == curr_code), None)
            conv_str = currency_service.format_currency(conv_part["converted_total"], display_currency) if conv_part else ""
            st.metric(
                label=f"{curr_code} ({cnt} invoice{'s' if cnt > 1 else ''})",
                value=format_currency_amount(spent, curr_code),
                delta=f"≈ {conv_str}" if curr_code != display_currency else "1:1 Base",
            )
else:
    st.info("No expense data recorded yet.")

st.markdown("---")

# 5. Converted Visualizations: Monthly Trend & Currency Distribution
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader(f"Monthly Spending in {display_currency}")
    monthly_data = agg_spending["monthly_spending"]
    if monthly_data:
        df_monthly = pd.DataFrame(monthly_data)
        fig_monthly = px.bar(
            df_monthly,
            x="month",
            y="converted_spent",
            text_auto=".2s",
            title=f"Monthly Expenses Converted to {display_currency} ({mode.capitalize()} Mode)",
            labels={"month": "Month (YYYY-MM)", "converted_spent": f"Total Spent ({display_currency})"},
            color_discrete_sequence=["#4B37B2"],
        )
        fig_monthly.update_layout(
            paper_bgcolor="#08070B",
            plot_bgcolor="#08070B",
            font_color="#F1F1F1",
            height=380,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("No dated invoice data available for monthly trends.")

with chart_col2:
    st.subheader("Currency Distribution")
    orig_curr_data = agg_spending["original_currencies"]
    if orig_curr_data:
        df_curr_dist = pd.DataFrame(orig_curr_data)
        fig_curr = px.pie(
            df_curr_dist,
            names="currency",
            values="converted_total",
            hole=0.45,
            title=f"Share of Total Spend by Original Currency (Valued in {display_currency})",
            color_discrete_sequence=["#4B37B2", "#8879A7", "#BAA7D1", "#4B334D"],
        )
        fig_curr.update_layout(
            paper_bgcolor="#08070B",
            font_color="#F1F1F1",
            height=380,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_curr, use_container_width=True)
    else:
        st.info("No currency breakdown available.")

st.markdown("---")

# 6. Converted Vendor Spending & Status Distribution
v_col1, v_col2 = st.columns(2)

with v_col1:
    st.subheader(f"Spending by Vendor ({display_currency})")
    vendor_data = agg_spending["vendor_spending"]
    if vendor_data:
        df_vendor = pd.DataFrame(vendor_data)
        fig_vendor = px.bar(
            df_vendor,
            x="converted_spent",
            y="vendor",
            orientation="h",
            title=f"Vendors by Total Spend (Valued in {display_currency})",
            labels={"converted_spent": f"Total Spent ({display_currency})", "vendor": "Vendor"},
            color_discrete_sequence=["#8879A7"],
        )
        fig_vendor.update_layout(
            paper_bgcolor="#08070B",
            plot_bgcolor="#08070B",
            font_color="#F1F1F1",
            height=380,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_vendor, use_container_width=True)
    else:
        st.info("No vendor expense data available.")

with v_col2:
    st.subheader("Document Status Distribution")
    if counts["total"] > 0:
        status_labels = ["Processed Cleanly", "Needs Review", "Verified", "Suspected Duplicate"]
        status_vals = [
            counts["processed"],
            counts["needs_review"],
            counts["verified"],
            counts.get("suspected_duplicate", 0),
        ]
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=status_labels,
                    values=status_vals,
                    hole=0.45,
                    marker=dict(colors=["#10B981", "#F59E0B", "#8879A7", "#923F53"]),
                )
            ]
        )
        fig_pie.update_layout(
            paper_bgcolor="#08070B",
            font_color="#F1F1F1",
            height=380,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No documents to display status distribution.")

st.markdown("---")

# 7. Highest-Value Invoices (Original & Converted)
st.subheader("Highest-Value Invoices")
top_invoices = db.get_highest_value_invoices(limit=5)
if top_invoices:
    # Convert top invoices to display currency
    converted_top = [currency_service.convert_invoice(inv, target_currency=display_currency, mode=mode) for inv in top_invoices]
    df_top = pd.DataFrame(converted_top)
    df_top["Original Total"] = df_top.apply(
        lambda r: format_currency_amount(r["total_amount"], r["currency"]), axis=1
    )
    df_top[f"Valuation ({display_currency})"] = df_top.apply(
        lambda r: currency_service.format_currency(r["converted_amount"], display_currency), axis=1
    )
    st.dataframe(
        df_top[["invoice_number", "vendor_name", "invoice_date", "Original Total", f"Valuation ({display_currency})", "status"]],
        column_config={
            "invoice_number": "Invoice #",
            "vendor_name": "Vendor",
            "invoice_date": "Date",
            "Original Total": "Original Total",
            f"Valuation ({display_currency})": f"Valuation ({display_currency})",
            "status": "Status",
        },
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No invoices found.")

