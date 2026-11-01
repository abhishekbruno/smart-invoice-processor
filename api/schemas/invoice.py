from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LineItemResponse(BaseModel):
    id: Optional[int] = None
    description: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = 0.0
    amount: Optional[float] = 0.0


class InvoiceListItem(BaseModel):
    id: int
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    converted_amount: Optional[float] = None
    converted_currency: Optional[str] = "INR"
    status: str
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None
    duplicate_reason: Optional[str] = None
    created_at: str


class InvoiceDetailResponse(InvoiceListItem):
    customer_name: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    payment_status: Optional[str] = None
    source_file_path: Optional[str] = None
    file_hash: str
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    extraction_notes: List[str] = Field(default_factory=list)
    line_items: List[LineItemResponse] = Field(default_factory=list)
    updated_at: Optional[str] = None


class InvoiceUpdateRequest(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    customer_name: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    payment_status: Optional[str] = None
    status: Optional[str] = None


class InvoiceUploadResponse(BaseModel):
    status: str
    invoice_id: Optional[int] = None
    file_name: str
    file_hash: Optional[str] = None
    is_duplicate: bool = False
    duplicate_reason: Optional[str] = None
    message: str

