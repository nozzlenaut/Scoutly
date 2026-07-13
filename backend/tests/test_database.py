from contextlib import contextmanager

from fastapi.testclient import TestClient

from app.main import app
from app.services import database, feedback_store


def test_database_url_ignores_unresolved_railway_reference(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "${{Postgres.DATABASE_URL}}")
    assert database.database_url() is None
    assert database.database_configured() is False


def test_health_reports_file_fallback_without_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["storage"]["backend"] == "file"


def test_admin_is_closed_when_token_not_configured(monkeypatch):
    monkeypatch.delenv("SCOUTLY_ADMIN_TOKEN", raising=False)
    client = TestClient(app)
    response = client.get("/api/analytics/summary")
    assert response.status_code == 503


def test_filtered_listing_database_writes_are_batched(monkeypatch):
    batches: list[list[tuple]] = []
    connection_calls = 0

    class FakeResult:
        rowcount = 1

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def executemany(self, _sql, values):
            batches.append(list(values))

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def execute(self, _sql, _params=None):
            return FakeResult()

    @contextmanager
    def fake_connection():
        nonlocal connection_calls
        connection_calls += 1
        yield FakeConnection()

    monkeypatch.setattr(feedback_store, "database_configured", lambda: True)
    monkeypatch.setattr(feedback_store, "database_connection", fake_connection)

    feedback_store.log_filtered_listings(
        [
            {
                "url": "https://www.ebay.com/itm/111111111111",
                "title": "Bad listing one",
                "category": "lego",
                "reasons": ["partial"],
            },
            {
                "url": "https://www.ebay.com/itm/222222222222",
                "title": "Bad listing two",
                "category": "consoles",
                "reasons": ["accessory"],
            },
        ]
    )

    assert connection_calls == 1
    assert len(batches) == 1
    assert len(batches[0]) == 2
