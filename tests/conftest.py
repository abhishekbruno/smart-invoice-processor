"""
Pytest configuration and session-wide fixtures for Smart Invoice Processor.
"""

import os
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from scripts.seed_demo_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def ensure_database_seeded():
    """
    Session-wide fixture ensuring the database at settings.DB_PATH is populated
    with the required demonstration invoice records, line items, and exchange rates.
    This guarantees that tests pass reliably in clean CI/CD environments where .db
    files are intentionally excluded from version control.
    """
    from core.database import db

    counts = db.get_invoice_counts()
    if counts.get("total", 0) < 24:
        seed_database(db.db_path)

