from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.schemas.common import APIResponse
from config.settings import settings
from core.currency_service import currency_service
from core.database import db
from core.vector_store import vector_store

router = APIRouter(prefix="/settings", tags=["Preferences & Settings"])


class CurrencyPreferenceRequest(BaseModel):
    currency: str = Field(..., pattern="^(INR|USD|EUR|GBP)$", description="Preferred display currency code")


@router.get("")
def get_all_settings():
    """Retrieves all application configuration values, storage paths, and multi-currency preferences."""
    pref_curr = db.get_setting("preferred_display_currency", "INR")

    latest_rates = {}
    try:
        rates_data = currency_service.get_latest_rates(base_currency="USD")
        latest_rates = {k: float(v) for k, v in rates_data.get("rates", {}).items()}
    except Exception:
        pass

    return {
        "success": True,
        "data": {
            "preferred_display_currency": pref_curr,
            "supported_currencies": ["INR", "USD", "EUR", "GBP"],
            "latest_reference_rates_usd": latest_rates,
            "exchange_rate_source": currency_service.SOURCE_LABEL,
            "storage": {
                "watch_dir": str(settings.INVOICE_WATCH_DIR),
                "processed_dir": str(settings.PROCESSED_DIR),
                "db_path": str(settings.DB_PATH),
                "chroma_dir": str(settings.CHROMA_DIR),
            },
            "ai": {
                "gemini_model": settings.GEMINI_MODEL,
                "embedding_model": settings.EMBEDDING_MODEL,
            },
        },
    }


@router.post("/currency", response_model=APIResponse[dict])
def update_currency_preference(payload: CurrencyPreferenceRequest):
    """Sets the preferred display currency used for converted financial valuation."""
    db.set_setting("preferred_display_currency", payload.currency)
    return APIResponse(
        success=True,
        message=f"Preferred currency updated to {payload.currency}",
        data={"preferred_display_currency": payload.currency},
    )


@router.post("/reindex", response_model=APIResponse[dict])
def reindex_vector_store():
    """Forces re-indexing of all database invoices into the ChromaDB vector store."""
    try:
        res = vector_store.reindex_all(db, force=True)
        return APIResponse(
            success=True,
            message="Vector store successfully reindexed",
            data=res,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}",
        )

