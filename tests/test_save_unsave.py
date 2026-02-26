import os
import uuid
from fastapi.testclient import TestClient

os.environ["APP_TEST_MODE"] = "1"

from backend.app import app  # noqa: E402
from backend import database as db  # noqa: E402


def _auth_client():
    email = f"save_test_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(email=email, password="password123", name="Saver")
    assert user is not None
    session_id = db.create_session(user["user_id"], email)
    client = TestClient(app)
    client.cookies.set("session_id", session_id)
    return client


def test_save_unsave_scheme_round_trip():
    client = _auth_client()

    save_resp = client.post("/api/v1/saved-schemes", json={"scheme_name": "PM Kisan"})
    assert save_resp.status_code == 200
    saved = save_resp.json()["saved_schemes"]
    assert any(item["scheme_name"] == "PM Kisan" for item in saved)

    delete_resp = client.delete("/api/v1/saved-schemes/PM%20Kisan")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["success"] is True
    assert all(item["scheme_name"] != "PM Kisan" for item in delete_resp.json()["saved_schemes"])


def test_save_scheme_is_per_user_isolated():
    client_a = _auth_client()
    client_b = _auth_client()

    client_a.post("/api/v1/saved-schemes", json={"scheme_name": "Atal Pension Yojana"})

    dashboard_a = client_a.get("/api/v1/saved-dashboard")
    dashboard_b = client_b.get("/api/v1/saved-dashboard")

    assert dashboard_a.status_code == 200
    assert dashboard_b.status_code == 200

    saved_a = dashboard_a.json()["saved_schemes"]
    saved_b = dashboard_b.json()["saved_schemes"]

    assert any(item["scheme_name"] == "Atal Pension Yojana" for item in saved_a)
    assert all(item["scheme_name"] != "Atal Pension Yojana" for item in saved_b)
