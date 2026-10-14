"""
Tests for Database Initialization, Cloud Connection Normalization,
Streamlit Precedence Resolution, and Health Diagnostic Endpoints.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
import psycopg

from backend.main import app
from backend.database import (
    normalize_database_url,
    get_raw_database_url,
    check_db_status,
    ensure_schema,
    ManagedConnection
)
from utils.api_client import (
    get_api_url,
    get_admin_api_key,
    get_stream_secret,
    CivicPulseApiClient,
    DEFAULT_PRODUCTION_API_URL
)


@pytest.fixture
def client():
    return TestClient(app)


# =====================================================================
# 1. DATABASE URL NORMALIZATION & CLOUD SSL ENFORCEMENT
# =====================================================================

def test_normalize_database_url_converts_postgres_prefix():
    url = "postgres://user:pass@ep-neon-123.us-east-2.aws.neon.tech/neondb"
    normalized = normalize_database_url(url)
    assert "user=user" in normalized or "postgresql://" in normalized
    assert "sslmode=require" in normalized


def test_normalize_database_url_preserves_local_without_forcing_ssl():
    url = "postgresql://postgres:postgres@localhost:5432/civicpulse"
    normalized = normalize_database_url(url)
    assert "host=localhost" in normalized
    assert "sslmode=require" not in normalized


def test_normalize_database_url_strips_quotes_and_spaces():
    url = "  'postgresql://postgres:postgres@127.0.0.1:5432/civicpulse'  "
    normalized = normalize_database_url(url)
    assert "host=127.0.0.1" in normalized


def test_normalize_database_url_raises_when_unconfigured(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    with pytest.raises(RuntimeError) as exc_info:
        normalize_database_url(None)
    assert "DATABASE_URL is not configured" in str(exc_info.value)


# =====================================================================
# 2. DATABASE STATUS CHECK & SAFE SANITIZATION
# =====================================================================

def test_check_db_status_unconfigured(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    status = check_db_status()
    assert status["configured"] is False
    assert status["connected"] is False
    assert status["tables_ready"] is False
    assert "not configured" in status["detail"].lower()


def test_check_db_status_sanitizes_error_details():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.execute.side_effect = psycopg.OperationalError("password authentication failed for user secret_pass@ep-neon.tech")

    with patch("backend.database.get_connection", side_effect=psycopg.OperationalError("password authentication failed for user user:supersecret@ep-neon.tech")):
        status = check_db_status()
        assert status["connected"] is False
        assert "supersecret" not in status["detail"]


def test_ensure_schema_skips_when_url_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    res = ensure_schema()
    assert res["success"] is False
    assert "not configured" in res["message"]


# =====================================================================
# 3. STREAMLIT CLOUD PRECEDENCE RESOLUTION
# =====================================================================

def test_get_stream_secret_safe_when_no_secrets():
    # Calling get_stream_secret should not raise StreamlitSecretNotFoundError
    val = get_stream_secret("NON_EXISTENT_KEY_XYZ")
    assert val is None


def test_get_api_url_precedence_secrets(monkeypatch):
    # Mock streamlit secrets present
    mock_streamlit = MagicMock()
    mock_streamlit.secrets = {"API_URL": "https://custom-secrets-url.render.com"}

    with patch.dict("sys.modules", {"streamlit": mock_streamlit}):
        url = get_api_url()
        assert url == "https://custom-secrets-url.render.com"


def test_get_api_url_precedence_env(monkeypatch):
    monkeypatch.setenv("API_URL", "http://127.0.0.1:9099")
    url = get_api_url()
    assert url == "http://127.0.0.1:9099"


def test_get_api_url_fallback_to_production_render(monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    with patch("utils.api_client.load_dotenv"):
        url = get_api_url()
        assert url == DEFAULT_PRODUCTION_API_URL


def test_get_admin_api_key_precedence(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "env-secret-key-123")
    key = get_admin_api_key()
    assert key == "env-secret-key-123"

    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    with patch("utils.api_client.load_dotenv"):
        assert get_admin_api_key() == ""


# =====================================================================
# 4. FASTAPI HEALTH ENDPOINT & CORS HEADERS
# =====================================================================

def test_health_endpoint_returns_db_diagnostics(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "CivicPulse AI API"
    assert "database" in data
    assert "status" in data["database"]
    assert "configured" in data["database"]


def test_cors_middleware_headers(client):
    resp = client.options(
        "/complaints/count",
        headers={
            "Origin": "https://civicpulse-ai-bqh964obd3wqrgkvsp82kk.streamlit.app",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers


def test_complaints_count_503_when_db_missing(client):
    with patch("backend.main.get_connection", side_effect=RuntimeError("DATABASE_URL is not configured")):
        resp = client.get("/complaints/count")
        assert resp.status_code == 503
        assert "Database service unavailable" in resp.json()["detail"]


def test_complaints_count_self_heals_when_table_missing(client):
    """Verifies that if UndefinedTable occurs, ensure_schema is called and query retried."""
    mock_conn1 = MagicMock()
    mock_cursor1 = MagicMock()
    mock_conn1.cursor.return_value.__enter__.return_value = mock_cursor1
    mock_cursor1.execute.side_effect = psycopg.errors.UndefinedTable("relation 'complaints' does not exist")

    mock_conn2 = MagicMock()
    mock_cursor2 = MagicMock()
    mock_conn2.cursor.return_value.__enter__.return_value = mock_cursor2
    mock_cursor2.fetchone.side_effect = [(0,), (0,)]

    with patch("backend.main.get_connection", side_effect=[mock_conn1, mock_conn2]):
        with patch("backend.main.ensure_schema", return_value={"success": True}) as mock_ensure:
            resp = client.get("/complaints/count")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["complaints"] == 0
            assert mock_ensure.called
