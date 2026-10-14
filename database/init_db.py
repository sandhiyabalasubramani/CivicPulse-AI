"""
Database Initialization & Verification Script for CivicPulse AI.
Safely connects to PostgreSQL, creates all required tables and indexes idempotently,
and verifies schema readiness. Safe to run multiple times. Never drops existing tables or data.

Usage:
    python database/init_db.py
    python database/init_db.py --url "postgresql://user:pass@host/dbname?sslmode=require"
"""

import sys
import argparse
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import (
    ensure_schema,
    check_db_status,
    normalize_database_url,
    get_raw_database_url,
    close_pool
)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Initialize CivicPulse AI PostgreSQL database schema.")
    parser.add_argument("--url", help="Custom DATABASE_URL to initialize instead of .env / environment.")
    args = parser.parse_args()

    if args.url:
        os.environ["DATABASE_URL"] = args.url

    print("==================================================")
    print("   CivicPulse AI - Database Schema Initializer    ")
    print("==================================================")

    raw_url = get_raw_database_url()
    if not raw_url:
        print("\n[ERROR] DATABASE_URL is not set.")
        print("Please configure DATABASE_URL in your .env file or provide --url.")
        print("Format: postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require\n")
        sys.exit(1)

    try:
        norm = normalize_database_url()
        host_info = norm.split("@")[-1] if "@" in norm else "local/configured"
        print(f"Target Database Host: {host_info.split('/')[0]}")
    except Exception as e:
        print(f"[WARN] URL parsing warning: {e}")

    print("\n[Step 1/2] Checking database connectivity...")
    initial_status = check_db_status()
    if not initial_status.get("connected"):
        print(f"[ERROR] Connection failed: {initial_status.get('detail')}")
        print("\nPlease verify:")
        print("1. Your database host, user, and password are correct.")
        print("2. Neon/PostgreSQL allows inbound connections.")
        print("3. sslmode=require is used for cloud-hosted databases.")
        close_pool()
        sys.exit(1)

    print("[OK] Connected successfully to PostgreSQL!")
    print(f"   Current complaints table present: {initial_status.get('tables_ready')}")
    if initial_status.get("tables_ready"):
        print(f"   Current complaint count: {initial_status.get('complaints_count')}")
        print(f"   Current status history count: {initial_status.get('status_history_count')}")

    print("\n[Step 2/2] Ensuring schema tables and indexes...")
    result = ensure_schema()
    if not result.get("success"):
        print(f"[ERROR] Schema creation failed: {result.get('message')}")
        close_pool()
        sys.exit(1)

    print("[OK] Schema verified and up to date!")
    final_status = check_db_status()
    print("\nFinal Database Status:")
    print(f" - Connected: {final_status.get('connected')}")
    print(f" - Tables ready: {final_status.get('tables_ready')}")
    print(f" - Complaints recorded: {final_status.get('complaints_count')}")
    print(f" - Status history entries: {final_status.get('status_history_count')}")
    print("\nDatabase is fully initialized and operational for CivicPulse AI.")
    close_pool()


if __name__ == "__main__":
    main()
