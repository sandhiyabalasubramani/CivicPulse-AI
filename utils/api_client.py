"""
FastAPI Backend Client for CivicPulse AI.
Provides unified access to PostgreSQL grievance records, analytics, and status workflows.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger("civicpulse_client")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
DEFAULT_TIMEOUT = 10


class ApiResult:
    """
    Unified result object for API operations.
    Evaluates as a boolean for backwards compatibility, supports tuple unpacking,
    and exposes structured diagnostic details.
    """
    def __init__(
        self,
        success: bool,
        message: str = "",
        status_code: Optional[int] = None
    ):
        self.success = bool(success)
        self.message = str(message)
        self.status_code = status_code

    def __bool__(self) -> bool:
        return self.success

    def __iter__(self):
        return iter((self.success, self.message))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, bool):
            return self.success == other
        if isinstance(other, ApiResult):
            return (
                self.success == other.success
                and self.message == other.message
                and self.status_code == other.status_code
            )
        return super().__eq__(other)

    def __repr__(self) -> str:
        return f"ApiResult(success={self.success}, message='{self.message}', status_code={self.status_code})"


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
        self._admin_api_key = admin_api_key.strip() if admin_api_key is not None else None

    @property
    def admin_api_key(self) -> str:
        if self._admin_api_key is not None:
            return self._admin_api_key.strip()
        key = os.getenv("ADMIN_API_KEY")
        if not key:
            load_dotenv(PROJECT_ROOT / ".env", override=False)
            key = os.getenv("ADMIN_API_KEY", "")
        return (key or "").strip()

    @admin_api_key.setter
    def admin_api_key(self, value: Optional[str]):
        self._admin_api_key = value.strip() if value is not None else None

    @staticmethod
    def _extract_safe_error_detail(resp: requests.Response) -> str:
        """Safely extracts error details from response without exposing technical stack traces."""
        try:
            data = resp.json()
            if isinstance(data, dict):
                detail = data.get("detail", "")
                if isinstance(detail, list):
                    messages = []
                    for item in detail:
                        if isinstance(item, dict) and "msg" in item:
                            loc = item.get("loc", [])
                            field = str(loc[-1]) if loc else ""
                            msg_str = str(item["msg"])
                            messages.append(f"{field}: {msg_str}" if field else msg_str)
                    if messages:
                        return "; ".join(messages)
                elif isinstance(detail, str) and detail.strip():
                    clean = detail.strip()
                    if "traceback" in clean.lower() or "line " in clean.lower():
                        return "Internal service processing error"
                    return clean
        except Exception:
            pass
        return "Server returned an error"

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
    ) -> ApiResult:
        """
        Updates complaint status, priority, department, admin notes,
        and logs an audit trail event in PostgreSQL.
        Enforces server-side authentication using the configured admin key.
        Returns an ApiResult that functions as a boolean for backwards compatibility,
        while exposing user-friendly error messages and HTTP status codes.
        """
        cid = complaint_id.strip() if complaint_id else ""
        if not cid:
            logger.warning("Status update rejected: Empty complaint_id provided.")
            return ApiResult(False, "Complaint ID cannot be empty.", status_code=400)

        clean_status = new_status.strip() if new_status else ""
        if not clean_status:
            logger.warning("Status update rejected: Empty status provided for %s.", cid)
            return ApiResult(False, "Status cannot be empty.", status_code=400)

        payload = {
            "new_status": clean_status,
            "changed_by": (changed_by or "Admin").strip(),
            "comment": (comment or "").strip(),
            "admin_notes": admin_notes,
            "priority": priority,
            "department": department,
        }

        headers: Dict[str, str] = {}
        api_key = self.admin_api_key
        if api_key:
            headers["X-Admin-Key"] = api_key
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            logger.warning(
                "Admin API key is not configured in client environment for complaint %s.", cid
            )

        try:
            logger.info("Sending status update request for complaint %s to status '%s'", cid, clean_status)
            resp = requests.put(
                f"{self.base_url}/complaints/{cid}/status",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if resp.status_code == 200:
                logger.info("Status update succeeded for complaint %s (HTTP 200)", cid)
                return ApiResult(
                    True,
                    f"Complaint {cid} updated to {clean_status} successfully.",
                    status_code=200
                )

            # Inspect and sanitize non-200 responses
            error_detail = self._extract_safe_error_detail(resp)
            logger.warning(
                "Status update failed for complaint %s: HTTP %s - %s",
                cid, resp.status_code, error_detail
            )

            if resp.status_code == 401:
                if not api_key:
                    msg = "Admin authentication key is not configured in environment."
                else:
                    msg = "Authentication failed: Invalid administrator credentials."
                return ApiResult(False, msg, status_code=401)

            elif resp.status_code == 403:
                return ApiResult(
                    False, "Access denied: Administrator privileges required.", status_code=403
                )

            elif resp.status_code == 404:
                return ApiResult(
                    False, f"Complaint ticket '{cid}' not found in database.", status_code=404
                )

            elif resp.status_code in [400, 422]:
                return ApiResult(
                    False, f"Invalid update request: {error_detail}", status_code=resp.status_code
                )

            elif resp.status_code == 500:
                if "admin authentication is not configured" in error_detail.lower():
                    msg = "Server configuration error: Admin authentication is not configured in backend service."
                else:
                    msg = "Backend server error while updating complaint status. Please try again later."
                return ApiResult(False, msg, status_code=500)

            else:
                return ApiResult(
                    False,
                    f"Unexpected response from backend service (HTTP {resp.status_code}).",
                    status_code=resp.status_code
                )

        except requests.exceptions.Timeout:
            logger.error("Request timed out after %ss while updating complaint %s", self.timeout, cid)
            return ApiResult(
                False,
                f"Request timed out after {self.timeout}s. Backend service took too long to respond."
            )

        except requests.exceptions.ConnectionError:
            logger.error("Connection failed to backend at %s for complaint %s", self.base_url, cid)
            return ApiResult(
                False,
                f"Unable to connect to backend service ({self.base_url}). Please ensure FastAPI is running."
            )

        except requests.exceptions.RequestException as e:
            logger.error("Network error for complaint %s: %s", cid, type(e).__name__)
            return ApiResult(
                False,
                "A network error occurred while communicating with backend service."
            )


# Singleton client instance
api_client = CivicPulseApiClient()
