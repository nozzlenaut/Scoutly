from fastapi.testclient import TestClient

from app.main import app
from app.services.beta_feedback_store import list_beta_feedback


def test_public_beta_feedback_is_saved_and_admin_can_read(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    response = client.post(
        "/api/feedback",
        json={
            "feedback_type": "usability",
            "category": "cpus",
            "message": "The exact model search worked, but this button was confusing.",
            "email": "tester@example.com",
            "page_url": "https://www.pricesift.app/search?category=cpus&q=9900k",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    records = list_beta_feedback()
    assert len(records) == 1
    assert records[0]["feedback_type"] == "usability"

    assert client.get("/api/analytics/beta-feedback").status_code == 401
    admin = client.get("/api/analytics/beta-feedback", params={"token": "secret"})
    assert admin.status_code == 200
    assert admin.json()["feedback"][0]["message"].startswith("The exact model")


def test_feedback_honeypot_is_accepted_without_storage(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    client = TestClient(app)
    response = client.post(
        "/api/feedback",
        json={
            "feedback_type": "general",
            "message": "This is bot-shaped feedback.",
            "website": "https://spam.invalid",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] is None
    assert list_beta_feedback() == []
