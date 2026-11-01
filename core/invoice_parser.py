import re
from typing import Dict, List, Optional, Tuple
from core.models import InvoiceData, LineItem
from core.pdf_extractor import ExtractedDocument
from utils.helpers import clean_extracted_text, normalize_currency, parse_date_string
from utils.logger import logger

# Well-known enterprise and tech vendors for enhanced detection
KNOWN_VENDORS = [
    "Amazon Web Services", "AWS", "Amazon Web Services, Inc.",
    "Microsoft", "Microsoft Corporation",
    "Google Cloud", "Google Cloud Platform", "Google LLC",
    "Twilio", "Twilio Inc.",
    "Slack", "Slack Technologies", "Slack Technologies Limited",
    "DigitalOcean", "DigitalOcean, LLC",
    "GitHub", "GitHub, Inc.",
    "Stripe", "Stripe, Inc.",
    "Atlassian", "Atlassian Pty Ltd",
    "Datadog", "Datadog, Inc.",
    "Cloudflare", "Cloudflare, Inc.",
    "Acme Office Supplies", "Acme Corp",
    "FastNet Internet Services",
    "DevConsulting Group",
    "CyberShield Security",
]

# Company suffix regex pattern
COMPANY_SUFFIX_PATTERN = re.compile(
    r"\b(Inc\.?|LLC|Ltd\.?|Limited|Corp\.?|Corporation|Technologies|Tech|Solutions|Services|GmbH|Co\.?|Pvt\.?\s*Ltd\.?)\b",
    re.IGNORECASE,
)


