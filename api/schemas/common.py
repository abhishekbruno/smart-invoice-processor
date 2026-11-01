from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard unified response wrapper for all API endpoints."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper for list endpoints."""
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

