import sqlite3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import normalize_database_url

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

# Connect to SQLite
sqlite_path = PROJECT_ROOT / "civicpulse.db"
sqlite_conn = sqlite3.connect(str(sqlite_path))
sqlite_cur = sqlite_conn.cursor()

# Connect to PostgreSQL with cloud SSL normalization
pg_conn = psycopg.connect(normalize_database_url(DATABASE_URL))
pg_cur = pg_conn.cursor()

try:
    # -----------------------------
    # Migrate complaints
    # -----------------------------
    sqlite_cur.execute("""
        SELECT
            id,
            complaint_id,
            name,
            email,
            location,
            title,
            description,
            category,
            subcategory,
            priority,
            priority_reason,
            department,
            status,
            admin_notes,
            similar_count,
            top_similar_id,
            top_similarity_score,
            created_at,
            updated_at,
            resolved_at
        FROM complaints
        ORDER BY id
    """)

    complaints = sqlite_cur.fetchall()

    for row in complaints:
        pg_cur.execute("""
            INSERT INTO complaints (
                id,
                complaint_id,
                name,
                email,
                location,
                title,
                description,
                category,
                subcategory,
                priority,
                priority_reason,
                department,
                status,
                admin_notes,
                similar_count,
                top_similar_id,
                top_similarity_score,
                created_at,
                updated_at,
                resolved_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (complaint_id) DO NOTHING
        """, row)

    # -----------------------------
    # Migrate status history
    # -----------------------------
    sqlite_cur.execute("""
        SELECT
            id,
            complaint_id,
            old_status,
            new_status,
            changed_by,
            comment,
            changed_at
        FROM status_history
        ORDER BY id
    """)

    history = sqlite_cur.fetchall()

    for row in history:
        pg_cur.execute("""
            INSERT INTO status_history (
                id,
                complaint_id,
                old_status,
                new_status,
                changed_by,
                comment,
                changed_at
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT DO NOTHING
        """, row)

    pg_conn.commit()

    print(f"Complaints migrated: {len(complaints)}")
    print(f"Status history migrated: {len(history)}")
    print("Migration completed successfully")

except Exception as e:
    pg_conn.rollback()
    print("Migration failed:", e)
    raise

finally:
    sqlite_cur.close()
    sqlite_conn.close()
    pg_cur.close()
    pg_conn.close()