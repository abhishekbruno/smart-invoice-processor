from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GeminiLineItemExtraction(BaseModel):
    """Pydantic validation schema for AI-extracted line items."""
    description: str = Field(default="", description="Description of the item or service")
    quantity: Optional[float] = Field(default=1.0, description="Quantity")
    unit_price: Optional[float] = Field(default=0.0, description="Unit price")
    amount: Optional[float] = Field(default=0.0, description="Total amount for item")


class GeminiInvoiceExtraction(BaseModel):
    """Pydantic validation schema for Level 3 AI-assisted invoice field extraction."""
    vendor_name: Optional[str] = Field(default=None, description="Name of the vendor")
    invoice_number: Optional[str] = Field(default=None, description="Invoice identifier")
    invoice_date: Optional[str] = Field(default=None, description="Invoice date in YYYY-MM-DD")
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD")
    customer_name: Optional[str] = Field(default=None, description="Customer or billed-to name")
    subtotal: Optional[float] = Field(default=None, description="Subtotal amount")
    tax_amount: Optional[float] = Field(default=None, description="Tax amount")
    discount: Optional[float] = Field(default=0.0, description="Discount amount")
    total_amount: Optional[float] = Field(default=None, description="Grand total amount")
    currency: Optional[str] = Field(default="USD", description="3-letter currency code")
    payment_status: Optional[str] = Field(default=None, description="Explicit payment status")
    line_items: List[GeminiLineItemExtraction] = Field(default_factory=list, description="Line items")


@dataclass
class LineItem:
    """Represents a single billable item or service line from an invoice."""
    description: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = 0.0
    amount: Optional[float] = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class InvoiceData:
    """Structured data extracted from an invoice document."""
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[str] = None  # ISO: YYYY-MM-DD
    due_date: Optional[str] = None      # ISO: YYYY-MM-DD
    customer_name: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    payment_status: Optional[str] = None  # e.g., PAID, PENDING, OVERDUE, DUE
    line_items: List[LineItem] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    raw_text: str = ""
    needs_review: bool = False
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None
    duplicate_reason: Optional[str] = None
    extraction_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["line_items"] = [item.to_dict() for item in self.line_items]
        return d


@dataclass
class ProcessingRecord:
    """Audit log record for document processing events."""
    file_name: str
    file_path: str
    file_hash: str
    file_size: int
    status: str  # 'success', 'failed', 'duplicate', 'needs_review'
    error_message: Optional[str] = None
    duration_sec: float = 0.0
    processed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

