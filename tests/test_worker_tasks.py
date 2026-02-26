import os
import uuid

os.environ["APP_TEST_MODE"] = "1"

from backend import database as db  # noqa: E402
from backend.worker import tasks  # noqa: E402


def _make_user_and_saved_scheme(name: str = "PM Kisan"):
    email = f"worker_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(email=email, password="password123", name="Worker User")
    assert user is not None
    db.save_scheme(user["user_id"], name)
    return user["user_id"]


def test_poll_scheme_statuses_updates_status_and_notifies(monkeypatch):
    user_id = _make_user_and_saved_scheme("PM Kisan")

    monkeypatch.setattr(tasks, "_status_from_remote", lambda _: "approved")

    result = tasks.poll_scheme_statuses(user_id=user_id)
    assert result["success"] is True
    assert result["updated"] >= 1

    rows = db.get_saved_schemes(user_id)
    assert rows[0].get("application_status") == "approved"

    events = db.get_notification_events(user_id)
    assert any("Status changed" in e.get("title", "") for e in events)


def test_process_deadline_alerts_runs_with_near_deadline(monkeypatch):
    email = f"worker_alert_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(email=email, password="password123", name="Worker Alert User")
    assert user is not None

    alert = db.add_alert_subscription(
        user_id=user["user_id"],
        scheme_name="PM Kisan",
        channel="in_app",
        contact=None,
        next_deadline="2099-01-01",
    )
    # force due window
    db.update_alert_subscription(alert["id"], next_deadline="2026-02-26")

    calls = []

    def fake_dispatch(a):
        calls.append(a["id"])
        return {"success": True}

    monkeypatch.setattr(tasks, "dispatch_alert", fake_dispatch)
    monkeypatch.setattr(tasks, "_should_dispatch_deadline", lambda _: True)

    result = tasks.process_deadline_alerts(user_id=user["user_id"])
    assert result["success"] is True
    assert len(calls) >= 1
