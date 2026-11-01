"""
Seed Demo Data Script for Smart Invoice Processor.
Populates SQLite database with 12 baseline invoices, 12 duplicate records (for review testing),
and European Central Bank exchange rates for multi-currency conversion.
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from core.database import DatabaseManager


def seed_database(db_path: Optional[Path] = None) -> bool:
    """
    Seeds the SQLite database with demonstration invoices and exchange rate cache.
    Initializes schema tables if not present, then loads seed records with explicit column mapping.
    Safe to run idempotently.
    """
    target_path = Path(db_path) if db_path else settings.DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Initialize schema via DatabaseManager to ensure all tables & migrations exist
    manager = DatabaseManager(db_path=target_path)
    manager.init_db()

    # 2. Check if already seeded with at least 24 invoices
    counts = manager.get_invoice_counts()
    if counts.get("total", 0) >= 24:
        return True

    # 3. Read seed SQL
    seed_sql_file = PROJECT_ROOT / "scripts" / "seed_data.sql"
    if not seed_sql_file.exists():
        raise FileNotFoundError(f"Seed SQL script not found at {seed_sql_file}")

    with open(seed_sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # 4. Execute seed SQL
    conn = sqlite3.connect(str(target_path))
    try:
        conn.executescript(sql_content)
        conn.commit()

        # Validate count
        new_counts = manager.get_invoice_counts()
        return new_counts.get("total", 0) >= 24
    finally:
        conn.close()


if __name__ == "__main__":
    success = seed_database()
    if success:
        print(f"Successfully seeded database at '{settings.DB_PATH}'.")
    else:
        print(f"Failed to seed database at '{settings.DB_PATH}'.", file=sys.stderr)
        sys.exit(1)
