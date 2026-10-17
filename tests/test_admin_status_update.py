"""
Tests for Admin Complaint Status Update Workflow, Endpoint Security,
Transaction Rollback, Client Error Handling, and Streamlit View Rendering.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
import requests

from backend.main import app, StatusUpdateRequest, SUPPORTED_STATUSES
from utils.api_client import CivicPulseApiClient, ApiResult


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def isolated_admin_key(monkeypatch):
    """Provides a temporary, isolated admin key in environment."""
    key = "isolated-test-admin-key-abc123xyz"
    monkeypatch.setenv("ADMIN_API_KEY", key)
    return key


# =====================================================================
# 1. ENVIRONMENT CONFIGURATION & MASKED LOADING TESTS
# =====================================================================

def test_admin_api_key_loaded_and_masked(monkeypatch):
    """
    Verifies ADMIN_API_KEY is loaded properly from environment
    and can be retrieved without printing/exposing secret.
    """
    secret = "super-secret-key-999"
    monkeypatch.setenv("ADMIN_API_KEY", secret)

    api_cli = CivicPulseApiClient(admin_api_key=None)
    loaded_key = api_cli.admin_api_key

    assert loaded_key == secret
    assert len(loaded_key) > 0
    # Ensure string representation does not leak key
    assert secret not in repr(api_cli)


# =====================================================================
# 2. STATUS UPDATE REQUEST MODEL VALIDATION TESTS
# =====================================================================

@pytest.mark.parametrize("valid_status", [
    "Pending", "Assigned", "In Progress", "Resolved", "Closed",
    "pending", "IN PROGRESS", "  resolved  "
])
def test_status_update_model_accepts_valid_statuses(valid_status):
    """Verifies that StatusUpdateRequest accepts and normalizes supported statuses."""
    req = StatusUpdateRequest(new_status=valid_status)
    assert req.new_status in SUPPORTED_STATUSES


@pytest.mark.parametrize("invalid_status", [
    "Unknown", "Cancelled", "Deleted", "InvalidStatus", "", "   "
])
def test_status_update_model_rejects_invalid_statuses(invalid_status):
    """Verifies that StatusUpdateRequest rejects unsupported statuses."""
    with pytest.raises(Exception):
        StatusUpdateRequest(new_status=invalid_status)


def test_status_update_model_priority_validation():
    """Verifies priority validation on StatusUpdateRequest."""
    req_valid = StatusUpdateRequest(new_status="In Progress", priority="High")
    assert req_valid.priority == "High"

    with pytest.raises(Exception):
        StatusUpdateRequest(new_status="In Progress", priority="NonExistentPriority")


# =====================================================================
# 3. BACKEND ENDPOINT: TRANSACTION & ROLLBACK TESTS (MOCKED DB)
# =====================================================================

def test_endpoint_empty_complaint_id_rejected(client, isolated_admin_key):
    """Verifies that whitespace complaint IDs are rejected with HTTP 400 or 404."""
    resp = client.put(
        "/complaints/%20/status",
        json={"new_status": "In Progress"},
        headers={"X-Admin-Key": isolated_admin_key}
    )
    assert resp.status_code in [400, 404]


def test_endpoint_invalid_status_rejected_with_422(client, isolated_admin_key):
    """Verifies that invalid new_status is rejected with HTTP 422 before touching DB."""
    resp = client.put(
        "/complaints/CP-TEST001/status",
        json={"new_status": "InvalidStatus"},
        headers={"X-Admin-Key": isolated_admin_key}
    )
    assert resp.status_code == 422


def test_endpoint_successful_status_update_and_history_insertion(client, isolated_admin_key):
    """
    Verifies that a successful update:
    1. Updates complaint record.
    2. Inserts exactly one status_history record.
    3. Commits transaction and closes connection.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Simulate existing complaint found: status="Pending", resolved_at=None
    mock_cursor.fetchone.return_value = ("Pending", None)

    with patch("backend.main.get_connection", return_value=mock_conn):
        resp = client.put(
            "/complaints/CP-MOCK1234/status",
            json={
                "new_status": "In Progress",
                "changed_by": "Test Handler",
                "comment": "Dispatched technician",
                "admin_notes": "Priority confirmed",
                "priority": "High",
                "department": "Electrical Maintenance Division"
            },
            headers={"X-Admin-Key": isolated_admin_key}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

        # Verify cursor execute calls
        execute_calls = mock_cursor.execute.call_args_list
        assert len(execute_calls) == 3

        # 1. SELECT query
        assert "SELECT status, resolved_at FROM complaints" in execute_calls[0][0][0]

        # 2. UPDATE query
        assert "UPDATE complaints" in execute_calls[1][0][0]
        update_params = execute_calls[1][0][1]
        assert update_params[0] == "In Progress"
        assert "CP-MOCK1234" in update_params

        # 3. INSERT status_history query (exactly once)
        assert "INSERT INTO status_history" in execute_calls[2][0][0]
        history_params = execute_calls[2][0][1]
        assert history_params[0] == "CP-MOCK1234"  # complaint_id
        assert history_params[1] == "Pending"      # old_status
        assert history_params[2] == "In Progress"  # new_status
        assert history_params[3] == "Test Handler" # changed_by
        assert history_params[4] == "Dispatched technician" # comment

        # Verify commit was called
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_conn.close.assert_called_once()


def test_endpoint_transaction_rollback_when_history_insert_fails(client, isolated_admin_key):
    """
    Verifies rollback behavior when status_history insertion raises an error:
    1. Transaction is rolled back.
    2. Commit is NOT called.
    3. Connection is closed.
    4. HTTP 500 returned with safe error detail.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchone.return_value = ("Pending", None)

    # Make second query (INSERT status_history) raise DatabaseError
    def side_effect(query, params=None):
        if "INSERT INTO status_history" in query:
            raise RuntimeError("Simulated status_history disk write error")
        return None

    mock_cursor.execute.side_effect = side_effect

    with patch("backend.main.get_connection", return_value=mock_conn):
        resp = client.put(
            "/complaints/CP-MOCK1234/status",
            json={
                "new_status": "In Progress",
                "changed_by": "Test Handler",
                "comment": "Testing rollback"
            },
            headers={"X-Admin-Key": isolated_admin_key}
        )

        assert resp.status_code == 500
        detail = resp.json().get("detail", "")
        assert "Simulated status_history" not in detail
        assert "internal error occurred" in detail.lower()

        # Verify rollback was called and commit was NOT called
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_conn.close.assert_called_once()


# =====================================================================
# 4. API CLIENT ERROR HANDLING & DIAGNOSTIC RESULT TESTS
# =====================================================================

def test_api_result_boolean_and_unpacking_compatibility():
    """Verifies that ApiResult satisfies boolean, equality, and unpacking semantics."""
    res_success = ApiResult(True, "All good", status_code=200)
    assert bool(res_success) is True
    assert res_success == True
    assert res_success.message == "All good"

    # Test tuple unpacking
    success, msg = res_success
    assert success is True
    assert msg == "All good"

    res_fail = ApiResult(False, "Failed to connect", status_code=503)
    assert bool(res_fail) is False
    assert res_fail == False
    assert res_fail.message == "Failed to connect"

    success_f, msg_f = res_fail
    assert success_f is False
    assert msg_f == "Failed to connect"


def test_api_client_update_status_handles_timeout():
    """Verifies api_client handles requests.exceptions.Timeout gracefully."""
    api_cli = CivicPulseApiClient(admin_api_key="valid-key")

    with patch("requests.put", side_effect=requests.exceptions.Timeout("Connection timed out")):
        res = api_cli.update_complaint_status("CP-TEST1", "In Progress")
        assert bool(res) is False
        assert "timed out" in res.message.lower()


def test_api_client_update_status_handles_connection_error():
    """Verifies api_client handles requests.exceptions.ConnectionError gracefully."""
    api_cli = CivicPulseApiClient(admin_api_key="valid-key")

    with patch("requests.put", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        res = api_cli.update_complaint_status("CP-TEST1", "In Progress")
        assert bool(res) is False
        assert "unable to connect" in res.message.lower()


def test_api_client_update_status_handles_401_auth_failure():
    """Verifies api_client provides informative message for HTTP 401."""
    api_cli = CivicPulseApiClient(admin_api_key="wrong-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.json.return_value = {"detail": "Unauthorized: Invalid admin credentials."}

    with patch("requests.put", return_value=mock_resp):
        res = api_cli.update_complaint_status("CP-TEST1", "In Progress")
        assert bool(res) is False
        assert "authentication failed" in res.message.lower()
        assert res.status_code == 401


def test_api_client_update_status_handles_500_backend_misconfigured():
    """Verifies api_client provides informative message when backend admin key is not configured."""
    api_cli = CivicPulseApiClient(admin_api_key="some-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.json.return_value = {
        "detail": "Server configuration error: Admin authentication is not configured. Status updates are disabled."
    }

    with patch("requests.put", return_value=mock_resp):
        res = api_cli.update_complaint_status("CP-TEST1", "In Progress")
        assert bool(res) is False
        assert "server configuration error" in res.message.lower()
        assert res.status_code == 500


# =====================================================================
# 5. STREAMLIT VIEWS RENDERING TESTS (SAFE, NON-DESTRUCTIVE)
# =====================================================================

def test_all_five_streamlit_views_render_without_exception():
    """
    Confirms all five Streamlit pages render cleanly without throwing exceptions.
    Uses mocked backend calls to ensure zero database alteration.
    """
    from contextlib import ExitStack
    import pandas as pd

    from views.submit_view import render_submit_view
    from views.tracker_view import render_tracker_view
    from views.admin_view import render_admin_view
    from views.analytics_view import render_analytics_view
    from views.reports_view import render_reports_view

    def mock_columns(spec, *args, **kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [MagicMock() for _ in range(count)]

    st_patches = [
        ("streamlit.sidebar", MagicMock()),
        ("streamlit.columns", MagicMock(side_effect=mock_columns)),
        ("streamlit.expander", MagicMock()),
        ("streamlit.markdown", MagicMock()),
        ("streamlit.write", MagicMock()),
        ("streamlit.dataframe", MagicMock()),
        ("streamlit.selectbox", MagicMock(return_value="Pending")),
        ("streamlit.text_input", MagicMock(return_value="")),
        ("streamlit.text_area", MagicMock(return_value="")),
        ("streamlit.form_submit_button", MagicMock(return_value=False)),
        ("streamlit.button", MagicMock(return_value=False)),
        ("streamlit.form", MagicMock()),
        ("streamlit.error", MagicMock()),
        ("streamlit.success", MagicMock()),
        ("streamlit.info", MagicMock()),
        ("streamlit.warning", MagicMock()),
        ("streamlit.subheader", MagicMock()),
        ("streamlit.caption", MagicMock()),
        ("streamlit.divider", MagicMock()),
        ("utils.api_client.api_client.check_health", MagicMock(return_value=True)),
        ("utils.api_client.api_client.get_kpis", MagicMock(return_value={
            "total": 5, "pending": 2, "in_progress": 1, "resolved": 2,
            "high_priority": 1, "critical_priority": 1, "resolution_rate": 40.0
        })),
        ("utils.api_client.api_client.get_all_complaints", MagicMock(return_value=pd.DataFrame([{
            "id": 1, "complaint_id": "CP-SAMPLE01", "name": "Jane", "email": "jane@test.edu",
            "location": "Library", "title": "Desk broken", "description": "Leg cracked",
            "category": "Infrastructure & Civil", "subcategory": "Furniture",
            "priority": "Low", "priority_reason": "Cosmetic", "department": "Civil Works",
            "status": "Pending", "admin_notes": "", "similar_count": 0, "top_similar_id": None,
            "top_similarity_score": 0.0, "created_at": "2026-10-12 10:00:00",
            "updated_at": "2026-10-12 10:00:00", "resolved_at": None
        }]))),
        ("utils.api_client.api_client.get_complaint", MagicMock(return_value=({
            "id": 1, "complaint_id": "CP-SAMPLE01", "name": "Jane", "email": "jane@test.edu",
            "location": "Library", "title": "Desk broken", "description": "Leg cracked",
            "category": "Infrastructure & Civil", "subcategory": "Furniture",
            "priority": "Low", "priority_reason": "Cosmetic", "department": "Civil Works",
            "status": "Pending", "admin_notes": "", "similar_count": 0, "top_similar_id": None,
            "top_similarity_score": 0.0, "created_at": "2026-10-12 10:00:00",
            "updated_at": "2026-10-12 10:00:00", "resolved_at": None
        }, []))),
        ("utils.api_client.api_client.get_all_status_history", MagicMock(return_value=pd.DataFrame())),
    ]

    with ExitStack() as stack:
        for target, mock_obj in st_patches:
            stack.enter_context(patch(target, mock_obj))

        # 1. Submit View
        render_submit_view()

        # 2. Tracker View
        render_tracker_view()

        # 3. Admin View
        render_admin_view()

        # 4. Analytics View
        render_analytics_view()

        # 5. Reports View
        render_reports_view()


def test_get_complaint_case_insensitive_and_whitespace_endpoint(client):
    """
    Verifies that GET /complaints/{complaint_id} handles leading/trailing whitespace
    and case-insensitivity gracefully without throwing 404.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_row = (
        1, "CP-2026-0001", "User", "user@test.edu", "Room 101", "AC leak",
        "Water leaking", "Electrical", "HVAC", "High", "Leak", "Maintenance",
        "Pending", "", 0, "", 0.0, "2026-10-12 10:00:00", "2026-10-12 10:00:00", None
    )
    mock_cursor.fetchone.return_value = mock_row
    mock_cursor.fetchall.return_value = [("None", "Pending", "System", "Logged", "2026-10-12 10:00:00")]

    with patch("backend.main.get_connection", return_value=mock_conn):
        resp = client.get("/complaints/  cp-2026-0001  ")
        assert resp.status_code == 200
        data = resp.json()
        assert data["complaint"]["complaint_id"] == "CP-2026-0001"
        assert len(data["history"]) == 1


def test_update_status_case_insensitive_endpoint(client, isolated_admin_key):
    """
    Verifies that PUT /complaints/{complaint_id}/status accepts lowercase ticket IDs
    and matches them case-insensitively.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ("Pending", None)

    with patch("backend.main.get_connection", return_value=mock_conn):
        resp = client.put(
            "/complaints/cp-2026-0001/status",
            json={"new_status": "Resolved", "changed_by": "Admin"},
            headers={"X-Admin-Key": isolated_admin_key}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
