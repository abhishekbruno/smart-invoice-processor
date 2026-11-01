import re
from datetime import datetime
from typing import Optional, Tuple
import zoneinfo
from config.settings import settings


# Common currency symbol to ISO code mapping
CURRENCY_MAP = {
    "$": "USD",
    "USD": "USD",
    "US$": "USD",
    "€": "EUR",
    "EUR": "EUR",
    "£": "GBP",
    "GBP": "GBP",
    "₹": "INR",
    "INR": "INR",
    "RS": "INR",
    "RS.": "INR",
    "CAD": "CAD",
    "AUD": "AUD",
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "CAD": "CA$",
    "AUD": "AU$",
}


def get_current_time_str() -> str:
    """Returns the current timestamp in ISO format respecting the configured timezone."""
    try:
        tz = zoneinfo.ZoneInfo(settings.TIMEZONE)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def normalize_currency(currency_raw: Optional[str]) -> str:
    """Normalizes raw currency string or symbol to standard 3-letter code (default USD)."""
    if not currency_raw:
        return "USD"
    cleaned = currency_raw.strip().upper()
    return CURRENCY_MAP.get(cleaned, CURRENCY_MAP.get(currency_raw.strip(), "USD"))


def format_currency_amount(amount: Optional[float], currency: str = "USD") -> str:
    """Formats a monetary amount with currency symbol or code."""
    if amount is None:
        return "N/A"
    curr = normalize_currency(currency)
    symbol = CURRENCY_SYMBOLS.get(curr, curr + " ")
    return f"{symbol}{amount:,.2f}"


def format_financial_markdown(text: str) -> str:
    """
    Cleans and formats markdown text containing financial data so Streamlit
    does not interpret '$' as KaTeX LaTeX math delimiters while properly
    rendering headings, bold text, lists, and tables.
    """
    if not text:
        return ""

    # 1. Fix broken bold asterisks like '* *' into '**'
    cleaned = re.sub(r"\*\s+\*", "**", text)

    # 2. Split text by code blocks (fenced ```...``` and inline `...`)
    # so we do not escape $ inside code blocks or monospace snippets.
    parts = re.split(r"(```[\s\S]*?```|`[^`\n]*`)", cleaned)

    escaped_parts = []
    for part in parts:
        if part.startswith("`"):
            # Inside code block or inline code: preserve as-is
            escaped_parts.append(part)
        else:
            # Outside code: escape unescaped dollar signs ($ -> \$)
            # Matches $ not preceded by a backslash
            escaped_part = re.sub(r"(?<!\\)\$", r"\\$", part)
            escaped_parts.append(escaped_part)

    return "".join(escaped_parts)


def parse_date_string(date_str: Optional[str]) -> Optional[str]:
    """
    Attempts to parse a variety of human and machine date formats
    into ISO standard format YYYY-MM-DD.
    Returns None if parsing fails.
    """
    if not date_str:
        return None

    cleaned = date_str.strip()
    # Remove ordinal suffixes like 1st, 2nd, 3rd, 4th
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", cleaned)

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            # Guard against implausible years
            if 1990 <= dt.year <= 2100:
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def extract_quarter(date_iso: Optional[str]) -> Optional[str]:
    """Returns YYYY-Q# for a given ISO date string YYYY-MM-DD."""
    if not date_iso:
        return None
    try:
        dt = datetime.strptime(date_iso, "%Y-%m-%d")
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{q}"
    except Exception:
        return None


def get_now_in_configured_timezone() -> datetime:
    """Returns current datetime in the configured application timezone."""
    try:
        tz = zoneinfo.ZoneInfo(settings.TIMEZONE)
        return datetime.now(tz)
    except Exception:
        return datetime.now()


def get_relative_date_range(query_text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parses natural language relative date periods respecting the configured timezone.
    Returns (start_date_iso, end_date_iso, period_description).
    """
    now = get_now_in_configured_timezone()
    q = query_text.lower()

    # 1. Last Month
    if "last month" in q:
        first_of_this_month = now.replace(day=1)
        # End of last month is one day before first of this month
        import datetime as dt_mod
        last_day_prev = first_of_this_month - dt_mod.timedelta(days=1)
        first_day_prev = last_day_prev.replace(day=1)
        return (
            first_day_prev.strftime("%Y-%m-%d"),
            last_day_prev.strftime("%Y-%m-%d"),
            f"Last Month ({first_day_prev.strftime('%B %Y')})",
        )

    # 2. This Month / Current Month
    if "this month" in q or "current month" in q:
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        return (start_date, now.strftime("%Y-%m-%d"), f"This Month ({now.strftime('%B %Y')})")

    # 3. Last Quarter
    if "last quarter" in q:
        curr_quarter = (now.month - 1) // 3 + 1
        if curr_quarter == 1:
            prev_q = 4
            year = now.year - 1
        else:
            prev_q = curr_quarter - 1
            year = now.year

        start_month = (prev_q - 1) * 3 + 1
        end_month = start_month + 2
        # End of quarter day
        end_day = 31 if end_month in (3, 12) else 30
        return (
            f"{year}-{start_month:02d}-01",
            f"{year}-{end_month:02d}-{end_day:02d}",
            f"Last Quarter ({year}-Q{prev_q})",
        )

    # 4. Explicit Quarter (e.g. Q1, Q2, Q3, Q4)
    q_match = re.search(r"\b(20\d\d)?[\s\-_]?(q[1-4])\b|\b(q[1-4])[\s\-_]?(20\d\d)?\b", q)
    if q_match:
        raw_q = (q_match.group(2) or q_match.group(3) or "").upper()
        raw_yr = q_match.group(1) or q_match.group(4) or str(now.year)
        q_num = int(raw_q.replace("Q", ""))
        start_month = (q_num - 1) * 3 + 1
        end_month = start_month + 2
        end_day = 31 if end_month in (3, 12) else 30
        return (
            f"{raw_yr}-{start_month:02d}-01",
            f"{raw_yr}-{end_month:02d}-{end_day:02d}",
            f"{raw_yr}-{raw_q}",
        )

    # 5. Full Year (e.g. 2024, 2025)
    yr_match = re.search(r"\b(20\d\d)\b", q)
    if yr_match:
        yr = yr_match.group(1)
        return (f"{yr}-01-01", f"{yr}-12-31", f"Year {yr}")

    return None, None, None


def clean_extracted_text(text: str) -> str:
    """Removes excessive whitespace, null bytes, and non-printable control characters."""
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize multiple line breaks
    text = re.sub(r"\r\n|\r", "\n", text)
    # Collapse multiple consecutive empty lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple horizontal spaces to single space
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

