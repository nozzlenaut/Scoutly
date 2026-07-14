from fastapi.testclient import TestClient

from app.main import app
from app.services import search_service


def test_unsupported_public_query_does_not_reach_marketplace(monkeypatch):
    async def fail_if_called(**_kwargs):
        raise AssertionError("Unsupported public query reached a marketplace provider")

    monkeypatch.setattr(search_service, "_search_provider", fail_if_called)
    client = TestClient(app)

    response = client.get(
        "/api/search",
        params={"q": "DJI Mavic 3 drone", "category": "cameras", "providers": "ebay"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resolved_product"] is None
    assert payload["results"] == []
    assert payload["auction_results"] == []
    assert payload["diagnostics"]["fixed_price_candidates"] == 0


def test_unsupported_public_auction_query_does_not_reach_marketplace(monkeypatch):
    async def fail_if_called(**_kwargs):
        raise AssertionError("Unsupported public auction query reached a marketplace provider")

    monkeypatch.setattr(search_service, "_search_provider", fail_if_called)
    client = TestClient(app)

    response = client.get(
        "/api/search/auctions",
        params={"q": "DJI Mavic 3 drone", "category": "cameras", "providers": "ebay"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resolved_product"] is None
    assert payload["auction_results"] == []
    assert payload["diagnostics"]["auction_candidates"] == 0


def test_supported_catalog_query_still_resolves():
    client = TestClient(app)
    response = client.get(
        "/api/search",
        params={"q": "Sony A7 IV", "category": "cameras", "providers": "ebay"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resolved_product"]["product"]["display_name"] == "Sony A7 IV Body"
