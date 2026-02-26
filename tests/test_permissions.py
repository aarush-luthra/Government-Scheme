import os
import uuid

from fastapi.testclient import TestClient

os.environ["APP_TEST_MODE"] = "1"

from backend.app import app  # noqa: E402
from backend import database as db  # noqa: E402


client = TestClient(app)


def _login_headers(email: str, password: str) -> dict:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("success") is True
    token = payload.get("access_token")
    assert token
    return {"Authorization": f"Bearer {token}"}


def _create_user(role: str):
    email = f"perm_{role}_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(email=email, password="password123", name=f"{role} user", role=role)
    assert user is not None
    return email


def test_user_token_cannot_access_admin_routes():
    email = _create_user("user")
    headers = _login_headers(email, "password123")

    resp = client.get("/api/v1/admin/ingestion-health", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Insufficient permissions"


def test_admin_token_can_access_admin_routes():
    email = _create_user("admin")
    headers = _login_headers(email, "password123")

    get_resp = client.get("/api/v1/admin/ingestion-health", headers=headers)
    assert get_resp.status_code == 200
    assert "rows" in get_resp.json()

    post_resp = client.post(
        "/api/v1/admin/ingestion-health",
        headers=headers,
        json={
            "source_name": "myscheme.gov.in",
            "total_schemes": 10,
            "parser_confidence": 0.91,
            "broken_links": 1,
            "pending_approvals": 0,
            "published_count": 9,
        },
    )
    assert post_resp.status_code == 200
    assert post_resp.json().get("success") is True

    analytics_resp = client.get("/api/v1/admin/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    assert "analytics" in analytics_resp.json()


def test_missing_token_denied_for_admin_routes():
    anon_client = TestClient(app)
    resp = anon_client.get("/api/v1/admin/ingestion-health")
    assert resp.status_code == 401
    assert resp.json()["detail"] in {"Not authenticated", "Invalid or expired token"}
