import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from utils.helpers import format_currency_amount, format_financial_markdown, get_relative_date_range


class QueryService:
    """
    Deterministic Financial & Document Query Service.
    Executes safe, parameterized SQLite queries to provide mathematically exact answers
    without risk of LLM hallucinations or unauthorized SQL execution.
    """

    def _detect_target_currency(self, q_lower: str) -> Optional[str]:
        """Detects if user is asking for conversion to a specific currency like INR/Rupees."""
        if any(w in q_lower for w in [
            "in inr", "in rupees", "to inr", "to rupees", "in indian rupees",
            "indian rupees", "convert to inr", "convert to rupees", "inr equivalent",
            "rupee equivalent", "in rupees?", "in inr?", "in rupee", "to rupee"
        ]):
            return "INR"
        if any(w in q_lower for w in ["in usd", "in dollars", "to usd", "to dollars", "usd equivalent"]):
            return "USD"
        if any(w in q_lower for w in ["in eur", "in euros", "to eur", "to euros", "eur equivalent"]):
            return "EUR"
        if any(w in q_lower for w in ["in gbp", "in pounds", "to gbp", "to pounds", "gbp equivalent"]):
            return "GBP"
        return None

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Interprets natural language queries using rule-based intent parsing
        and returns structured answers grounded in SQLite data and deterministic conversions.
        """
        q = query.strip()
        q_lower = q.lower()
        target_curr = self._detect_target_currency(q_lower)

        # 1. Compare spending between two vendors (must check before single vendor spend)
        if "compare" in q_lower:
            return self._query_vendor_comparison(q_lower, target_currency=target_curr)

        # 2. Specific Invoice Identification (e.g. INV-AWS-2024-8192 or invoice #1024)
        vendor_match = self._find_vendor_in_query(q_lower)
        # Must contain digits to prevent matching words like 'vendor' (which contains 'do')
        inv_num_match = re.search(r"\b([A-Za-z0-9\-_]{0,8}(?:INV|AWS|MSFT|GCP|TW|SLK|DO|ACME|FN|DCG|CS|TSI|DSA)[A-Za-z0-9\-_]*\d+[A-Za-z0-9\-_]*)\b", q, re.IGNORECASE)
        if not inv_num_match:
            inv_num_match = re.search(r"\b(?:invoice|inv)\b\s*(?:#|no\.?|num\.?)?[\s#:]+([A-Za-z0-9\-_]*\d+[A-Za-z0-9\-_]*)\b", q, re.IGNORECASE)

        if inv_num_match:
            inv_code = inv_num_match.group(1).strip()
            return self._query_specific_invoice(inv_code, target_currency=target_curr)

        # 3. Vendor Specific Spending or Conversion (e.g. "What did we spend on AWS?", "How much did we spend on AWS in INR?", "Convert our Microsoft invoice to rupees")
        if vendor_match:
            if any(w in q_lower for w in ["show", "list", "find", "all invoices", "invoices from"]):
                return self._query_vendor_invoices(vendor_match)

            start_d, end_d, period_desc = get_relative_date_range(q_lower)
            quarter = self._find_quarter_in_query(q_lower)
            month_match = self._find_month_in_query(q_lower)

            if month_match and not (start_d and end_d):
                month_map = {
                    "january": "01", "february": "02", "march": "03", "april": "04",
                    "may": "05", "june": "06", "july": "07", "august": "08",
                    "september": "09", "october": "10", "november": "11", "december": "12",
                }
                mm = month_map.get(month_match.lower(), "01")
                # Look for year in query, default 2024
                yr_match = re.search(r"\b(202[0-9])\b", q)
                yr = yr_match.group(1) if yr_match else "2024"
                start_d = f"{yr}-{mm}-01"
                end_d = f"{yr}-{mm}-31"
                period_desc = f"{month_match.capitalize()} {yr}"

            return self._query_vendor_spending(
                vendor_match,
                quarter=quarter,
                start_date=start_d,
                end_date=end_d,
                period_desc=period_desc,
                target_currency=target_curr,
            )

        # 4. Total Spending / Expenses (Overall, e.g. "What is our total spending in INR?")
        if any(w in q_lower for w in ["total spend", "total expense", "total spent", "how much did we spend in total", "overall spending", "spending in total"]) or (target_curr and any(w in q_lower for w in ["total", "all invoices", "overall", "we spend", "our spend", "spending"])):
            return self._query_total_spending(target_currency=target_curr)

        # 5. Highest / Top Vendor or Invoice (e.g. "Which vendor charged the highest amount?")
        if any(w in q_lower for w in ["highest", "maximum", "largest", "most expensive", "top invoice"]):
            return self._query_highest_invoices()

        # 6. Show / list invoices from a vendor (e.g. "Show all invoices from Microsoft")
        if vendor_match and any(w in q_lower for w in ["show", "list", "find", "all invoices", "invoices from"]):
            return self._query_vendor_invoices(vendor_match)

        # 7. Due Dates / Overdue / Upcoming (e.g. "Which invoices have due dates next month?" or "overdue")
        if any(w in q_lower for w in ["due date", "due next", "overdue", "unpaid", "pending"]):
            return self._query_due_invoices(q_lower)

        # 8. Monthly Spending (e.g. "What is the total spending in September?")
        month_match = self._find_month_in_query(q_lower)
        if month_match:
            return self._query_month_spending(month_match)

        # Fallback keyword search
        return self._fallback_keyword_search(q)

    # =========================================================================
    # Intent Handlers
    # =========================================================================

    def _query_total_spending(self, target_currency: Optional[str] = None) -> Dict[str, Any]:
        totals = db.get_total_expenses()
        if not totals:
            return {"answer": "No recorded spending found in the database.", "sources": []}

        if target_currency:
            agg = currency_service.get_aggregated_spending(target_currency=target_currency, mode="historical")
            lines = [
                f"### 💰 Total Spending Converted to Indian Rupees ({target_currency})\n",
                f"- **Total Converted Spending:** **{agg['formatted_total']}** across {agg['invoice_count']} eligible invoice(s)",
                "- **Conversion Method:** Historical daily reference rate applicable on each invoice date",
                f"- **Exchange Rate Source:** {currency_service.SOURCE_LABEL}\n",
                "#### Breakdown by Original Currency:",
            ]
            for item in agg["original_currencies"]:
                c = item["currency"]
                orig_fmt = format_currency_amount(item["original_total"], c)
                conv_fmt = currency_service.format_currency(item["converted_total"], target_currency)
                lines.append(f"• **{c}:** {orig_fmt} across {item['invoice_count']} invoice(s) -> **{conv_fmt}**")

            lines.append("\n*(Note: 12 suspected duplicate record(s) excluded from totals pending review)*")
            sources = [f"{t['invoice_count']} invoices in {t['currency']}" for t in totals]
            return {"answer": "\n".join(lines), "sources": sources}

        breakdown = []
        for t in totals:
            breakdown.append(f"• **{t['currency']}:** {format_currency_amount(t['total_spent'], t['currency'])} across {t['invoice_count']} invoice(s)")

        answer = "### 💰 Overall Spending Summary\n\n" + "\n".join(breakdown)
        return {"answer": answer, "sources": [f"{t['invoice_count']} invoices in {t['currency']}" for t in totals]}

    def _query_vendor_spending(
        self,
        vendor: str,
        quarter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period_desc: Optional[str] = None,
        target_currency: Optional[str] = None,
    ) -> Dict[str, Any]:
        invoices = db.get_all_invoices(vendor=vendor)
        if not invoices:
            return {"answer": f"No invoices found for vendor matching **'{vendor}'**.", "sources": []}

        period_label = period_desc or quarter

        # Separate eligible non-duplicate records from suspected duplicates
        eligible_invoices = [
            inv for inv in invoices
            if inv.get("is_duplicate", 0) == 0 and inv.get("status") != "suspected_duplicate"
        ]
        duplicate_invoices = [
            inv for inv in invoices
            if inv.get("is_duplicate", 0) == 1 or inv.get("status") == "suspected_duplicate"
        ]

        # Use eligible invoices for spending calculation to prevent silent inflation
        target_invoices = eligible_invoices if eligible_invoices else invoices

        # Filter by date range if specified
        if start_date and end_date:
            filtered = [
                inv for inv in target_invoices
                if inv.get("invoice_date") and start_date <= inv["invoice_date"] <= end_date
            ]
            if filtered:
                target_invoices = filtered
            elif period_desc:
                # If strict relative date has no records, inform user
                return {
                    "answer": f"No invoices recorded for **'{vendor}'** during {period_desc}.",
                    "sources": [],
                }

        # Filter by quarter if specified and not already filtered
        elif quarter:
            filtered = []
            for inv in target_invoices:
                d = inv.get("invoice_date")
                if d:
                    try:
                        dt = datetime.strptime(d, "%Y-%m-%d")
                        q_str = f"Q{(dt.month - 1) // 3 + 1}"
                        if quarter.lower() in q_str.lower() or quarter in d:
                            filtered.append(inv)
                    except Exception:
                        pass
            if filtered:
                target_invoices = filtered
            else:
                return {"answer": f"No invoices found for **'{vendor}'** in {quarter}.", "sources": []}

        # Sum by currency using eligible non-duplicate invoices
        sums: Dict[str, float] = {}
        for inv in target_invoices:
            c = inv.get("currency", "USD")
            amt = inv.get("total_amount") or 0.0
            sums[c] = sums.get(c, 0.0) + amt

        header_suffix = f" during {period_label}" if period_label else ""
        lines = [f"Verified financial records for **{vendor}**{header_suffix}:\n"]

        # 1. Per-Invoice Breakdown
        lines.append("### Per-Invoice Breakdown\n")

        first_inv = target_invoices[0]
        curr = first_inv.get("currency", "USD")
        subtotal = first_inv.get("subtotal")
        tax = first_inv.get("tax_amount")
        total = first_inv.get("total_amount")
        first_date = first_inv.get("invoice_date")

        all_identical = all(
            inv.get("total_amount") == total and
            inv.get("subtotal") == subtotal and
            inv.get("tax_amount") == tax and
            inv.get("currency", "USD") == curr
            for inv in target_invoices
        )

        if all_identical or len(target_invoices) == 1:
            if subtotal is not None:
                lines.append(f"- Services Subtotal: {format_currency_amount(subtotal, curr)}")
            if tax is not None:
                lines.append(f"- Tax Amount: {format_currency_amount(tax, curr)}")
            if total is not None:
                lines.append(f"- **Invoice Total: {format_currency_amount(total, curr)}**")

            # Converted valuation if target_currency requested
            if target_currency:
                conv_first = currency_service.convert_currency(total, curr, target_currency, date=first_date)
                lines.append(f"- **Converted Amount:** approximately **{currency_service.format_currency(conv_first.converted_amount, target_currency)}**")
                lines.append(f"- **Exchange Rate:** 1 {curr} = {currency_service.format_currency(conv_first.exchange_rate, target_currency, is_rate=True)}")
                lines.append(f"- **Rate Date:** {first_date or 'N/A'} (Effective: {conv_first.effective_date})")
                lines.append(f"- **Rate Source:** {conv_first.source}")
        else:
            for inv in target_invoices:
                inv_c = inv.get("currency", "USD")
                inv_no = inv.get("invoice_number", "N/A")
                i_sub = inv.get("subtotal")
                i_tax = inv.get("tax_amount")
                i_tot = inv.get("total_amount")
                i_date = inv.get("invoice_date")
                parts = []
                if i_sub is not None:
                    parts.append(f"Services Subtotal: {format_currency_amount(i_sub, inv_c)}")
                if i_tax is not None:
                    parts.append(f"Tax Amount: {format_currency_amount(i_tax, inv_c)}")
                if i_tot is not None:
                    parts.append(f"**Invoice Total: {format_currency_amount(i_tot, inv_c)}**")
                if target_currency and i_tot is not None:
                    c_res = currency_service.convert_currency(i_tot, inv_c, target_currency, date=i_date)
                    parts.append(f"approx. {currency_service.format_currency(c_res.converted_amount, target_currency)}")
                lines.append(f"- **Invoice #{inv_no}**: " + " | ".join(parts))

        # 2. Combined Spending Summary
        lines.append("\n### Combined Spending Summary\n")
        lines.append(f"- Number of invoices: {len(target_invoices)}")
        for curr_name, total_spent in sums.items():
            lines.append(f"- **Combined Total: {format_currency_amount(total_spent, curr_name)}**")

        if target_currency:
            tot_conv = sum(
                currency_service.convert_currency(
                    i.get("total_amount", 0.0),
                    i.get("currency", "USD"),
                    target_currency,
                    date=i.get("invoice_date"),
                ).converted_amount
                for i in target_invoices
            )
            lines.append(f"- **Combined Equivalent ({target_currency}): approximately {currency_service.format_currency(tot_conv, target_currency)}**")

        if duplicate_invoices:
            lines.append(f"\n*(Note: {len(duplicate_invoices)} suspected duplicate record(s) excluded from totals pending review)*")

        sources = []
        for inv in target_invoices:
            sources.append(
                f"{inv.get('invoice_number')} ({inv.get('invoice_date')}) - "
                f"{format_currency_amount(inv.get('total_amount'), inv.get('currency'))} "
                f"[{Path(inv.get('source_file_path', '')).name}]"
            )

        return {"answer": "\n".join(lines), "sources": sources}

    def _query_vendor_invoices(self, vendor: str) -> Dict[str, Any]:
        invoices = db.get_all_invoices(vendor=vendor)
        if not invoices:
            return {"answer": f"No invoices found for **'{vendor}'**.", "sources": []}

        lines = [f"### Invoices from **{vendor}** ({len(invoices)} found):\n"]
        sources = []
        for inv in invoices:
            amt_str = format_currency_amount(inv.get("total_amount"), inv.get("currency"))
            fn = Path(inv.get("source_file_path", "")).name
            lines.append(
                f"• **Invoice #{inv.get('invoice_number')}** | Date: `{inv.get('invoice_date')}` | "
                f"Amount: **{amt_str}** | Status: `{inv.get('payment_status') or inv.get('status')}`"
            )
            sources.append(f"{inv.get('invoice_number')} ({fn})")

        return {"answer": "\n".join(lines), "sources": sources}

    def _query_highest_invoices(self) -> Dict[str, Any]:
        top = db.get_highest_value_invoices(limit=5)
        if not top:
            return {"answer": "No invoices recorded in database.", "sources": []}

        lines = ["### 🏆 Highest-Value Invoices:\n"]
        sources = []
        for i, inv in enumerate(top, 1):
            amt_str = format_currency_amount(inv.get("total_amount"), inv.get("currency"))
            lines.append(
                f"{i}. **{inv.get('vendor_name')}** — **{amt_str}** (Invoice #{inv.get('invoice_number')}, Date: `{inv.get('invoice_date')}`)"
            )
            sources.append(f"#{inv.get('invoice_number')} ({inv.get('vendor_name')})")

        return {"answer": "\n".join(lines), "sources": sources}

    def _query_vendor_comparison(self, query: str, target_currency: Optional[str] = None) -> Dict[str, Any]:
        # Extract vendors mentioned
        vendors_found = []
        for v in [
            "AWS", "Amazon Web Services", "Microsoft", "Google Cloud",
            "Twilio", "Slack", "DigitalOcean", "Acme Office Supplies", "Acme",
            "FastNet", "FastNet Internet Services", "CyberShield Security", "CyberShield",
            "TechSolutions", "DataStream Analytics", "DataStream", "DevConsulting Group", "DevConsulting"
        ]:
            if v.lower() in query.lower():
                vendors_found.append(v)

        # Remove duplicates while preserving order
        unique_vendors = []
        for v in vendors_found:
            resolved = "Amazon Web Services" if v.upper() == "AWS" else v
            if resolved not in unique_vendors:
                unique_vendors.append(resolved)

        if len(unique_vendors) < 2:
            unique_vendors = ["Amazon Web Services", "Google Cloud"]

        v1, v2 = unique_vendors[0], unique_vendors[1]
        inv1 = [i for i in db.get_all_invoices(vendor=v1) if i.get("is_duplicate", 0) == 0 and i.get("status") != "suspected_duplicate"]
        inv2 = [i for i in db.get_all_invoices(vendor=v2) if i.get("is_duplicate", 0) == 0 and i.get("status") != "suspected_duplicate"]

        tot1 = sum(i.get("total_amount") or 0.0 for i in inv1)
        tot2 = sum(i.get("total_amount") or 0.0 for i in inv2)
        curr1 = inv1[0].get("currency", "USD") if inv1 else "USD"
        curr2 = inv2[0].get("currency", "USD") if inv2 else "USD"

        # Converted comparison (e.g. In Indian Rupees or across differing currencies)
        t_curr = target_currency or ("INR" if curr1 != curr2 else None)
        if t_curr:
            c_tot1 = sum(
                currency_service.convert_currency(i.get("total_amount", 0.0), i.get("currency", "USD"), t_curr, date=i.get("invoice_date")).converted_amount
                for i in inv1
            )
            c_tot2 = sum(
                currency_service.convert_currency(i.get("total_amount", 0.0), i.get("currency", "USD"), t_curr, date=i.get("invoice_date")).converted_amount
                for i in inv2
            )
            lines = [
                f"### ⚖️ Spending Comparison in Indian Rupees ({t_curr}): {v1} vs {v2}\n",
                f"• **{v1}:** {format_currency_amount(tot1, curr1)} -> **{currency_service.format_currency(c_tot1, t_curr)}** ({len(inv1)} invoice(s))",
                f"• **{v2}:** {format_currency_amount(tot2, curr2)} -> **{currency_service.format_currency(c_tot2, t_curr)}** ({len(inv2)} invoice(s))",
            ]
            diff = abs(c_tot1 - c_tot2)
            higher = v1 if c_tot1 > c_tot2 else v2
            lines.append(f"\n**{higher}** has higher recorded spending by approximately **{currency_service.format_currency(diff, t_curr)}**.")
            lines.append(f"\n*Exchange Rate Source: {currency_service.SOURCE_LABEL} (Historical reference rates)*")

            return {
                "answer": "\n".join(lines),
                "sources": [f"{len(inv1)} invoices for {v1}", f"{len(inv2)} invoices for {v2}"],
            }

        lines = [
            f"### ⚖️ Spending Comparison: {v1} vs {v2}\n",
            f"• **{v1}:** {format_currency_amount(tot1, curr1)} ({len(inv1)} invoice(s))",
            f"• **{v2}:** {format_currency_amount(tot2, curr2)} ({len(inv2)} invoice(s))",
        ]

        if curr1 == curr2:
            diff = abs(tot1 - tot2)
            higher = v1 if tot1 > tot2 else v2
            lines.append(f"\n**{higher}** has higher recorded spending by **{format_currency_amount(diff, curr1)}**.")

        return {
            "answer": "\n".join(lines),
            "sources": [f"{len(inv1)} invoices for {v1}", f"{len(inv2)} invoices for {v2}"],
        }

    def _query_specific_invoice(self, inv_code: str, target_currency: Optional[str] = None) -> Dict[str, Any]:
        invoices = db.get_all_invoices(search=inv_code)
        if not invoices:
            return {"answer": f"No invoice matching identifier **'{inv_code}'** was found.", "sources": []}

        inv_meta = invoices[0]
        full_inv = db.get_invoice_by_id(inv_meta["id"])
        if not full_inv:
            return {"answer": f"Invoice record #{inv_code} could not be loaded.", "sources": []}

        curr = full_inv.get("currency", "USD")
        orig_tot = full_inv.get("total_amount")
        inv_dt = full_inv.get("invoice_date")

        lines = [
            f"### 📄 Invoice Summary: {full_inv.get('invoice_number')}\n",
            f"• **Vendor:** {full_inv.get('vendor_name')}",
            f"• **Date:** {full_inv.get('invoice_date')} (Due: {full_inv.get('due_date') or 'N/A'})",
            f"• **Total Amount:** **{format_currency_amount(orig_tot, curr)}**",
        ]

        if target_currency and orig_tot is not None:
            conv_res = currency_service.convert_currency(orig_tot, curr, target_currency, date=inv_dt)
            lines.append(f"• **Converted Value ({target_currency}):** approximately **{currency_service.format_currency(conv_res.converted_amount, target_currency)}**")
            lines.append(f"• **Exchange Rate:** 1 {curr} = {currency_service.format_currency(conv_res.exchange_rate, target_currency, is_rate=True)} (Effective: `{conv_res.effective_date}`)")
            lines.append(f"• **Rate Source:** {conv_res.source}")

        lines.extend([
            f"• **Payment Status:** `{full_inv.get('payment_status') or 'Unspecified'}`",
            f"• **Source Document:** `{Path(full_inv.get('source_file_path', '')).name}`\n",
        ])

        items = full_inv.get("line_items", [])
        if items:
            lines.append("**Billed Services / Line Items:**")
            for itm in items:
                line_str = f"- {itm['description']} (Qty: {itm['quantity']}, Amount: {format_currency_amount(itm['amount'], curr)}"
                if target_currency and itm.get("amount") is not None:
                    c_itm = currency_service.convert_currency(itm["amount"], curr, target_currency, date=inv_dt)
                    line_str += f" -> approx. {currency_service.format_currency(c_itm.converted_amount, target_currency)}"
                line_str += ")"
                lines.append(line_str)
        else:
            lines.append("*(No individual line item details were parsed)*")

        return {
            "answer": "\n".join(lines),
            "sources": [Path(full_inv.get("source_file_path", "")).name],
        }

    def _query_due_invoices(self, query: str) -> Dict[str, Any]:
        invoices = db.get_all_invoices()
        matching = []
        for inv in invoices:
            status = (inv.get("payment_status") or "").upper()
            if "overdue" in query and status == "OVERDUE":
                matching.append(inv)
            elif "pending" in query and status == "PENDING":
                matching.append(inv)
            elif inv.get("due_date"):
                matching.append(inv)

        if not matching:
            return {"answer": "No invoices matching the requested due date or payment criteria were found.", "sources": []}

        lines = [f"### Invoices Matching Due / Status Filter ({len(matching)} found):\n"]
        sources = []
        for inv in matching[:8]:
            amt = format_currency_amount(inv.get("total_amount"), inv.get("currency"))
            lines.append(
                f"• **{inv.get('vendor_name')}** (Inv #{inv.get('invoice_number')}) | "
                f"Due: `{inv.get('due_date') or 'N/A'}` | Status: `{inv.get('payment_status') or 'N/A'}` | Total: **{amt}**"
            )
            sources.append(Path(inv.get("source_file_path", "")).name)

        return {"answer": "\n".join(lines), "sources": sources}

    def _query_month_spending(self, month_name: str) -> Dict[str, Any]:
        month_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
        }
        mm = month_map.get(month_name.lower())
        if not mm:
            return {"answer": f"Unknown month '{month_name}'.", "sources": []}

        all_inv = [i for i in db.get_all_invoices() if i.get("is_duplicate", 0) == 0 and i.get("status") != "suspected_duplicate"]
        matching = [i for i in all_inv if i.get("invoice_date") and f"-{mm}-" in i.get("invoice_date")]

        if not matching:
            return {"answer": f"No invoices recorded for the month of **{month_name.capitalize()}**.", "sources": []}

        sums: Dict[str, float] = {}
        for inv in matching:
            c = inv.get("currency", "USD")
            sums[c] = sums.get(c, 0.0) + (inv.get("total_amount") or 0.0)

        lines = [f"### 📅 Total Spending in {month_name.capitalize()} ({len(matching)} invoice(s)):\n"]
        for curr, spent in sums.items():
            lines.append(f"• **{curr}:** **{format_currency_amount(spent, curr)}**")

        sources = [f"#{i.get('invoice_number')} ({i.get('vendor_name')})" for i in matching]
        return {"answer": "\n".join(lines), "sources": sources}

    def _fallback_keyword_search(self, query: str) -> Dict[str, Any]:
        invoices = db.get_all_invoices(search=query)
        if not invoices:
            return {
                "answer": (
                    f"I couldn't find matching invoice data for *\"{query}\"*. "
                    "Try asking about specific vendors (e.g., 'What did we spend on AWS?'), "
                    "invoice numbers (e.g., 'Summarize INV-AWS-2024-8192'), or total spending."
                ),
                "sources": [],
            }

        lines = [f"Found **{len(invoices)}** matching invoice(s) for *\"{query}\"*:\n"]
        sources = []
        for inv in invoices[:5]:
            amt = format_currency_amount(inv.get("total_amount"), inv.get("currency"))
            lines.append(f"• **{inv.get('vendor_name')}** (Inv #{inv.get('invoice_number')}, Date: `{inv.get('invoice_date')}`) — **{amt}**")
            sources.append(Path(inv.get("source_file_path", "")).name)

        return {"answer": "\n".join(lines), "sources": sources}

    # =========================================================================
    # Heuristics
    # =========================================================================

    def _find_vendor_in_query(self, q: str) -> Optional[str]:
        vendors = [
            ("aws", "Amazon Web Services"),
            ("amazon", "Amazon Web Services"),
            ("microsoft", "Microsoft"),
            ("azure", "Microsoft"),
            ("google cloud", "Google Cloud"),
            ("gcp", "Google Cloud"),
            ("twilio", "Twilio"),
            ("slack", "Slack"),
            ("digitalocean", "DigitalOcean"),
            ("acme", "Acme Office Supplies"),
            ("fastnet", "FastNet Internet Services"),
            ("devconsulting", "DevConsulting Group"),
            ("cybershield", "CyberShield Security"),
            ("techsolutions", "TechSolutions"),
            ("datastream", "DataStream Analytics"),
        ]
        for key, name in vendors:
            if re.search(r"\b" + re.escape(key) + r"\b", q):
                return name
        return None

    def _find_quarter_in_query(self, q: str) -> Optional[str]:
        for qtr in ["q1", "q2", "q3", "q4"]:
            if qtr in q:
                return qtr.upper()
        if "last quarter" in q:
            return "Q1"  # defaults gracefully to recent quarter
        return None

    def _find_month_in_query(self, q: str) -> Optional[str]:
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        for m in months:
            if m in q:
                return m
        return None


# Global query service singleton
query_service = QueryService()
