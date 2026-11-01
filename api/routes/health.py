from datetime import datetime
from fastapi import APIRouter, Depends
from config.settings import settings
from core.database import db
from core.embedding_service import embedding_service
from core.gemini_service import gemini_service
from core.pdf_extractor import pdf_extractor
from core.vector_store import vector_store

router = APIRouter(tags=["System & Health"])


@router.get("/health")
def get_health():
    """Basic health check endpoint for monitoring and connectivity validation."""
    return {
        "status": "healthy",
        "service": "Smart Invoice Processor API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/system/status")
def get_system_status():
    """Detailed system diagnostic status across storage, database, vector index, AI, and RPA."""
    inv_counts = db.get_invoice_counts()
    v_stats = vector_store.get_stats()
    gemini_health = gemini_service.check_health()
    active_gmail = db.get_active_gmail_account()
    pref_curr = db.get_setting("preferred_display_currency", "INR")

    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": {
            "status": "online",
            "path": str(settings.DB_PATH),
            "counts": inv_counts,
        },
        "vector_store": {
            "status": "online",
            "collection_name": vector_store.collection_name,
            "total_chunks": v_stats.get("total_chunks", 0),
            "unique_invoices_indexed": v_stats.get("unique_invoices_indexed", 0),
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_dimensions": embedding_service.dimension,
        },
        "ai_service": {
            "provider": "Google Gemini API",
            "is_configured": gemini_service.is_configured,
            "is_available": gemini_health.get("is_available", False),
            "configured_model": settings.GEMINI_MODEL,
            "active_model": gemini_health.get("active_model") or settings.GEMINI_MODEL,
        },
        "ocr_engine": {
            "enabled": settings.OCR_ENABLED,
            "is_supported": pdf_extractor.is_ocr_supported,
        },
        "gmail_automation": {
            "configured": settings.GMAIL_CREDENTIALS_FILE.exists(),
            "connected": active_gmail is not None,
            "connected_email": active_gmail.get("email") if active_gmail else None,
            "last_synced_at": active_gmail.get("last_synced_at") if active_gmail else None,
        },
        "preferences": {
            "preferred_display_currency": pref_curr,
            "exchange_rate_source": "European Central Bank via Frankfurter API",
        },
    }

