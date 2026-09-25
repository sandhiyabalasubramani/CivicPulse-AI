"""
SQLite Database Manager for CivicPulse AI.
Provides thread-safe operations, parameterized queries, and analytics aggregation.
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from .schema import CREATE_COMPLAINTS_TABLE, CREATE_STATUS_HISTORY_TABLE, CREATE_INDEXES


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "civicpulse.db")


class DatabaseManager:
    """Manages SQLite database operations for complaints and status logs."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a database connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Initializes tables and indexes if they do not already exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_COMPLAINTS_TABLE)
            cursor.execute(CREATE_STATUS_HISTORY_TABLE)
            for idx_query in CREATE_INDEXES:
                cursor.execute(idx_query)
            conn.commit()

    def generate_complaint_id(self) -> str:
        """Generates a sequential complaint ID like CP-2026-0001."""
        current_year = datetime.now().strftime("%Y")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM complaints WHERE complaint_id LIKE ?",
                (f"CP-{current_year}-%",)
            )
            count = cursor.fetchone()["cnt"] + 1
            return f"CP-{current_year}-{count:04d}"

    def insert_complaint(self, data: Dict[str, Any]) -> str:
        """
        Inserts a new complaint using parameterized queries.
        Also creates the initial entry in status_history.
        """
        complaint_id = data.get("complaint_id") or self.generate_complaint_id()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO complaints (
                    complaint_id, name, email, location, title, description,
                    category, subcategory, priority, priority_reason, department,
                    status, admin_notes, similar_count, top_similar_id, top_similarity_score,
                    created_at, updated_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    complaint_id,
                    data.get("name", "").strip(),
                    data.get("email", "").strip().lower(),
                    data.get("location", "").strip(),
                    data.get("title", "").strip(),
                    data.get("description", "").strip(),
                    data.get("category", "Other"),
                    data.get("subcategory", "General"),
                    data.get("priority", "Medium"),
                    data.get("priority_reason", ""),
                    data.get("department", "General Administration"),
                    data.get("status", "Pending"),
                    data.get("admin_notes", ""),
                    int(data.get("similar_count", 0)),
                    data.get("top_similar_id", ""),
                    float(data.get("top_similarity_score", 0.0)),
                    data.get("created_at", now),
                    data.get("updated_at", now),
                    data.get("resolved_at", None),
                )
            )

            # Insert initial history entry
            cursor.execute(
                """
                INSERT INTO status_history (
                    complaint_id, old_status, new_status, changed_by, comment, changed_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    complaint_id,
                    "None",
                    data.get("status", "Pending"),
                    "System",
                    "Complaint submitted and automatically logged.",
                    data.get("created_at", now),
                )
            )
            conn.commit()

        return complaint_id

    def get_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single complaint record by its complaint_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id.strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_complaints_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Retrieves all complaints filed by a specific user email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM complaints WHERE email = ? ORDER BY created_at DESC",
                (email.strip().lower(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_complaints(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        search_query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieves complaints with flexible filtering as a Pandas DataFrame.
        """
        query = "SELECT * FROM complaints WHERE 1=1"
        params: List[Any] = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if priority and priority != "All":
            query += " AND priority = ?"
            params.append(priority)

        if status and status != "All":
            query += " AND status = ?"
            params.append(status)

        if location and location != "All":
            query += " AND location = ?"
            params.append(location)

        if start_date:
            query += " AND created_at >= ?"
            params.append(f"{start_date} 00:00:00")

        if end_date:
            query += " AND created_at <= ?"
            params.append(f"{end_date} 23:59:59")

        if search_query:
            query += " AND (complaint_id LIKE ? OR title LIKE ? OR description LIKE ? OR name LIKE ? OR email LIKE ? OR location LIKE ?)"
            wildcard = f"%{search_query.strip()}%"
            params.extend([wildcard, wildcard, wildcard, wildcard, wildcard, wildcard])

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df

    def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        changed_by: str = "Admin",
        comment: str = "",
        admin_notes: Optional[str] = None,
        priority: Optional[str] = None,
        department: Optional[str] = None
    ) -> bool:
        """
        Updates complaint status and adds a tracking log in status_history.
        Also handles resolution timestamp when status becomes Resolved or Closed.
        """
        current = self.get_complaint(complaint_id)
        if not current:
            return False

        old_status = current["status"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resolved_at = current["resolved_at"]

        if new_status in ["Resolved", "Closed"] and not resolved_at:
            resolved_at = now
        elif new_status not in ["Resolved", "Closed"] and old_status in ["Resolved", "Closed"]:
            resolved_at = None

        update_query = """
            UPDATE complaints
            SET status = ?, updated_at = ?, resolved_at = ?
        """
        update_params = [new_status, now, resolved_at]

        if admin_notes is not None:
            update_query += ", admin_notes = ?"
            update_params.append(admin_notes)

        if priority is not None:
            update_query += ", priority = ?"
            update_params.append(priority)

        if department is not None:
            update_query += ", department = ?"
            update_params.append(department)

        update_query += " WHERE complaint_id = ?"
        update_params.append(complaint_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, tuple(update_params))

            cursor.execute(
                """
                INSERT INTO status_history (
                    complaint_id, old_status, new_status, changed_by, comment, changed_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (complaint_id, old_status, new_status, changed_by, comment, now)
            )
            conn.commit()

        return True

    def get_status_history(self, complaint_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological timeline for a complaint."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM status_history WHERE complaint_id = ? ORDER BY changed_at ASC",
                (complaint_id.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_complaints_for_similarity(self, exclude_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns lightweight dictionary records of existing complaints for TF-IDF corpus analysis.
        """
        query = "SELECT complaint_id, title, description, category, location, priority, status, created_at FROM complaints"
        params = []
        if exclude_id:
            query += " WHERE complaint_id != ?"
            params.append(exclude_id)
        query += " ORDER BY id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_kpis(self) -> Dict[str, Any]:
        """Calculates core KPI metrics for the executive overview."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM complaints")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as cnt FROM complaints WHERE status = 'Pending'")
            pending = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) as cnt FROM complaints WHERE status = 'In Progress'")
            in_progress = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) as cnt FROM complaints WHERE status IN ('Resolved', 'Closed')")
            resolved = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) as cnt FROM complaints WHERE priority = 'High'")
            high_priority = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) as cnt FROM complaints WHERE priority = 'Critical'")
            critical_priority = cursor.fetchone()["cnt"]

            # Calculate average resolution time in hours
            cursor.execute(
                """
                SELECT created_at, resolved_at 
                FROM complaints 
                WHERE resolved_at IS NOT NULL AND status IN ('Resolved', 'Closed')
                """
            )
            resolved_rows = cursor.fetchall()
            
            avg_res_hours = 0.0
            if resolved_rows:
                durations = []
                for r in resolved_rows:
                    try:
                        c_dt = datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S")
                        r_dt = datetime.strptime(r["resolved_at"], "%Y-%m-%d %H:%M:%S")
                        diff_hours = (r_dt - c_dt).total_seconds() / 3600.0
                        if diff_hours >= 0:
                            durations.append(diff_hours)
                    except Exception:
                        pass
                if durations:
                    avg_res_hours = sum(durations) / len(durations)

            resolution_rate = (resolved / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "high_priority": high_priority,
            "critical_priority": critical_priority,
            "resolution_rate": round(resolution_rate, 1),
            "avg_resolution_hours": round(avg_res_hours, 1)
        }

    def get_distinct_values(self, column: str) -> List[str]:
        """Returns distinct non-empty values for a given column."""
        valid_columns = ["category", "priority", "status", "location", "department"]
        if column not in valid_columns:
            return []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT {column} FROM complaints WHERE {column} IS NOT NULL AND {column} != '' ORDER BY {column} ASC")
            return [row[column] for row in cursor.fetchall()]

    def reset_db(self) -> None:
        """Clears all records from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM status_history;")
            cursor.execute("DELETE FROM complaints;")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints', 'status_history');")
            conn.commit()


# Singleton database instance helper
_db_instance: Optional[DatabaseManager] = None

def get_db() -> DatabaseManager:
    """Provides a global singleton instance of DatabaseManager."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
