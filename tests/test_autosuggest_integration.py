import os
from fastapi.testclient import TestClient

os.environ["APP_TEST_MODE"] = "1"

from backend.app import app  # noqa: E402

client = TestClient(app)


def test_autosuggest_prefix_returns_matches():
    resp = client.get("/api/v1/schemes/autosuggest?q=PM&limit=5")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["query"] == "PM"
    assert isinstance(payload["suggestions"], list)
    assert any("PM" in s for s in payload["suggestions"])


def test_autosuggest_fuzzy_match_typo():
    resp = client.get("/api/v1/schemes/autosuggest?q=Kisn&limit=8")
    assert resp.status_code == 200
    suggestions = resp.json()["suggestions"]
    assert any("Kisan" in s for s in suggestions)


def test_natural_language_search_endpoint():
    resp = client.post("/api/v1/schemes/search", json={"query": "farmer income support schemes", "limit": 4})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["query"] == "farmer income support schemes"
    assert isinstance(payload["results"], list)
    assert len(payload["results"]) <= 4
