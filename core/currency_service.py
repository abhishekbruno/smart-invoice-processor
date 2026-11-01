import json
import logging
import re
import threading
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple, Union
from core.database import db
from utils.helpers import get_current_time_str, normalize_currency

logger = logging.getLogger(__name__)

# Supported currency ISO codes
SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "INR"}

# Baseline fallback rates (used only when offline/network failure and rate is not in SQLite cache)
# Grounded in official European Central Bank reference data
BASELINE_OFFLINE_RATES: Dict[Tuple[str, str], Tuple[Decimal, str]] = {
    # (from, to) -> (rate, effective_date)
    ("USD", "INR"): (Decimal("83.50"), "2024-05-10"),
    ("EUR", "INR"): (Decimal("90.50"), "2024-05-10"),
    ("GBP", "INR"): (Decimal("106.00"), "2024-05-10"),
    ("INR", "INR"): (Decimal("1.00"), "2024-05-10"),
    ("INR", "USD"): (Decimal("0.011976"), "2024-05-10"),
    ("INR", "EUR"): (Decimal("0.011050"), "2024-05-10"),
    ("INR", "GBP"): (Decimal("0.009434"), "2024-05-10"),
    ("USD", "EUR"): (Decimal("0.9225"), "2024-05-10"),
    ("EUR", "USD"): (Decimal("1.0840"), "2024-05-10"),
    ("GBP", "USD"): (Decimal("1.2690"), "2024-05-10"),
    ("USD", "GBP"): (Decimal("0.7880"), "2024-05-10"),
    ("EUR", "GBP"): (Decimal("0.8530"), "2024-05-10"),
    ("GBP", "EUR"): (Decimal("1.1720"), "2024-05-10"),
}


@dataclass
class ExchangeRateResult:
    """Represents a verified exchange rate lookup result."""
    rate: Decimal
    from_currency: str
    to_currency: str
    requested_date: str          # 'latest' or 'YYYY-MM-DD'
    effective_date: str          # Actual ECB business day of rate
    source: str                  # API name, cache, or fallback indicator
    is_cached: bool = False
    is_fallback: bool = False
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["rate"] = float(self.rate)
        return d

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


