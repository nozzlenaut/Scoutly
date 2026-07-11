import hashlib

from fastapi.testclient import TestClient

from app.main import app


def test_ebay_notification_challenge_response(monkeypatch):
    endpoint = "https://example.com/api/ebay/notifications"
    token = "Scoutly_Test_Token_1234567890_abcdef"
    challenge_code = "challenge123"
    monkeypatch.setenv("EBAY_NOTIFICATION_ENDPOINT_URL", endpoint)
    monkeypatch.setenv("EBAY_NOTIFICATION_VERIFICATION_TOKEN", token)

    client = TestClient(app)
    response = client.get(f"/api/ebay/notifications?challenge_code={challenge_code}")

    expected = hashlib.sha256(f"{challenge_code}{token}{endpoint}".encode("utf-8")).hexdigest()
    assert response.status_code == 200
    assert response.json() == {"challengeResponse": expected}


def test_ebay_notification_post_acknowledges():
    client = TestClient(app)
    response = client.post("/api/ebay/notifications", json={"metadata": {}, "notification": {}})

    assert response.status_code == 204
    assert response.content == b""
