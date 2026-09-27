import sqlite3
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

# Connect to SQLite
sqlite_conn = sqlite3.connect("civicpulse.db")
sqlite_cur = sqlite_conn.cursor()

# Connect to PostgreSQL
pg_conn = psycopg.connect(DATABASE_URL)
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