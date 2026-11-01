import time
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import HTTPException, status

from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from core.folder_monitor import folder_monitor, InvoiceProcessingPipeline
from core.gemini_service import gemini_service
from core.gmail_auth_service import gmail_auth_service
from core.gmail_sync_service import gmail_sync_service
from core.query_service import query_service
from core.report_service import report_service
from core.vector_store import vector_store


class SimpleRateLimiter:
    """Sliding-window rate limiter for expensive AI/RAG requests."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, client_id: str = "default") -> None:
        now = time.time()
        window_start = now - self.window_seconds
        # Clean older entries
        self.history[client_id] = [t for t in self.history[client_id] if t > window_start]

        if len(self.history[client_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per minute.",
            )
        self.history[client_id].append(now)


# Global rate limiter singleton
ai_rate_limiter = SimpleRateLimiter(max_requests=40, window_seconds=60)


def get_db():
    return db


def get_currency_service():
    return currency_service


def get_query_service():
    return query_service


def get_vector_store():
    return vector_store


def get_gemini_service():
    return gemini_service


def get_report_service():
    return report_service

