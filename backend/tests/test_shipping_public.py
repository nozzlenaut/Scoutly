import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.services import shipping_qa


def test_public_delivery_estimates_use_post_body_and_do_not_echo_zip(monkeypatch):
    captured: dict = {}

    async def fake_estimates(item_ids, postal_code, country):
        captured.update({"item_ids": item_ids, "postal_code": postal_code, "country": country})
        return {
            "country": "US",
            "returned": 1,
            "items": [
                {
                    "item_id": "v1|123|0",
                    "title": "Sony A7 III",
                    "shipping_cost": 12.5,
                    "best_shipping_option": {
                        "service": "USPSGroundAdvantage",
                        "min_delivery": "2026-07-23T00:00:00.000Z",
                        "max_delivery": "2026-07-27T00:00:00.000Z",
                    },
                }
            ],
        }

    monkeypatch.setattr("app.api.shipping.get_delivery_estimates", fake_estimates)
    response = TestClient(app).post(
        "/api/shipping/estimates",
        json={"postal_code": "48035", "country": "US", "item_ids": ["v1|123|0"]},
    )

    assert response.status_code == 200
    assert captured == {
        "item_ids": ["v1|123|0"],
        "postal_code": "48035",
        "country": "US",
    }
    assert "postal_code" not in response.json()


def test_public_delivery_estimates_reject_invalid_zip(monkeypatch):
    async def fake_estimates(_item_ids, _postal_code, _country):
        raise ValueError("ZIP code format is not valid.")

    monkeypatch.setattr("app.api.shipping.get_delivery_estimates", fake_estimates)
    response = TestClient(app).post(
        "/api/shipping/estimates",
        json={"postal_code": "??", "country": "US", "item_ids": ["123"]},
    )

    assert response.status_code == 422


def test_public_delivery_response_strips_ebay_echoed_zip(monkeypatch):
    class FakeClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

    class FakeProvider:
        config = SimpleNamespace(
            api_base="https://api.ebay.test",
            affiliate_campaign_id=None,
            affiliate_reference_id=None,
        )

        async def _request_headers(self):
            return {}

    async def fake_detail(_client, _url, _headers):
        return {
            "itemId": "v1|123|0",
            "title": "Sony A7 III",
            "price": {"value": "750.00", "currency": "USD"},
            "shippingOptions": [
                {
                    "shippingCost": {"value": "12.50", "currency": "USD"},
                    "shippingServiceCode": "USPSGroundAdvantage",
                    "minEstimatedDeliveryDate": "2026-07-23T00:00:00.000Z",
                    "maxEstimatedDeliveryDate": "2026-07-27T00:00:00.000Z",
                    "shipToLocationUsedForEstimate": {
                        "country": "US",
                        "postalCode": "48035",
                    },
                }
            ],
        }, None

    monkeypatch.setattr(shipping_qa, "EbayProvider", FakeProvider)
    monkeypatch.setattr(shipping_qa, "_fetch_item_detail", fake_detail)
    monkeypatch.setattr(shipping_qa.httpx, "AsyncClient", FakeClient)
    payload = asyncio.run(
        shipping_qa.get_delivery_estimates(["v1|123|0"], "48035", "US")
    )

    assert "48035" not in str(payload)
    assert payload["items"][0]["shipping_cost"] == 12.5
    assert payload["items"][0]["best_shipping_option"]["service"] == "USPSGroundAdvantage"
