import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class QueryType(str, Enum):
    SQL = "sql"          # Exact calculations, sums, dates, counts, comparisons
    RAG = "rag"          # Semantic questions, service descriptions, summaries, topics
    HYBRID = "hybrid"    # Requires both numerical calculation & semantic explanation


@dataclass
class RouteDecision:
    query_type: QueryType
    confidence: float
    reason: str
    target_vendor: Optional[str] = None
    target_invoice: Optional[str] = None


class QueryRouter:
    """
    Classifies user queries into Category A (SQL), Category B (RAG), or Category C (Hybrid).
    Ensures calculations are performed deterministically while semantic questions leverage vector RAG.
    """

    def route(self, query: str) -> RouteDecision:
        q = query.strip()
        q_lower = q.lower()

        # Extract target invoice number if mentioned
        inv_match = re.search(
            r"\b([A-Za-z0-9\-_]{2,15}(?:INV|AWS|MSFT|GCP|TW|SLK|DO|ACME|FN|DCG|CS|TSI|DSA)[A-Za-z0-9\-_]*)\b",
            q,
            re.IGNORECASE,
        )
        target_inv = inv_match.group(1).strip() if inv_match else None

        # Extract vendor if mentioned
        target_vendor = self._detect_vendor(q_lower)

        # Check for Hybrid indicators:
        # User asks both "how much / total spend / spend" AND "what services / why / included / describe / explain"
        calc_indicators = [
            "how much", "total spend", "total spent", "total cost", "spending in",
            "what did we spend", "charged the most", "highest", "convert", "conversion",
            "in inr", "in rupees", "equivalent", "to rupees", "to inr"
        ]
        semantic_indicators = ["what services", "which services", "what was included", "and why", "and what", "explain", "describe", "categories", "service details"]

        has_calc = any(c in q_lower for c in calc_indicators)
        has_semantic = any(s in q_lower for s in semantic_indicators)

        if has_calc and has_semantic:
            return RouteDecision(
                query_type=QueryType.HYBRID,
                confidence=0.92,
                reason="Query requests both exact numerical calculations and semantic service descriptions.",
                target_vendor=target_vendor,
                target_invoice=target_inv,
            )

        # Category B: Pure RAG / Semantic questions
        rag_phrases = [
            "what services", "what did they bill", "billed for", "explain", "describe",
            "summarize", "summary of", "what does the", "cover", "which invoices contain",
            "search for", "find invoices with", "cloud storage charges", "terms", "notes",
            "what was purchased", "line item details", "contract", "address"
        ]
        if any(p in q_lower for p in rag_phrases) and not any(w in q_lower for w in ["how much total", "total spent across", "in inr", "in rupees", "convert"]):
            return RouteDecision(
                query_type=QueryType.RAG,
                confidence=0.90,
                reason="Query asks for document explanation, semantic content, or line item details.",
                target_vendor=target_vendor,
                target_invoice=target_inv,
            )

        # Category A: Pure SQL / Deterministic Financial Calculations
        sql_phrases = [
            "total spend", "total spent", "how much did we spend", "spend on", "cost of",
            "total invoices", "count of invoices", "how many invoices", "highest amount",
            "highest value", "most expensive", "compare spending", "compare", "overdue",
            "unpaid invoices", "pending invoices", "due date", "spending in", "invoices in",
            "in inr", "in rupees", "convert", "conversion", "indian rupees", "equivalent in",
            "to inr", "to rupees"
        ]
        if any(p in q_lower for p in sql_phrases):
            return RouteDecision(
                query_type=QueryType.SQL,
                confidence=0.95,
                reason="Query asks for numerical totals, date filters, or comparisons suitable for exact SQL.",
                target_vendor=target_vendor,
                target_invoice=target_inv,
            )

        # "Show all invoices from [vendor]" is structured SQL
        if "show" in q_lower and ("invoice" in q_lower or target_vendor is not None):
            return RouteDecision(
                query_type=QueryType.SQL,
                confidence=0.88,
                reason="Query requests listing structured invoice records by vendor or filter.",
                target_vendor=target_vendor,
                target_invoice=target_inv,
            )

        # Fallback: if query mentions a specific invoice number and ask to explain/summarize, it's RAG, otherwise SQL
        if target_inv:
            if any(w in q_lower for w in ["what", "services", "items", "details", "about"]):
                return RouteDecision(
                    query_type=QueryType.RAG,
                    confidence=0.85,
                    reason="Query references specific invoice seeking content or line item explanations.",
                    target_vendor=target_vendor,
                    target_invoice=target_inv,
                )

        # Default fallback to Hybrid or RAG if semantic, SQL if short vendor name
        if target_vendor and len(q.split()) <= 4:
            return RouteDecision(
                query_type=QueryType.SQL,
                confidence=0.75,
                reason="Short query referencing a specific vendor routed to SQL summary.",
                target_vendor=target_vendor,
                target_invoice=target_inv,
            )

        return RouteDecision(
            query_type=QueryType.RAG,
            confidence=0.70,
            reason="General natural-language query routed to semantic vector retrieval.",
            target_vendor=target_vendor,
            target_invoice=target_inv,
        )

    def _detect_vendor(self, q_lower: str) -> Optional[str]:
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
            if re.search(r"\b" + re.escape(key) + r"\b", q_lower):
                return name
        return None


# Global query router singleton
query_router = QueryRouter()

