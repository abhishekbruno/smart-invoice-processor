import pytest
import sqlite3
from core.database import db
from core.query_service import query_service
from core.rag_pipeline import RAGPipeline
from utils.helpers import format_financial_markdown, format_currency_amount


def test_format_financial_markdown_escapes_dollar_signs():
    sample = "Invoice Total: **$793.80** per invoice (combining the verified total of **$1,587.60** across both invoices)."
    formatted = format_financial_markdown(sample)
    assert r"\$793.80" in formatted
    assert r"\$1,587.60" in formatted
    # Ensure raw unescaped $ does not exist
    assert " $793.80" not in formatted
    assert " $1,587.60" not in formatted


def test_format_financial_markdown_preserves_decimals_commas_and_symbols():
    text = (
        "### Per-Invoice Breakdown\n\n"
        "- Services Subtotal: $735.00\n"
        "- Tax Amount: $58.80\n"
        "- **Invoice Total: $793.80**\n\n"
        "### Combined Spending Summary\n\n"
        "- Number of invoices: 2\n"
        "- **Combined Total: $1,587.60**"
    )
    formatted = format_financial_markdown(text)
    assert r"- Services Subtotal: \$735.00" in formatted
    assert r"- Tax Amount: \$58.80" in formatted
    assert r"- **Invoice Total: \$793.80**" in formatted
    assert r"- **Combined Total: \$1,587.60**" in formatted

    # Other currency symbols should remain untouched
    multi_curr = "EUR: €5,150.00, GBP: £780.00, INR: ₹1,75,000.00"
    formatted_curr = format_financial_markdown(multi_curr)
    assert "€5,150.00" in formatted_curr
    assert "£780.00" in formatted_curr
    assert "₹1,75,000.00" in formatted_curr


def test_format_financial_markdown_code_blocks_unaltered():
    code_text = "Here is the code: `total = $100` and block:\n```python\nval = '$200'\n```\nOutside: $300.00"
    formatted = format_financial_markdown(code_text)
    assert "`total = $100`" in formatted
    assert "val = '$200'" in formatted
    assert r"Outside: \$300.00" in formatted


def test_broken_asterisks_fixed():
    broken = "Invoice Total: 793.80 * *per invoice (combining the verified total of * *1,587.60 across both invoices)."
    fixed = format_financial_markdown(broken)
    assert "* *" not in fixed
    assert "**" in fixed


def test_idempotent_escaping():
    original = "Total: $793.80"
    once = format_financial_markdown(original)
    twice = format_financial_markdown(once)
    assert once == r"Total: \$793.80"
    assert twice == r"Total: \$793.80"
    assert r"\\$" not in twice


def test_query_vendor_spending_per_invoice_and_combined_breakdown():
    res = query_service.process_query("What did we spend on AWS?")
    ans = res["answer"]

    # Verify Markdown sections
    assert "### Per-Invoice Breakdown" in ans
    assert "- Services Subtotal: $735.00" in ans
    assert "- Tax Amount: $58.80" in ans
    assert "- **Invoice Total: $793.80**" in ans

    assert "### Combined Spending Summary" in ans
    assert "- Number of invoices: 1" in ans
    assert "- **Combined Total: $793.80**" in ans
    assert "suspected duplicate record(s) excluded" in ans


def test_confirm_aws_invoices_are_distinct_records():
    """Confirms the two invoices represent distinct records on disk/DB, with duplicate detection correctly identifying ID 14."""
    invoices = db.get_all_invoices(vendor="Amazon Web Services")
    assert len(invoices) == 2, f"Expected 2 AWS invoices, got {len(invoices)}"

    inv1, inv2 = invoices[0], invoices[1]

    # Verify distinct database IDs
    assert inv1["id"] != inv2["id"], "Records must have distinct primary keys"
    assert {inv1["id"], inv2["id"]} == {2, 14}

    # Verify distinct SHA-256 file hashes
    assert inv1["file_hash"] != inv2["file_hash"], "Records must have distinct file hashes"

    # Verify duplicate detection flagged ID 14 as duplicate of ID 2
    id2_record = inv1 if inv1["id"] == 2 else inv2
    id14_record = inv1 if inv1["id"] == 14 else inv2
    assert id2_record["is_duplicate"] == 0
    assert id14_record["is_duplicate"] == 1
    assert id14_record["duplicate_of_id"] == 2
    assert id14_record["status"] == "suspected_duplicate"


def test_hybrid_rag_pipeline_preserves_sqlite_financial_totals():
    class MockGeminiService:
        @property
        def is_available(self):
            return True

        def generate(self, prompt, system_prompt=None):
            return (
                "Based on the invoice excerpts, Amazon Web Services billed for:\n\n"
                "- Amazon EC2 Linux and ARM compute instances\n"
                "- Amazon S3 Standard storage\n"
                "- Amazon RDS Multi-AZ PostgreSQL database"
            )

    pipeline = RAGPipeline(llm=MockGeminiService())
    response = pipeline.answer_query("How much did we spend on AWS and what services were included?")

    assert response.query_type == "hybrid"
    assert response.is_llm_generated

    ans = response.answer
    # Must contain both SQLite sections
    assert "### Per-Invoice Breakdown" in ans
    assert r"- Services Subtotal: \$735.00" in ans
    assert r"- Tax Amount: \$58.80" in ans
    assert r"- **Invoice Total: \$793.80**" in ans
    assert "### Combined Spending Summary" in ans
    assert "- Number of invoices: 1" in ans
    assert r"- **Combined Total: \$793.80**" in ans

    # Must contain LLM explanation
    assert "Amazon EC2" in ans
    assert "Amazon S3" in ans
    assert "Amazon RDS" in ans

    # Must have all raw dollar signs properly escaped for Streamlit
    import re
    raw_dollars = re.findall(r"(?<!\\)\$", ans)
    assert len(raw_dollars) == 0, f"Found unescaped dollar signs: {raw_dollars}"

