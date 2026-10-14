"""
PostgreSQL Database Connection & Schema Manager for CivicPulse AI.
Provides connection pooling, SSL enforcement for cloud databases (e.g. Neon),
schema migration/initialization, and safe health inspection.
"""

import os
import logging
import atexit
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import psycopg
from dotenv import load_dotenv

try:
    from psycopg_pool import ConnectionPool
    HAS_POOL = True
except ImportError:
    ConnectionPool = None
    HAS_POOL = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger("civicpulse_db")

# Global pool instance and cached URL
_pool: Optional[Any] = None
_pool_url: Optional[str] = None


def get_raw_database_url() -> Optional[str]:
    """Retrieves raw DATABASE_URL or POSTGRES_URL from environment."""
    url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    return url.strip() if url and url.strip() else None


def normalize_database_url(url: Optional[str] = None) -> str:
    """
    Normalizes a PostgreSQL connection URL:
    - Strips enclosing quotes and whitespace.
    - Converts postgres:// prefix to postgresql://.
    - Enforces sslmode=require for remote hosts (e.g. Neon, Render, RDS)
      if sslmode is not already explicitly specified.
    - Sets a default connect_timeout of 10 seconds to avoid hanging.
    """
    db_url = url or get_raw_database_url()
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL is not configured in environment variables or .env file."
        )

    clean_url = db_url.strip().strip("'\"")

    if clean_url.startswith("postgres://"):
        clean_url = "postgresql://" + clean_url[len("postgres://"):]

    try:
        conn_dict = psycopg.conninfo.conninfo_to_dict(clean_url)
    except Exception:
        # If psycopg cannot parse as URI/conninfo, return cleaned string directly
        return clean_url

    host = conn_dict.get("host", "").lower().strip()
    is_local = host in ("localhost", "127.0.0.1", "::1", "")

    # For remote cloud databases like Neon or Render, require SSL if not configured
    if not is_local:
        conn_dict.setdefault("sslmode", "require")

    # Set connection timeout if not specified
    conn_dict.setdefault("connect_timeout", "10")

    return psycopg.conninfo.make_conninfo(**conn_dict)


class ManagedConnection:
    """
    Wrapper around a psycopg Connection that returns it to the pool
    or closes it upon .close(), preventing connection leaks.
    """
    def __init__(self, conn: psycopg.Connection, pool: Optional[Any] = None):
        self._conn = conn
        self._pool = pool
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            if self._pool is not None:
                try:
                    self._pool.putconn(self._conn)
                    return
                except Exception:
                    pass
            try:
                self._conn.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def _get_or_create_pool(conninfo: str) -> Optional[Any]:
    """Initializes or retrieves the global ConnectionPool."""
    global _pool, _pool_url
    if not HAS_POOL:
        return None

    if _pool is not None and _pool_url == conninfo and not _pool.closed:
        return _pool

    try:
        if _pool is not None and not _pool.closed:
            _pool.close()
    except Exception:
        pass

    try:
        _pool = ConnectionPool(
            conninfo=conninfo,
            min_size=1,
            max_size=10,
            timeout=10.0,
            max_idle=300.0,
            check=ConnectionPool.check_connection,
            open=True
        )
        _pool_url = conninfo
        logger.info("PostgreSQL connection pool initialized (min_size=1, max_size=10)")
        return _pool
    except Exception as e:
        logger.warning("Could not initialize connection pool (%s), using direct connections.", e)
        _pool = None
        _pool_url = None
        return None


def close_pool():
    """Closes the global connection pool if open."""
    global _pool, _pool_url
    if _pool is not None:
        try:
            _pool.close()
            logger.info("PostgreSQL connection pool closed.")
        except Exception:
            pass
        _pool = None
        _pool_url = None


atexit.register(close_pool)


def get_connection() -> ManagedConnection:
    """
    Returns an active, thread-safe PostgreSQL database connection.
    Uses connection pooling when available, otherwise falls back to direct connection.
    Raises RuntimeError if DATABASE_URL is missing.
    """
    conninfo = normalize_database_url()

    pool = _get_or_create_pool(conninfo)
    if pool is not None:
        try:
            raw_conn = pool.getconn(timeout=10.0)
            return ManagedConnection(raw_conn, pool=pool)
        except Exception as e:
            logger.warning("Failed to checkout connection from pool (%s), falling back to direct connection.", e)

    # Fallback to direct connection
    raw_conn = psycopg.connect(conninfo)
    return ManagedConnection(raw_conn, pool=None)


# ============================================================
# SAFE IDEMPOTENT SCHEMA INITIALIZATION
# ============================================================

