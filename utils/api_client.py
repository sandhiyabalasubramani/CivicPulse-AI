"""
FastAPI Backend Client for CivicPulse AI.
Provides unified access to PostgreSQL grievance records, analytics, and status workflows.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
DEFAULT_TIMEOUT = 10


class CivicPulseApiClient:
    """Client for communicating with the FastAPI PostgreSQL backend."""

    def __init__(
        self,
        base_url: str = API_URL,
        timeout: int = DEFAULT_TIMEOUT,
        admin_api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        resolved_key = (
            admin_api_key
            if admin_api_key is not None
            else os.getenv("ADMIN_API_KEY", ADMIN_API_KEY)
        )
        self.admin_api_key = resolved_key.strip() if resolved_key else ""

    def check_health(self) -> bool:
        """Check if the FastAPI backend service is healthy."""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def get_complaint(
        self, complaint_id: str
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Retrieves a single complaint and its chronological status history.
        Returns (complaint_dict, history_list).
        """
        cid = complaint_id.strip()
        resp = requests.get(f"{self.base_url}/complaints/{cid}", timeout=self.timeout)
        if resp.status_code == 200:
            data = resp.json()
            complaint = data.get("complaint", data)
            history = data.get("history", [])
            return complaint, history
        elif resp.status_code == 404:
            return None, []
        else:
            resp.raise_for_status()
            return None, []

    def get_complaints_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Retrieves all complaints filed under a registered email address."""
        clean_email = email.strip()
        if not clean_email:
            return []
        resp = requests.get(
            f"{self.base_url}/complaints/by-email/{clean_email}",
            timeout=self.timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("complaints", [])
        else:
            resp.raise_for_status()
            return []

    def get_all_complaints(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        search_query: Optional[str] = None,
        email: Optional[str] = None,
        limit: Optional[int] = 1000,
    ) -> pd.DataFrame:
        """
        Retrieves filtered complaints as a Pandas DataFrame for Admin, Analytics, and Reports.
        """
        params: Dict[str, Any] = {}
        if category and category != "All":
            params["category"] = category
        if priority and priority != "All":
            params["priority"] = priority
        if status and status != "All":
            params["status"] = status
        if location and location != "All":
            params["location"] = location
        if department and department != "All":
            params["department"] = department
        if search_query and search_query.strip():
            params["search_query"] = search_query.strip()
        if email and email.strip():
            params["email"] = email.strip()
        if limit:
            params["limit"] = limit

        resp = requests.get(
            f"{self.base_url}/complaints",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            complaints = data.get("complaints", [])
            if not complaints:
                return pd.DataFrame()
            return pd.DataFrame(complaints)
        else:
            resp.raise_for_status()
            return pd.DataFrame()

    def get_kpis(self) -> Dict[str, Any]:
        """Retrieves aggregated KPI metrics computed from PostgreSQL."""
        resp = requests.get(f"{self.base_url}/complaints/kpis", timeout=self.timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("kpis", {})
        else:
            resp.raise_for_status()
            return {}

    def get_distinct_values(self, column: str) -> List[str]:
        """Retrieves distinct non-empty values for a given column from PostgreSQL."""
        resp = requests.get(
            f"{self.base_url}/complaints/distinct/{column.strip()}",
            timeout=self.timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("values", [])
        else:
            resp.raise_for_status()
            return []

    def get_status_history(self, complaint_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological status timeline for a complaint."""
        complaint, history = self.get_complaint(complaint_id)
        return history

    def get_all_status_history(self, limit: int = 5000) -> pd.DataFrame:
        """Retrieves complete audit trail log across all complaints as a DataFrame."""
        try:
            resp = requests.get(
                f"{self.base_url}/status-history",
                params={"limit": limit},
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                history = data.get("history", [])
                if not history:
                    return pd.DataFrame()
                return pd.DataFrame(history)
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        changed_by: str = "Admin",
        comment: str = "",
        admin_notes: Optional[str] = None,
        priority: Optional[str] = None,
        department: Optional[str] = None,
    ) -> bool:
        """
        Updates complaint status, priority, department, admin notes,
        and logs an audit trail event in PostgreSQL.
        Enforces server-side authentication using the configured admin key.
        """
        cid = complaint_id.strip()
        payload = {
            "new_status": new_status,
            "changed_by": changed_by,
            "comment": comment,
            "admin_notes": admin_notes,
            "priority": priority,
            "department": department,
        }
        headers = {}
        if self.admin_api_key:
            headers["X-Admin-Key"] = self.admin_api_key
            headers["Authorization"] = f"Bearer {self.admin_api_key}"

        resp = requests.put(
            f"{self.base_url}/complaints/{cid}/status",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        return resp.status_code == 200


# Singleton client instance
api_client = CivicPulseApiClient()
