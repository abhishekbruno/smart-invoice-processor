from datetime import datetime
from fastapi import APIRouter, Depends, Request

from api.dependencies import ai_rate_limiter
from api.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatStatusResponse, CitationItem
from core.gemini_service import gemini_service
from core.query_service import query_service
from core.vector_store import vector_store

router = APIRouter(prefix="/chat", tags=["AI & RAG Chat"])


@router.post("/query", response_model=ChatQueryResponse)
def ask_ai_chat(payload: ChatQueryRequest, request: Request):
    """
    Submits a natural language invoice query through the hybrid router.
    Deterministic SQL calculations are enforced for spending aggregations,
    while vector search and Google Gemini 2.5 Flash provide grounded explanations.
    """
    client_ip = request.client.host if request.client else "default"
    ai_rate_limiter.check_rate_limit(client_id=client_ip)

    # Process via existing hybrid query service
    result = query_service.process_query(payload.query)

    citations = [
        CitationItem(
            filename=c.get("filename"),
            invoice_number=c.get("invoice_number"),
            vendor=c.get("vendor"),
            page_number=c.get("page_number"),
            snippet=c.get("snippet"),
        )
        for c in result.get("citations", [])
    ]

    return ChatQueryResponse(
        query=payload.query,
        query_type=result.get("category", "Hybrid"),
        answer=result.get("answer", "No answer could be generated."),
        citations=citations,
        verified_totals=result.get("sql_result"),
        is_fallback=bool(result.get("is_fallback", False)),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/status", response_model=ChatStatusResponse)
def get_chat_status():
    """Checks Google Gemini API readiness and ChromaDB vector index metrics."""
    health = gemini_service.check_health()
    v_stats = vector_store.get_stats()

    return ChatStatusResponse(
        is_gemini_available=health.get("is_available", False),
        configured_model=gemini_service.model,
        active_model=health.get("active_model") or gemini_service.model,
        total_indexed_chunks=v_stats.get("total_chunks", 0),
        unique_invoices_indexed=v_stats.get("unique_invoices_indexed", 0),
        status=health.get("status", "unknown"),
    )

