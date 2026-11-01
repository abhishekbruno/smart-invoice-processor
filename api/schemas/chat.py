from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="Natural language question about invoices")
    session_id: Optional[str] = Field(default=None, description="Optional conversation session identifier")


class CitationItem(BaseModel):
    filename: Optional[str] = None
    invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    page_number: Optional[int] = None
    snippet: Optional[str] = None


class ChatQueryResponse(BaseModel):
    query: str
    query_type: str  # "SQL", "RAG", "Hybrid"
    answer: str
    citations: List[CitationItem] = Field(default_factory=list)
    verified_totals: Optional[Dict[str, Any]] = None
    is_fallback: bool = False
    timestamp: str


class ChatStatusResponse(BaseModel):
    is_gemini_available: bool
    configured_model: str
    active_model: Optional[str] = None
    total_indexed_chunks: int
    unique_invoices_indexed: int
    status: str

