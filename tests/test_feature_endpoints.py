import os
import uuid
from fastapi.testclient import TestClient

os.environ["APP_TEST_MODE"] = "1"
os.environ["ADMIN_DISPATCH_TOKEN"] = "test-admin-token"

from backend.app import app  # noqa: E402
from backend import database as db  # noqa: E402


client = TestClient(app)


def _auth_client():
    email = f"feature_test_{uuid.uuid4().hex[:10]}@example.com"
    user = db.create_user(
        email=email,
        password="password123",
        name="Feature User",
        state="Haryana",
        area="Rural",
        employment_status="Farmer",
        annual_income=250000
    )
    assert user is not None
    session_id = db.create_session(user["user_id"], email)
    test_client = TestClient(app)
    test_client.cookies.set("session_id", session_id)
    return test_client, user["user_id"]


def test_compare_and_checklist_flow():
    test_client, _ = _auth_client()

    compare_resp = test_client.post(
        "/api/v1/schemes/compare",
        json={"scheme_names": ["PM Kisan", "Atal Pension Yojana"]}
    )
    assert compare_resp.status_code == 200
    compare_data = compare_resp.json()
    assert len(compare_data.get("comparison", [])) == 2

    checklist_resp = test_client.post(
        "/api/v1/checklists/generate",
        json={"scheme_name": "PM Kisan"}
    )
    assert checklist_resp.status_code == 200
    checklist = checklist_resp.json().get("checklist", {})
    assert checklist.get("scheme_name") == "PM Kisan"
    assert isinstance(checklist.get("items"), list)
    assert len(checklist.get("items")) > 0


def test_alert_subscription_and_dispatch():
    test_client, _ = _auth_client()

    create_alert = test_client.post(
        "/api/v1/alerts/subscriptions",
        json={
            "scheme_name": "PM Kisan",
            "channel": "push",
            "contact": "device-token-1",
            "next_deadline": "2026-03-20"
        }
    )
    assert create_alert.status_code == 200
    create_data = create_alert.json()
    assert create_data.get("success") is True
    assert "initial_delivery" in create_data

    dispatch_resp = test_client.post("/api/v1/alerts/dispatch")
    assert dispatch_resp.status_code == 200
    dispatch_data = dispatch_resp.json()
    assert dispatch_data.get("success") is True
    assert dispatch_data.get("mode") in {"sync", "queued"}

    alert_id = create_data["alert"]["id"]
    pause_resp = test_client.post(f"/api/v1/alerts/subscriptions/{alert_id}", json={"is_active": False})
    assert pause_resp.status_code == 200
    paused_alerts = pause_resp.json().get("alerts", [])
    paused = [a for a in paused_alerts if a["id"] == alert_id]
    assert paused and paused[0]["is_active"] == 0


def test_family_prefill_and_simulator():
    test_client, _ = _auth_client()

    add_member = test_client.post(
        "/api/v1/family/members",
        json={"name": "Member One", "relationship": "Child", "age": 14, "state": "Haryana"}
    )
    assert add_member.status_code == 200
    members = add_member.json().get("members", [])
    assert len(members) >= 1

    family_eligibility = test_client.get("/api/v1/family/eligibility")
    assert family_eligibility.status_code == 200
    assert "family_results" in family_eligibility.json()

    prefill_resp = test_client.post(
        "/api/v1/prefill",
        json={"scheme_name": "PM Kisan", "ocr_fields": {"name": "Feature User"}}
    )
    assert prefill_resp.status_code == 200
    prefill_sheet = prefill_resp.json().get("prefill_sheet", {})
    assert prefill_sheet.get("generated_for_scheme") == "PM Kisan"

    sim_resp = test_client.post(
        "/api/v1/eligibility/simulate",
        json={"overrides": {"annual_income": 180000, "age": 29}, "top_k": 3}
    )
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert isinstance(sim_data.get("results"), list)


def test_admin_dispatch_requires_admin_role_and_works():
    test_client, _ = _auth_client()
    test_client.post(
        "/api/v1/alerts/subscriptions",
        json={
            "scheme_name": "PM Kisan",
            "channel": "push",
            "contact": "device-token-admin",
            "next_deadline": "2026-03-20"
        }
    )

    unauthorized = test_client.post("/api/v1/admin/alerts/dispatch")
    assert unauthorized.status_code == 403

    admin_email = f"admin_{uuid.uuid4().hex[:10]}@example.com"
    admin_user = db.create_user(
        email=admin_email,
        password="password123",
        name="Admin User",
        role="admin",
    )
    assert admin_user is not None
    admin_session = db.create_session(admin_user["user_id"], admin_email)
    admin_client = TestClient(app)
    admin_client.cookies.set("session_id", admin_session)

    authorized = admin_client.post("/api/v1/admin/alerts/dispatch")
    assert authorized.status_code == 200
    payload = authorized.json()
    assert payload.get("success") is True
    assert payload.get("mode") in {"sync", "queued", "sync_fallback"}
