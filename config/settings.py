import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from root if it exists
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()


class Settings:
    """Central configuration for Smart Invoice Processor."""

    def __init__(self):
        # Environment
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.TIMEZONE: str = os.getenv("APP_TIMEZONE", "Asia/Kolkata")
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # Directories
        self.BASE_DIR: Path = BASE_DIR
        self.INVOICE_WATCH_DIR: Path = self._resolve_path(
            os.getenv("INVOICE_WATCH_DIR", "data/invoices")
        )
        self.PROCESSED_DIR: Path = self._resolve_path(
            os.getenv("PROCESSED_DIR", "data/processed")
        )
        self.SAMPLES_DIR: Path = self._resolve_path("data/samples")
        self.LOGS_DIR: Path = self._resolve_path("logs")
        self.DB_PATH: Path = self._resolve_path(
            os.getenv("DB_PATH", "data/invoices.db")
        )
        self.CHROMA_DIR: Path = self._resolve_path(
            os.getenv("CHROMA_DIR", "storage/chroma")
        )

        # File processing limits
        self.MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
        self.MAX_FILE_SIZE_BYTES: int = self.MAX_FILE_SIZE_MB * 1024 * 1024

        # OCR configuration
        self.OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "false").lower() in ("1", "true", "yes")
        self.TESSERACT_PATH: Optional[str] = os.getenv("TESSERACT_PATH", None)

        # AI & Embeddings (Phase 2 - Google Gemini API)
        self.EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Gmail Integration (Phase 3)
        self.GMAIL_CREDENTIALS_FILE: Path = self._resolve_path(
            os.getenv("GMAIL_CREDENTIALS_FILE", "config/credentials.json")
        )
        self.GMAIL_TOKEN_FILE: Path = self._resolve_path(
            os.getenv("GMAIL_TOKEN_FILE", "config/token.json")
        )
        self.GMAIL_SYNC_INTERVAL_MINUTES: int = int(
            os.getenv("GMAIL_SYNC_INTERVAL_MINUTES", "15")
        )
        self.GMAIL_SEARCH_QUERY: str = os.getenv(
            "GMAIL_SEARCH_QUERY", "has:attachment filename:pdf"
        )

        # Ensure critical directories exist
        self._ensure_directories()

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve a path relative to BASE_DIR if not absolute."""
        p = Path(path_str)
        if not p.is_absolute():
            p = self.BASE_DIR / p
        return p

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [
            self.INVOICE_WATCH_DIR,
            self.PROCESSED_DIR,
            self.SAMPLES_DIR,
            self.LOGS_DIR,
            self.DB_PATH.parent,
            self.CHROMA_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()

