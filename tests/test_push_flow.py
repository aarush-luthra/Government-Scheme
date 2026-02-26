import os
import uuid

from fastapi.testclient import TestClient

os.environ["APP_TEST_MODE"] = "1"

from backend.app import app  # noqa: E402
from backend import database as db  # noqa: E402
from backend import notifications  # noqa: E402


def _auth_client():
    email = f"push_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(email=email, password="password123", name="Push User")
    assert user is not None
    session_id = db.create_session(user["user_id"], email)
    client = TestClient(app)
    client.cookies.set("session_id", session_id)
    return client, user["user_id"]


def test_push_subscribe_and_test_delivery(monkeypatch):
    client, user_id = _auth_client()

    subscribe_resp = client.post(
        "/api/v1/push/subscribe",
        json={"provider": "fcm", "fcm_token": "fcm-token-1", "user_agent": "pytest"},
    )
    assert subscribe_resp.status_code == 200
    assert subscribe_resp.json()["success"] is True

    monkeypatch.setattr(notifications, "_send_fcm", lambda token, title, body: {"success": True, "provider": "fcm", "message": "ok"})

    test_resp = client.post("/api/v1/push/test")
    assert test_resp.status_code == 200
    payload = test_resp.json()
    assert payload["success"] is True

    events = db.get_notification_events(user_id)
    assert any(e.get("channel") == "push" for e in events)