class InvoiceParser:
    """Extracts structured invoice fields from raw/cleaned text using robust heuristics & regex."""

    def parse(self, doc: ExtractedDocument, use_gemini_fallback: bool = False) -> InvoiceData:
        """Parses extracted document text into an InvoiceData instance."""
        text = doc.cleaned_text
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        confidence: Dict[str, float] = {}
        notes: List[str] = list(doc.warnings)

        # 1. Currency
        currency = self._extract_currency(text)

        # 2. Invoice Number
        inv_number, inv_num_conf = self._extract_invoice_number(text, lines)
        confidence["invoice_number"] = inv_num_conf
        if not inv_number:
            notes.append("Invoice number could not be determined with high certainty.")

        # 3. Vendor Name
        vendor, vendor_conf = self._extract_vendor_name(text, lines)
        confidence["vendor_name"] = vendor_conf
        if not vendor:
            notes.append("Vendor name could not be identified.")

        # 4. Dates
        inv_date, inv_date_conf = self._extract_invoice_date(text)
        confidence["invoice_date"] = inv_date_conf
        if not inv_date:
            notes.append("Invoice date is missing or unparseable.")

        due_date, due_date_conf = self._extract_due_date(text)
        confidence["due_date"] = due_date_conf

        # 5. Customer Name
        customer, cust_conf = self._extract_customer_name(text, lines)
        confidence["customer_name"] = cust_conf

        # 6. Amounts
        subtotal, tax, total, amounts_conf = self._extract_financial_amounts(text)
        confidence.update(amounts_conf)
        if total is None:
            notes.append("Total amount was not detected in document.")

        # 7. Line Items
        line_items = self._extract_line_items(lines)

        # 8. Payment Status (Strict - only if explicitly stated)
        payment_status = self._extract_payment_status(text)

        # 9. Determine Review Flag
        needs_review = False
        if total is None or total <= 0:
            needs_review = True
            notes.append("Flagged for review: Missing or zero total amount.")
        if not vendor:
            needs_review = True
            notes.append("Flagged for review: Missing vendor name.")
        if not inv_date:
            needs_review = True
            notes.append("Flagged for review: Missing invoice date.")
        if inv_num_conf < 0.5 or vendor_conf < 0.5:
            needs_review = True
            notes.append("Flagged for review: Low confidence score on key identifying fields.")

        inv_data = InvoiceData(
            invoice_number=inv_number,
            vendor_name=vendor,
            invoice_date=inv_date,
            due_date=due_date,
            customer_name=customer,
            subtotal=subtotal,
            tax_amount=tax,
            total_amount=total,
            currency=currency,
            payment_status=payment_status,
            line_items=line_items,
            confidence_scores=confidence,
            raw_text=text,
            needs_review=needs_review,
            extraction_notes=notes,
        )

        # Level 3: Optional Gemini-assisted structured extraction for missing/uncertain fields
        if inv_data.needs_review and use_gemini_fallback:
            inv_data = self.enhance_with_gemini_extraction(inv_data, text)

        return inv_data

    def enhance_with_gemini_extraction(self, invoice_data: InvoiceData, raw_text: str) -> InvoiceData:
        """
        Level 3 AI Extraction: When rule-based extraction leaves key fields missing or has low confidence,
        optionally consults Google Gemini with JSON schema validation.
        Validates amounts and checks mathematical consistency: subtotal + tax - discount == total.
        Never blindly overwrites verified rule-based values.
        """
        import json
        from core.gemini_service import gemini_service
        from core.models import GeminiInvoiceExtraction, LineItem

        if not gemini_service.is_configured:
            return invoice_data

        prompt = f"""Extract structured invoice fields from the following invoice text into strict JSON format matching this schema:
{{
  "vendor_name": "Company or vendor name",
  "invoice_number": "Invoice reference number",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "customer_name": "Billed customer name",
  "subtotal": 0.0,
  "tax_amount": 0.0,
  "discount": 0.0,
  "total_amount": 0.0,
  "currency": "3-letter currency code (e.g. USD, EUR, GBP, INR)",
  "payment_status": "PAID / UNPAID / DUE / etc.",
  "line_items": [
    {{"description": "Item description", "quantity": 1.0, "unit_price": 0.0, "amount": 0.0}}
  ]
}}

Invoice Text:
---
{raw_text[:3500]}
---

Return ONLY raw JSON, with no markdown code fences or conversational text.
"""
        try:
            raw_response = gemini_service.generate(
                prompt=prompt,
                system_prompt="You are an expert invoice processing and financial data extraction specialist. Output valid JSON only.",
                temperature=0.0,
            )
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = re.sub(r"^```(?:json)?\s*", "", clean_json)
                clean_json = re.sub(r"\s*```$", "", clean_json)

            data_dict = json.loads(clean_json)
            validated = GeminiInvoiceExtraction.model_validate(data_dict)

            # Check math consistency: subtotal + tax - discount ~= total
            math_consistent = False
            if validated.total_amount is not None and validated.subtotal is not None:
                calc_total = validated.subtotal + (validated.tax_amount or 0.0) - (validated.discount or 0.0)
                if abs(calc_total - validated.total_amount) < 0.05:
                    math_consistent = True

            # Fill missing or low-confidence fields safely
            if (not invoice_data.vendor_name or invoice_data.confidence_scores.get("vendor_name", 0.0) < 0.90) and validated.vendor_name:
                invoice_data.vendor_name = validated.vendor_name
                invoice_data.confidence_scores["vendor_name"] = 0.95
                invoice_data.extraction_notes.append(f"Vendor name extracted via Gemini: {validated.vendor_name}")

            if (not invoice_data.invoice_number or invoice_data.confidence_scores.get("invoice_number", 0.0) < 0.90) and validated.invoice_number:
                invoice_data.invoice_number = validated.invoice_number
                invoice_data.confidence_scores["invoice_number"] = 0.95
                invoice_data.extraction_notes.append(f"Invoice number extracted via Gemini: {validated.invoice_number}")

            if not invoice_data.invoice_date and validated.invoice_date:
                invoice_data.invoice_date = validated.invoice_date
                invoice_data.confidence_scores["invoice_date"] = 0.85

            if not invoice_data.due_date and validated.due_date:
                invoice_data.due_date = validated.due_date

            if not invoice_data.customer_name and validated.customer_name:
                invoice_data.customer_name = validated.customer_name

            if invoice_data.total_amount is None and validated.total_amount is not None:
                if math_consistent or validated.total_amount > 0:
                    invoice_data.total_amount = validated.total_amount
                    invoice_data.confidence_scores["total_amount"] = 0.9 if math_consistent else 0.7
                    invoice_data.extraction_notes.append(
                        f"Total amount extracted via Gemini: {validated.total_amount} (Math consistent: {math_consistent})"
                    )

            if invoice_data.subtotal is None and validated.subtotal is not None:
                invoice_data.subtotal = validated.subtotal

            if invoice_data.tax_amount is None and validated.tax_amount is not None:
                invoice_data.tax_amount = validated.tax_amount

            if not invoice_data.line_items and validated.line_items:
                invoice_data.line_items = [
                    LineItem(
                        description=item.description,
                        quantity=item.quantity or 1.0,
                        unit_price=item.unit_price or 0.0,
                        amount=item.amount or 0.0,
                    )
                    for item in validated.line_items
                ]

            # If core fields are now complete and valid, update needs_review
            if (
                invoice_data.vendor_name
                and invoice_data.total_amount is not None
                and invoice_data.total_amount > 0
                and invoice_data.invoice_date
                and (math_consistent or validated.subtotal is None)
            ):
                invoice_data.needs_review = False

        except Exception as e:
            logger.warning(f"Level 3 Gemini extraction fallback note: {e}")
            invoice_data.extraction_notes.append(f"AI extraction fallback attempted: {str(e)[:100]}")

        return invoice_data

    # =========================================================================
    # Extraction Helpers
    # =========================================================================

    def _extract_currency(self, text: str) -> str:
        """Detects the primary currency in the document."""
        # Prioritize symbols with explicit context
        if "₹" in text or "INR" in text or "Rs." in text:
            return "INR"
        if "€" in text or "EUR" in text:
            return "EUR"
        if "£" in text or "GBP" in text:
            return "GBP"
        if "CA$" in text or "CAD" in text:
            return "CAD"
        if "AU$" in text or "AUD" in text:
            return "AUD"
        if "$" in text or "USD" in text:
            return "USD"
        return "USD"

    def _extract_invoice_number(self, text: str, lines: List[str]) -> Tuple[Optional[str], float]:
        """Extracts invoice identifier."""
        # Clean reject words
        invalid_words = {
            "invoice", "inv", "bill", "receipt", "date", "number", "due",
            "total", "amount", "usd", "tax", "status", "paid", "pending", "overdue"
        }

        patterns = [
            # Explicit label with #, :, or No.
            (r"(?i)(?:invoice\s*#|inv\s*#|invoice\s*number|invoice\s*no\.?|bill\s*no\.?|bill\s*#)[\s:]*([A-Za-z0-9\-_\/]{3,30})", 0.95),
            (r"(?i)(?:reference\s*no\.?|ref\s*#?)[\s:]*([A-Za-z0-9\-_\/]{3,30})", 0.85),
            # Standard prefix pattern like INV-AWS-2024-8192 or MSFT-INV-99214
            (r"\b([A-Z]{2,6}-INV-[A-Za-z0-9\-_]{3,20})\b", 0.95),
            (r"\b(INV-[A-Za-z0-9\-_]{3,20})\b", 0.95),
            (r"(?i)invoice\s*:\s*([A-Za-z0-9\-_\/]{3,30})", 0.90),
            (r"(?i)#\s*([A-Za-z0-9\-_\/]{4,20})\b", 0.70),
        ]

        for pattern, conf in patterns:
            for match in re.finditer(pattern, text):
                candidate = match.group(1).strip()
                # Clean punctuation
                candidate = re.sub(r"^[\W_]+|[\W_]+$", "", candidate)
                if candidate.lower() not in invalid_words and len(candidate) >= 3:
                    return candidate, conf

        return None, 0.0

    def _extract_vendor_name(self, text: str, lines: List[str]) -> Tuple[Optional[str], float]:
        """Extracts vendor / issuer organization."""
        # 1. Check known vendors list (supporting whitespace / linebreaks between words)
        for known in KNOWN_VENDORS:
            words = known.split()
            escaped_words = [re.escape(w) for w in words]
            flex_pattern = r"\b" + r"[\s\n]+".join(escaped_words) + r"\b"
            if re.search(flex_pattern, text, re.IGNORECASE):
                return known, 0.95

        # 2. Check for explicit "From:" or "Seller:" or "Vendor:"
        from_match = re.search(r"(?i)(?:from|seller|billed\s*by|vendor)[\s:]*\n?([^\n]{3,80})", text)
        if from_match:
            candidate = from_match.group(1).strip()
            candidate = re.sub(r"^(?:is\s+|from|seller|vendor|billed\s*by)[\s:]*", "", candidate, flags=re.IGNORECASE).strip()
            candidate = re.split(r"[.\n;]|\b(?:reference|invoice|total|bill\s*to|phone|email)\b", candidate, flags=re.IGNORECASE)[0].strip()
            if len(candidate) > 2 and not candidate.lower().startswith(("invoice", "bill to", "tax")):
                return candidate, 0.85

        # 3. Look in the first 6 lines for company indicators (Inc, LLC, etc.)
        for line in lines[:6]:
            if COMPANY_SUFFIX_PATTERN.search(line):
                if not re.search(r"(?i)\b(bill to|invoice to|customer|client)\b", line):
                    return line.strip(), 0.75

        # 4. Fallback: First non-empty line if short enough and not generic header
        if lines:
            first_line = lines[0].strip()
            if 3 <= len(first_line) <= 50 and not re.search(r"(?i)\b(invoice|receipt|tax|bill|statement)\b", first_line):
                return first_line, 0.50

        return None, 0.0

    def _extract_invoice_date(self, text: str) -> Tuple[Optional[str], float]:
        """Extracts invoice creation or issue date."""
        patterns = [
            (r"(?i)(?:invoice\s*date|bill\s*date|date\s*of\s*issue|issue\s*date|dated)[\s:]+([A-Za-z0-9\s,\/\.\-]{6,25})", 0.95),
            (r"(?i)\bdate[\s:]+([A-Za-z0-9\s,\/\.\-]{6,25})", 0.75),
        ]

        for pattern, conf in patterns:
            match = re.search(pattern, text)
            if match:
                raw_date = match.group(1).strip()
                # Stop before newline or next field label
                raw_date = re.split(r"[\n\r]|due|invoice|total|page", raw_date, flags=re.IGNORECASE)[0].strip()
                parsed = parse_date_string(raw_date)
                if parsed:
                    return parsed, conf

        # Generic date search fallback
        generic_match = re.search(r"\b(20\d\d[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01]))\b", text)
        if generic_match:
            parsed = parse_date_string(generic_match.group(1))
            if parsed:
                return parsed, 0.60

        return None, 0.0

    def _extract_due_date(self, text: str) -> Tuple[Optional[str], float]:
        """Extracts invoice payment due date."""
        patterns = [
            (r"(?i)(?:due\s*date|payment\s*due|pay\s*by|due\s*on)[\s:]+([A-Za-z0-9\s,\/\.\-]{6,25})", 0.95),
            (r"(?i)\bdue[\s:]+([A-Za-z0-9\s,\/\.\-]{6,25})", 0.70),
        ]

        for pattern, conf in patterns:
            match = re.search(pattern, text)
            if match:
                raw_date = match.group(1).strip()
                raw_date = re.split(r"[\n\r]|invoice|total|amount", raw_date, flags=re.IGNORECASE)[0].strip()
                parsed = parse_date_string(raw_date)
                if parsed:
                    return parsed, conf

        return None, 0.0

    def _extract_customer_name(self, text: str, lines: List[str]) -> Tuple[Optional[str], float]:
        """Extracts billed customer / client name."""
        match = re.search(
            r"(?i)(?:bill\s*to|invoice\s*to|billed\s*to|client|sold\s*to|customer)[\s:]*\n?([^\n]{3,60})",
            text,
        )
        if match:
            candidate = match.group(1).strip()
            # Clean common label repetition
            candidate = re.sub(r"^(?:bill to|invoice to|client|customer)[\s:]*", "", candidate, flags=re.IGNORECASE).strip()
            if candidate and not re.search(r"(?i)(invoice|date|amount|total|number)", candidate):
                return candidate, 0.85

        return None, 0.0

    def _extract_financial_amounts(
        self, text: str
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Dict[str, float]]:
        """
        Extracts subtotal, tax amount, and total amount.
        Supports international and Indian comma separation (e.g., 1,45,000.00 or 145,000.00).
        Returns (subtotal, tax_amount, total_amount, confidence_dict).
        """
        confidence: Dict[str, float] = {}

        # Currency prefix pattern
        curr_prefix = r"(?:[$€£₹]|INR|USD|EUR|GBP|Rs\.?|[A-Za-z]{1,3})?"
        # Number pattern supporting standard (1,234.56) and Indian lakh (1,23,456.78) formatting
        num_pattern = r"([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2}))"

        # 1. Total Amount Patterns (supports Total (USD):, Grand Total:, Balance Due:, etc.)
        total_val: Optional[float] = None
        total_patterns = [
            (rf"(?i)(?:total\s*(?:\([A-Za-z]+\))?|grand\s*total|amount\s*due|total\s*due|balance\s*due|net\s*payable)[\s:]*{curr_prefix}\s*{num_pattern}", 0.95),
            (rf"(?i)(?:total\s*amount)[\s:]*{curr_prefix}\s*{num_pattern}", 0.95),
            (rf"(?i)\btotal[\s:]*{curr_prefix}\s*{num_pattern}", 0.85),
        ]

        for pat, conf in total_patterns:
            matches = list(re.finditer(pat, text))
            if matches:
                # The last total match on an invoice is usually the summary grand total
                last_match = matches[-1]
                num_str = last_match.group(1).replace(",", "")
                try:
                    total_val = float(num_str)
                    confidence["total_amount"] = conf
                    break
                except ValueError:
                    continue

        # 2. Subtotal Patterns
        subtotal_val: Optional[float] = None
        subtotal_match = re.search(
            rf"(?i)(?:sub\s*total|subtotal|net\s*amount|taxable\s*amount)[\s:]*{curr_prefix}\s*{num_pattern}",
            text,
        )
        if subtotal_match:
            num_str = subtotal_match.group(1).replace(",", "")
            try:
                subtotal_val = float(num_str)
                confidence["subtotal"] = 0.90
            except ValueError:
                pass

        # 3. Tax Amount Patterns
        tax_val: Optional[float] = None
        tax_match = re.search(
            rf"(?i)(?:tax(?:\s*amount)?|vat(?:\s*amount)?|gst(?:\s*amount)?|sales\s*tax)[\s:]*{curr_prefix}\s*{num_pattern}",
            text,
        )
        if tax_match:
            num_str = tax_match.group(1).replace(",", "")
            try:
                tax_val = float(num_str)
                confidence["tax_amount"] = 0.85
            except ValueError:
                pass

        # Consistency verification
        if subtotal_val is not None and tax_val is not None and total_val is not None:
            expected = subtotal_val + tax_val
            if abs(expected - total_val) < 0.05:
                confidence["total_amount"] = 1.0
                confidence["subtotal"] = 0.98
                confidence["tax_amount"] = 0.98

        return subtotal_val, tax_val, total_val, confidence

    def _extract_line_items(self, lines: List[str]) -> List[LineItem]:
        """Extracts individual line items from invoice text supporting both single-line and multi-line layouts."""
        items: List[LineItem] = []
        ignore_words = {
            "subtotal", "total", "tax", "vat", "gst", "amount due", "balance",
            "invoice", "date", "qty", "description", "unit price", "price", "amount",
            "thank you", "billing inquiries", "status", "bill to"
        }

        # 1. Check for consecutive 4-line table block structure:
        # Line i: Description
        # Line i+1: Qty (e.g. 1, 2, 25000.0)
        # Line i+2: Unit Price (e.g. $145.00)
        # Line i+3: Amount (e.g. $435.00)
        i = 0
        n = len(lines)
        amount_regex = re.compile(r"^[$€£₹]?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2}))$")
        qty_regex = re.compile(r"^\d+(?:\.\d+)?$")

        while i < n - 3:
            desc_candidate = lines[i].strip()
            qty_candidate = lines[i + 1].strip()
            unit_candidate = lines[i + 2].strip()
            amt_candidate = lines[i + 3].strip()

            if (
                desc_candidate.lower() not in ignore_words
                and not any(w in desc_candidate.lower() for w in ("subtotal:", "tax amount:", "total (", "bill to:"))
                and qty_regex.match(qty_candidate)
                and amount_regex.match(unit_candidate)
                and amount_regex.match(amt_candidate)
            ):
                try:
                    qty = float(qty_candidate)
                    unit_m = amount_regex.match(unit_candidate)
                    amt_m = amount_regex.match(amt_candidate)
                    if unit_m and amt_m:
                        unit = float(unit_m.group(1).replace(",", ""))
                        amt = float(amt_m.group(1).replace(",", ""))
                        items.append(LineItem(description=desc_candidate, quantity=qty, unit_price=unit, amount=amt))
                        i += 4
                        continue
                except ValueError:
                    pass

            i += 1

        # 2. Check for single-line format if no items found
        if not items:
            pattern_with_qty = re.compile(
                r"^(?P<desc>[A-Za-z0-9\s\-_\/()#.,]{3,45})\s+(?P<qty>\d+(?:\.\d+)?)\s+[$€£₹]?(?P<unit>\d+(?:,\d{3})*(?:\.\d{2})?)\s+[$€£₹]?(?P<amount>\d+(?:,\d{3})*(?:\.\d{2})?)$"
            )
            for line in lines:
                line_lower = line.lower()
                if any(w in line_lower for w in ignore_words):
                    continue
                m1 = pattern_with_qty.match(line)
                if m1:
                    try:
                        desc = m1.group("desc").strip()
                        qty = float(m1.group("qty"))
                        unit = float(m1.group("unit").replace(",", ""))
                        amt = float(m1.group("amount").replace(",", ""))
                        items.append(LineItem(description=desc, quantity=qty, unit_price=unit, amount=amt))
                    except ValueError:
                        continue

        return items

    def _extract_payment_status(self, text: str) -> Optional[str]:
        """
        Extracts payment status ONLY when explicitly stated in document.
        Does not guess or assume.
        """
        # Look for explicit status declarations
        if re.search(r"(?i)\bstatus[\s:]*\bpaid\b|\bpayment\s*status[\s:]*\bpaid\b|\bmark(?:ed)?\s*as\s*paid\b|\bpaid\s*in\s*full\b", text):
            return "PAID"
        if re.search(r"(?i)\bstatus[\s:]*\bunpaid\b|\bpayment\s*status[\s:]*\bunpaid\b", text):
            return "UNPAID"
        if re.search(r"(?i)\bstatus[\s:]*\bpending\b|\bpayment\s*status[\s:]*\bpending\b", text):
            return "PENDING"
        if re.search(r"(?i)\bstatus[\s:]*\boverdue\b|\bpayment\s*status[\s:]*\boverdue\b|\bpast\s*due\b", text):
            return "OVERDUE"
        if re.search(r"(?i)\bdue\s*upon\s*receipt\b", text):
            return "DUE UPON RECEIPT"

        # Check for standalone large PAID stamp text
        if re.search(r"\bPAID\b", text) and not re.search(r"(?i)\bpaid\s*by\b|\bif\s*paid\b", text):
            return "PAID"

        return None


# Global parser singleton
invoice_parser = InvoiceParser()
