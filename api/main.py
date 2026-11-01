import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import analytics, automation, chat, health, invoices, reports, settings
from config.settings import settings as app_settings
from utils.logger import logger

# Initialize FastAPI application
app = FastAPI(
    title="Smart Invoice Processor API",
    description="Unified REST API serving React web dashboard and Flutter Android mobile app with RPA, RAG, and multi-currency intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurable CORS for development origins
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

env_origins = os.getenv("CORS_ORIGINS", "").split(",")
allowed_origins = [o.strip() for o in env_origins if o.strip()] or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.0\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled API error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "error": str(exc) if app_settings.APP_ENV == "development" else "Internal server error",
        },
    )

# Register route modules under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(automation.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.get("/")
def root():
    """Root redirect / index info."""
    return {
        "service": "Smart Invoice Processor API",
        "documentation": "/docs",
        "status": "online",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

