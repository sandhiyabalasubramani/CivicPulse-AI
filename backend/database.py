"""
PostgreSQL Database Connection for CivicPulse AI FastAPI Backend.
Provides thread-safe connections configured via DATABASE_URL.
"""

import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Returns an active PostgreSQL database connection.
    Raises RuntimeError if DATABASE_URL is not configured.
    """
    database_url = os.getenv("DATABASE_URL") or DATABASE_URL

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured in the .env file"
        )

    return psycopg.connect(database_url)
