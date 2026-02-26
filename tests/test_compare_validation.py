import os
from fastapi.testclient import TestClient

os.environ['APP_TEST_MODE'] = '1'

from backend.app import app  # noqa: E402


client = TestClient(app)


def test_compare_rejects_duplicates():
    resp = client.post('/api/v1/schemes/compare', json={'scheme_names': ['PM Kisan', 'PM Kisan']})
    assert resp.status_code == 400
    assert 'unique' in resp.json()['detail'].lower()


def test_compare_requires_two_to_three_names():
    resp = client.post('/api/v1/schemes/compare', json={'scheme_names': ['PM Kisan']})
    assert resp.status_code == 422