@dataclass
class ConversionResult:
    """Represents a deterministic currency conversion result."""
    original_amount: Decimal
    from_currency: str
    converted_amount: Decimal
    to_currency: str
    exchange_rate: Decimal
    effective_date: str
    source: str
    mode: str = "historical"     # "historical" or "latest"
    is_cached: bool = False
    is_fallback: bool = False
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["original_amount"] = float(self.original_amount)
        d["converted_amount"] = float(self.converted_amount)
        d["exchange_rate"] = float(self.exchange_rate)
        return d

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class CurrencyService:
    """
    Deterministic Currency Conversion & Analytics Service.
    Powered by the free Frankfurter API v2 (European Central Bank reference data).
    Uses Python Decimal for exact financial calculations.
    Never hallucinates rates; caches historical and daily rates in SQLite.
    """

    PRIMARY_API_BASE = "https://api.frankfurter.dev/v1"
    BACKUP_API_BASE = "https://api.frankfurter.app/v1"
    SOURCE_LABEL = "European Central Bank via Frankfurter API"

    _lock = threading.Lock()

    def __init__(self):
        # In-memory session cache: (from, to, date_key) -> ExchangeRateResult
        self._memory_cache: Dict[Tuple[str, str, str], ExchangeRateResult] = {}

    # =========================================================================
    # Core API & Rate Retrieval
    # =========================================================================

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[str] = None,
    ) -> ExchangeRateResult:
        """
        Retrieves reference exchange rate between two currencies for a given date or latest.
        Handles:
          - 1:1 same currency conversions (zero network requests)
          - SQLite persistent caching
          - In-memory caching
          - Weekend / bank holiday date adjustments by ECB
          - Offline fallbacks with audit warnings
        """
        from_curr = normalize_currency(from_currency).upper()
        to_curr = normalize_currency(to_currency).upper()

        # Date normalization
        date_key = (date.strip() if date and date.strip() else "latest")

        # 1. Identity conversion (e.g. INR -> INR, USD -> USD)
        if from_curr == to_curr:
            eff_date = date_key if date_key != "latest" else get_current_time_str().split()[0]
            return ExchangeRateResult(
                rate=Decimal("1.0"),
                from_currency=from_curr,
                to_currency=to_curr,
                requested_date=date_key,
                effective_date=eff_date,
                source="Same Currency (1:1 Base)",
                is_cached=True,
                is_fallback=False,
            )

        cache_key = (from_curr, to_curr, date_key)

        # 2. Check in-memory cache
        with self._lock:
            if cache_key in self._memory_cache:
                return self._memory_cache[cache_key]

        # 3. Check SQLite persistent cache
        cached_row = db.get_cached_rate(from_curr, to_curr, date_key)
        if cached_row:
            res = ExchangeRateResult(
                rate=Decimal(str(cached_row["rate_decimal"])),
                from_currency=from_curr,
                to_currency=to_curr,
                requested_date=date_key,
                effective_date=cached_row["effective_date"],
                source=cached_row["source"],
                is_cached=True,
                is_fallback="Fallback" in cached_row["source"],
            )
            with self._lock:
                self._memory_cache[cache_key] = res
            return res

        # 4. Fetch live from Frankfurter API
        res = self._fetch_live_rate(from_curr, to_curr, date_key)

        # 5. Cache result if successful
        if res and not res.is_fallback:
            try:
                db.save_cached_rate(
                    from_currency=from_curr,
                    to_currency=to_curr,
                    rate_date=date_key,
                    effective_date=res.effective_date,
                    rate=float(res.rate),
                    rate_decimal=str(res.rate),
                    source=res.source,
                )
            except Exception as e:
                logger.debug(f"Failed to write rate to SQLite cache: {e}")

        with self._lock:
            self._memory_cache[cache_key] = res

        return res

    def get_historical_rate(
        self,
        date: str,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRateResult:
        """Alias for get_exchange_rate with explicit date parameter."""
        return self.get_exchange_rate(from_currency, to_currency, date=date)

    def get_latest_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """
        Fetches the latest reference exchange rates for all supported currencies
        relative to the given base currency.
        """
        base = normalize_currency(base_currency).upper()
        symbols = [c for c in ["USD", "EUR", "GBP", "INR"] if c != base]
        rates: Dict[str, Decimal] = {base: Decimal("1.0")}
        effective_date = get_current_time_str().split()[0]
        source = self.SOURCE_LABEL

        for sym in symbols:
            rate_res = self.get_exchange_rate(base, sym, date=None)
            rates[sym] = rate_res.rate
            effective_date = rate_res.effective_date
            source = rate_res.source

        return {
            "base": base,
            "effective_date": effective_date,
            "rates": rates,
            "source": source,
        }

    # =========================================================================
    # Financial Currency Conversion
    # =========================================================================

    def convert_currency(
        self,
        amount: Union[float, Decimal, int, str, None],
        from_currency: str,
        to_currency: str,
        date: Optional[str] = None,
        mode: str = "historical",
    ) -> ConversionResult:
        """
        Converts a monetary amount between currencies using Python Decimal.
        Applies mathematical rounding (ROUND_HALF_UP to 2 decimal places).
        """
        if amount is None:
            amt_dec = Decimal("0.00")
        else:
            try:
                amt_dec = Decimal(str(amount))
            except (InvalidOperation, ValueError):
                amt_dec = Decimal("0.00")

        # Determine rate date based on conversion mode
        rate_date = date if (mode == "historical" and date) else None

        rate_res = self.get_exchange_rate(from_currency, to_currency, date=rate_date)

        # Exact Decimal arithmetic
        converted_dec = (amt_dec * rate_res.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return ConversionResult(
            original_amount=amt_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            from_currency=rate_res.from_currency,
            converted_amount=converted_dec,
            to_currency=rate_res.to_currency,
            exchange_rate=rate_res.rate,
            effective_date=rate_res.effective_date,
            source=rate_res.source,
            mode=mode,
            is_cached=rate_res.is_cached,
            is_fallback=rate_res.is_fallback,
            warning=rate_res.warning,
        )

    # =========================================================================
    # High-Level Invoice & Dashboard Aggregation
    # =========================================================================

    def convert_invoice(
        self,
        invoice: Dict[str, Any],
        target_currency: str = "INR",
        mode: str = "historical",
    ) -> Dict[str, Any]:
        """
        Enriches an invoice dictionary with converted amounts and exchange rate metadata.
        Does not mutate the original database record.
        """
        inv_copy = dict(invoice)
        from_curr = inv_copy.get("currency", "USD")
        orig_amt = inv_copy.get("total_amount")
        inv_date = inv_copy.get("invoice_date")

        res = self.convert_currency(
            amount=orig_amt,
            from_currency=from_curr,
            to_currency=target_currency,
            date=inv_date,
            mode=mode,
        )

        inv_copy["converted_amount"] = float(res.converted_amount)
        inv_copy["target_currency"] = target_currency
        inv_copy["exchange_rate"] = float(res.exchange_rate)
        inv_copy["exchange_rate_str"] = f"1 {from_curr} = {self.format_currency(res.exchange_rate, target_currency, is_rate=True)}"
        inv_copy["rate_effective_date"] = res.effective_date
        inv_copy["rate_source"] = res.source
        inv_copy["rate_warning"] = res.warning
        inv_copy["conversion_mode"] = mode

        return inv_copy

    def get_aggregated_spending(
        self,
        target_currency: str = "INR",
        mode: str = "historical",
        include_duplicates: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculates total converted spending across all eligible invoices in target currency.
        Returns:
          - Total converted spending in target currency
          - Breakdown by original currency
          - Breakdown by vendor converted to target currency
          - Monthly trend converted to target currency
          - Currency distribution metrics
        """
        target_curr = normalize_currency(target_currency).upper()
        # Retrieve all invoices
        all_invoices = db.get_all_invoices(include_duplicates=True)

        # Filter strictly for eligible non-duplicate records
        eligible = [
            inv for inv in all_invoices
            if (include_duplicates or (inv.get("is_duplicate", 0) == 0 and inv.get("status") != "suspected_duplicate"))
            and inv.get("total_amount") is not None
        ]

        total_converted = Decimal("0.00")
        vendor_totals: Dict[str, Decimal] = {}
        monthly_totals: Dict[str, Decimal] = {}
        original_currency_breakdown: Dict[str, Dict[str, Any]] = {}
        conversion_records: List[ConversionResult] = []

        for inv in eligible:
            curr = inv.get("currency", "USD")
            amt = inv.get("total_amount", 0.0)
            date_str = inv.get("invoice_date")
            vendor = inv.get("vendor_name") or "Unknown"

            # Track original totals
            if curr not in original_currency_breakdown:
                original_currency_breakdown[curr] = {
                    "currency": curr,
                    "original_total": Decimal("0.00"),
                    "converted_total": Decimal("0.00"),
                    "invoice_count": 0,
                }
            original_currency_breakdown[curr]["original_total"] += Decimal(str(amt))
            original_currency_breakdown[curr]["invoice_count"] += 1

            # Convert to target currency
            conv = self.convert_currency(
                amount=amt,
                from_currency=curr,
                to_currency=target_curr,
                date=date_str,
                mode=mode,
            )
            conversion_records.append(conv)
            total_converted += conv.converted_amount
            original_currency_breakdown[curr]["converted_total"] += conv.converted_amount

            # Vendor aggregation
            vendor_totals[vendor] = vendor_totals.get(vendor, Decimal("0.00")) + conv.converted_amount

            # Monthly aggregation
            month_key = date_str[:7] if date_str and len(date_str) >= 7 else "Unknown"
            monthly_totals[month_key] = monthly_totals.get(month_key, Decimal("0.00")) + conv.converted_amount

        # Format structures for charting
        vendor_list = [
            {"vendor": v, "converted_spent": float(amt), "currency": target_curr}
            for v, amt in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)
        ]

        monthly_list = [
            {"month": m, "converted_spent": float(amt), "currency": target_curr}
            for m, amt in sorted(monthly_totals.items())
        ]

        orig_list = [
            {
                "currency": k,
                "original_total": float(v["original_total"]),
                "converted_total": float(v["converted_total"]),
                "invoice_count": v["invoice_count"],
            }
            for k, v in original_currency_breakdown.items()
        ]

        return {
            "target_currency": target_curr,
            "mode": mode,
            "total_converted": total_converted,
            "total_converted_float": float(total_converted),
            "formatted_total": self.format_currency(total_converted, target_curr),
            "invoice_count": len(eligible),
            "vendor_spending": vendor_list,
            "monthly_spending": monthly_list,
            "original_currencies": orig_list,
            "effective_rates_used": len(conversion_records),
        }

    # =========================================================================
    # Currency Formatting (Indian Lakhs/Crores & International Standard)
    # =========================================================================

    def format_currency(
        self,
        amount: Union[float, Decimal, int, str, None],
        currency: str = "INR",
        is_rate: bool = False,
    ) -> str:
        """
        Formats a monetary amount according to the conventions of the specified currency.
        Uses Indian numbering system (Lakhs, Crores) for INR amounts.
        """
        if amount is None:
            return "N/A"

        try:
            amt_dec = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            return "N/A"

        curr = normalize_currency(currency).upper()

        if is_rate:
            # Exchange rate formatting (4 decimal places)
            return f"₹{amt_dec:.4f}" if curr == "INR" else f"{amt_dec:.4f} {curr}"

        # Standard financial rounding to 2 decimal places
        quantized = amt_dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if curr == "INR":
            return self._format_inr_lakhs(quantized)
        elif curr == "USD":
            return f"${quantized:,.2f}"
        elif curr == "EUR":
            return f"€{quantized:,.2f}"
        elif curr == "GBP":
            return f"£{quantized:,.2f}"
        else:
            return f"{curr} {quantized:,.2f}"

    def _format_inr_lakhs(self, dec_val: Decimal) -> str:
        """Formats Decimal into authentic Indian numbering format (e.g. ₹1,75,000.00)."""
        is_negative = dec_val < 0
        abs_val = abs(dec_val)
        s = f"{abs_val:.2f}"
        int_part, dec_part = s.split(".")

        if len(int_part) <= 3:
            formatted_int = int_part
        else:
            last3 = int_part[-3:]
            rest = int_part[:-3]
            groups = []
            while len(rest) > 2:
                groups.append(rest[-2:])
                rest = rest[:-2]
            if rest:
                groups.append(rest)
            groups.reverse()
            formatted_int = ",".join(groups) + "," + last3

        prefix = "-₹" if is_negative else "₹"
        return f"{prefix}{formatted_int}.{dec_part}"

    # =========================================================================
    # Internal HTTP Fetching & Fallbacks
    # =========================================================================

    def _fetch_live_rate(
        self,
        from_curr: str,
        to_curr: str,
        date_key: str,
    ) -> ExchangeRateResult:
        """Attempts to fetch reference rate from Frankfurter API with fallback endpoints."""
        url_path = "latest" if date_key == "latest" else date_key
        endpoints = [
            f"{self.PRIMARY_API_BASE}/{url_path}?base={from_curr}&symbols={to_curr}",
            f"{self.BACKUP_API_BASE}/{url_path}?base={from_curr}&symbols={to_curr}",
        ]

        last_error = None
        for endpoint in endpoints:
            try:
                req = urllib.request.Request(
                    endpoint,
                    headers={"User-Agent": "SmartInvoiceProcessor/2.0 (MultiCurrencyModule)"},
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        rates = data.get("rates", {})
                        if to_curr in rates:
                            rate_val = Decimal(str(rates[to_curr]))
                            eff_date = data.get("date", date_key)
                            return ExchangeRateResult(
                                rate=rate_val,
                                from_currency=from_curr,
                                to_currency=to_curr,
                                requested_date=date_key,
                                effective_date=eff_date,
                                source=f"{self.SOURCE_LABEL} ({eff_date})",
                                is_cached=False,
                                is_fallback=False,
                            )
            except Exception as e:
                last_error = str(e)
                logger.debug(f"Frankfurter request to {endpoint} failed: {e}")

        # Check if any cached rate exists for this pair across different dates
        cached_row = db.get_cached_rate(from_curr, to_curr, "latest")
        if cached_row:
            logger.warning(f"Using latest cached rate for {from_curr}->{to_curr} due to network failure: {last_error}")
            return ExchangeRateResult(
                rate=Decimal(str(cached_row["rate_decimal"])),
                from_currency=from_curr,
                to_currency=to_curr,
                requested_date=date_key,
                effective_date=cached_row["effective_date"],
                source=f"Cached Stale Rate ({cached_row['effective_date']})",
                is_cached=True,
                is_fallback=True,
                warning=f"Live rate unavailable ({last_error}). Using previously cached reference rate.",
            )

        # Baseline fallback rate
        pair = (from_curr, to_curr)
        if pair in BASELINE_OFFLINE_RATES:
            rate_val, eff_date = BASELINE_OFFLINE_RATES[pair]
            logger.warning(f"Using baseline offline fallback for {from_curr}->{to_curr}")
            return ExchangeRateResult(
                rate=rate_val,
                from_currency=from_curr,
                to_currency=to_curr,
                requested_date=date_key,
                effective_date=eff_date,
                source=f"Offline Reference Baseline ({eff_date})",
                is_cached=False,
                is_fallback=True,
                warning=f"Exchange rate API unreachable ({last_error}). Using offline ECB reference baseline.",
            )

        # If completely unsupported pair
        return ExchangeRateResult(
            rate=Decimal("1.0"),
            from_currency=from_curr,
            to_currency=to_curr,
            requested_date=date_key,
            effective_date=get_current_time_str().split()[0],
            source="Unsupported Currency Pair (1:1 Fallback)",
            is_cached=False,
            is_fallback=True,
            warning=f"Unsupported currency conversion {from_curr} to {to_curr}.",
        )


# Global currency service singleton
currency_service = CurrencyService()

