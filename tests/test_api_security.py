"""
Security and Production-Readiness Tests for CivicPulse AI API.
Verifies:
1. Strict email validation on ComplaintRequest and API rejection of invalid emails.
2. Server-side enforcement of admin authentication on status updates.
3. Fail-closed security: missing/empty ADMIN_API_KEY disables updates and rejects any secret.
4. Safe generic API error responses without sensitive technical trace leakage.
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.main import app, ComplaintRequest


@pytest.fixture
def api_client():
    """Provides a TestClient for backend FastAPI integration testing."""
    return TestClient(app)


@pytest.fixture
def test_admin_key(monkeypatch):
    """
    Configures a temporary test-only secret without introducing
    any production fallback secrets. Automatically restored after test.
    """
    key = "temporary-isolated-test-admin-secret-771122"
    monkeypatch.setenv("ADMIN_API_KEY", key)
    return key


# =====================================================================
# 1. EMAIL VALIDATION TESTS
# =====================================================================

@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "missing-at-sign.com",
    "@domain.com",
    "user@",
    "user@nodomain",
    "",
    "   ",
    "user name@domain.com",
    "user@.com",
])
def test_complaint_request_model_rejects_invalid_email(invalid_email):
    """Verifies that the real ComplaintRequest model strictly rejects invalid emails."""
    with pytest.raises(ValidationError):
        ComplaintRequest(
            name="John Doe",
            email=invalid_email,
            location="Main Hall",
            title="Broken projector in hall",
            description="The projector bulb is blown and cannot display images.",
            category="Auto-Detect",
            department="Auto-Assign"
        )


@pytest.mark.parametrize("valid_email, expected_email", [
    ("student@institution.edu", "student@institution.edu"),
    ("  User@Example.COM  ", "user@example.com"),
    ("admin.support+ticket@campus.gov", "admin.support+ticket@campus.gov"),
])
def test_complaint_request_model_accepts_and_normalizes_valid_email(valid_email, expected_email):
    """Verifies that ComplaintRequest accepts and lowercases/strips valid emails."""
    req = ComplaintRequest(
        name="Valid Complainant",
        email=valid_email,
        location="Hostel Block A",
        title="Water dispenser leaking",
        description="Water is pooling on floor 2 near the water cooler dispenser.",
        category="Auto-Detect",
        department="Auto-Assign"
    )
    assert req.email == expected_email


def test_api_rejects_invalid_email_on_analyze(api_client):
    """Verifies that POST /analyze rejects invalid email input with HTTP 422."""
    payload = {
        "name": "Alex Smith",
        "email": "invalid-email-format",
        "location": "Library 2F",
        "title": "Air conditioner making loud noise",
        "description": "AC unit in reading room makes continuous buzzing noise.",
        "category": "Auto-Detect",
        "department": "Auto-Assign"
    }
    response = api_client.post("/analyze", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_api_rejects_invalid_email_on_create(api_client):
    """Verifies that POST /complaints rejects invalid email input with HTTP 422."""
    payload = {
        "name": "Alex Smith",
        "email": "invalid-email-address",
        "location": "Library 2F",
        "title": "Air conditioner making loud noise",
        "description": "AC unit in reading room makes continuous buzzing noise.",
        "category": "Auto-Detect",
        "department": "Auto-Assign"
    }
    response = api_client.post("/complaints", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


# =====================================================================
# 2. ADMIN AUTHENTICATION TESTS (FAIL-CLOSED & HEADER ENFORCEMENT)
# =====================================================================

def test_unauthenticated_status_update_rejected(api_client):
    """
    Verifies that unauthenticated users cannot update complaint status
    through PUT /complaints/{complaint_id}/status. Must return HTTP 401.
    """
    payload = {
        "new_status": "Closed",
        "changed_by": "Anonymous Attacker",
        "comment": "Unauthorized status tamper attempt"
    }
    response = api_client.put("/complaints/CP-TEST1234/status", json=payload)
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]


def test_missing_admin_key_fails_closed_rejects_known_secret(api_client, monkeypatch):
    """
    Verifies that when ADMIN_API_KEY is not configured (missing from env),
    the server fails closed and rejects attempts to authenticate using
    any previous fallback secret (e.g. 'civicpulse-admin-secret-2026').
    """
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    payload = {
        "new_status": "Closed",
        "changed_by": "Attacker",
        "comment": "Probing for fallback default secret"
    }
    # Test via X-Admin-Key with known old secret
    response = api_client.put(
        "/complaints/CP-TEST1234/status",
        json=payload,
        headers={"X-Admin-Key": "civicpulse-admin-secret-2026"}
    )
    assert response.status_code == 500
    assert "Server configuration error" in response.json()["detail"]

    # Test via Bearer token with known old secret
    response_bearer = api_client.put(
        "/complaints/CP-TEST1234/status",
        json=payload,
        headers={"Authorization": "Bearer civicpulse-admin-secret-2026"}
    )
    assert response_bearer.status_code == 500
    assert "Server configuration error" in response_bearer.json()["detail"]


def test_empty_admin_key_fails_closed(api_client, monkeypatch):
    """
    Verifies that when ADMIN_API_KEY is an empty string or whitespace,
    the server fails closed with HTTP 500 and rejects all status updates.
    """
    for empty_val in ["", "   "]:
        monkeypatch.setenv("ADMIN_API_KEY", empty_val)
        payload = {
            "new_status": "Closed",
            "changed_by": "Attacker",
            "comment": "Probing empty secret"
        }
        response = api_client.put(
            "/complaints/CP-TEST1234/status",
            json=payload,
            headers={"X-Admin-Key": "civicpulse-admin-secret-2026"}
        )
        assert response.status_code == 500
        assert "Server configuration error" in response.json()["detail"]


def test_invalid_token_status_update_rejected(api_client, test_admin_key):
    """
    Verifies that requests with incorrect admin tokens are rejected with HTTP 401.
    """
    payload = {
        "new_status": "In Progress",
        "changed_by": "Fake Admin",
        "comment": "Testing invalid token rejection"
    }
    # Test via X-Admin-Key header
    resp_header = api_client.put(
        "/complaints/CP-TEST1234/status",
        json=payload,
        headers={"X-Admin-Key": "completely-wrong-token"}
    )
    assert resp_header.status_code == 401
    assert "Invalid admin credentials" in resp_header.json()["detail"]

    # Test via Authorization Bearer header
    resp_bearer = api_client.put(
        "/complaints/CP-TEST1234/status",
        json=payload,
        headers={"Authorization": "Bearer completely-wrong-token"}
    )
    assert resp_bearer.status_code == 401
    assert "Invalid admin credentials" in resp_bearer.json()["detail"]

    # Test that previous fallback secret is rejected when a valid key is configured
    resp_old_secret = api_client.put(
        "/complaints/CP-TEST1234/status",
        json=payload,
        headers={"X-Admin-Key": "civicpulse-admin-secret-2026"}
    )
    assert resp_old_secret.status_code == 401
    assert "Invalid admin credentials" in resp_old_secret.json()["detail"]


def test_authorized_status_update_passes_authentication(api_client, test_admin_key):
    """
    Verifies that requests with the valid admin key pass authentication.
    Even if the complaint does not exist, it must return 404 (not 401 or 500).
    """
    payload = {
        "new_status": "In Progress",
        "changed_by": "Real Admin",
        "comment": "Authorized update check"
    }
    # Test via X-Admin-Key
    response_x_key = api_client.put(
        "/complaints/CP-NONEXISTENT/status",
        json=payload,
        headers={"X-Admin-Key": test_admin_key}
    )
    assert response_x_key.status_code in [200, 404]

    # Test via Authorization Bearer
    response_bearer = api_client.put(
        "/complaints/CP-NONEXISTENT/status",
        json=payload,
        headers={"Authorization": f"Bearer {test_admin_key}"}
    )
    assert response_bearer.status_code in [200, 404]

    # Test via X-API-Key
    response_api_key = api_client.put(
        "/complaints/CP-NONEXISTENT/status",
        json=payload,
        headers={"X-API-Key": test_admin_key}
    )
    assert response_api_key.status_code in [200, 404]


# =====================================================================
# 3. SAFE ERROR RESPONSES TESTS
# =====================================================================

def test_safe_error_response_no_stack_trace_leakage(api_client):
    """
    Verifies that distinct column endpoint rejects invalid column
    safely without leaking technical traces or SQL errors.
    """
    response = api_client.get("/complaints/distinct/unrecognized_table_col")
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "traceback" not in detail.lower()
    assert "syntax error" not in detail.lower()