CREATE_COMPLAINTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    complaint_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    location TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    priority TEXT NOT NULL,
    priority_reason TEXT DEFAULT '',
    department TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    admin_notes TEXT DEFAULT '',
    similar_count INTEGER DEFAULT 0,
    top_similar_id TEXT DEFAULT '',
    top_similarity_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT DEFAULT NULL
);
"""

CREATE_STATUS_HISTORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    complaint_id TEXT NOT NULL,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_by TEXT DEFAULT 'System',
    comment TEXT DEFAULT '',
    changed_at TEXT NOT NULL
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_complaints_complaint_id ON complaints(complaint_id);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_location ON complaints(location);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_email ON complaints(email);",
    "CREATE INDEX IF NOT EXISTS idx_status_history_complaint_id ON status_history(complaint_id);",
    "CREATE INDEX IF NOT EXISTS idx_status_history_changed_at ON status_history(changed_at);"
]

ENSURE_COLUMNS_SQL = [
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS subcategory TEXT DEFAULT '';",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS priority_reason TEXT DEFAULT '';",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_notes TEXT DEFAULT '';",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS similar_count INTEGER DEFAULT 0;",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS top_similar_id TEXT DEFAULT '';",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS top_similarity_score REAL DEFAULT 0.0;",
    "ALTER TABLE complaints ADD COLUMN IF NOT EXISTS resolved_at TEXT DEFAULT NULL;"
]


def ensure_schema() -> Dict[str, Any]:
    """
    Safely and idempotently initializes or updates the PostgreSQL schema.
    Creates tables and indexes if they do not exist.
    Ensures required columns exist without dropping any data.
    Safe to execute multiple times against existing databases.
    """
    raw_url = get_raw_database_url()
    if not raw_url:
        logger.warning("Database schema initialization skipped: DATABASE_URL is not configured.")
        return {
            "success": False,
            "message": "DATABASE_URL is not configured."
        }

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(CREATE_COMPLAINTS_TABLE_SQL)
            cur.execute(CREATE_STATUS_HISTORY_TABLE_SQL)

            for col_query in ENSURE_COLUMNS_SQL:
                try:
                    cur.execute(col_query)
                except Exception as ex:
                    logger.debug("Column alter check note: %s", ex)

            for idx_query in CREATE_INDEXES_SQL:
                try:
                    cur.execute(idx_query)
                except Exception as ex:
                    logger.debug("Index creation note: %s", ex)

        conn.commit()
        logger.info("PostgreSQL database schema verified/initialized successfully.")
        return {
            "success": True,
            "message": "PostgreSQL database schema verified successfully."
        }
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.error("Failed to initialize database schema: %s", e, exc_info=True)
        return {
            "success": False,
            "message": f"Failed to initialize schema: {str(e)}"
        }
    finally:
        if conn:
            conn.close()


def check_db_status() -> Dict[str, Any]:
    """
    Checks PostgreSQL connectivity and returns a diagnostic status dictionary.
    Never exposes passwords, tokens, or credentials in the response.
    """
    raw_url = get_raw_database_url()
    if not raw_url:
        return {
            "configured": False,
            "connected": False,
            "tables_ready": False,
            "detail": "DATABASE_URL is not configured in environment variables."
        }

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Check for complaints and status_history tables
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN ('complaints', 'status_history')
                """
            )
            tables = [row[0] for row in cur.fetchall()]
            tables_ready = "complaints" in tables and "status_history" in tables

            complaints_count = 0
            history_count = 0

            if "complaints" in tables:
                cur.execute("SELECT COUNT(*) FROM complaints")
                complaints_count = cur.fetchone()[0]

            if "status_history" in tables:
                cur.execute("SELECT COUNT(*) FROM status_history")
                history_count = cur.fetchone()[0]

        return {
            "configured": True,
            "connected": True,
            "tables_ready": tables_ready,
            "complaints_count": complaints_count,
            "status_history_count": history_count,
            "detail": "Database connection healthy and operational."
        }
    except Exception as e:
        err_msg = str(e)
        # Sanitize error to avoid leaking credentials
        clean_err = err_msg.split("@")[-1] if "@" in err_msg else err_msg
        return {
            "configured": True,
            "connected": False,
            "tables_ready": False,
            "detail": f"Database connection failed: {clean_err}"
        }
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Checking database status...")
    status = check_db_status()
    print("Initial status:", status)
    if status.get("configured"):
        print("Ensuring schema...")
        result = ensure_schema()
        print("Schema result:", result)
        print("Updated status:", check_db_status())
    else:
        print("Please configure DATABASE_URL in .env before running schema initialization.")
    close_pool()
