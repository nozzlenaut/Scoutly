from fastapi.testclient import TestClient

from app.main import app
from app.models.listing import Listing
from app.services.feedback_store import (
    BadResultReport,
    ebay_item_id_from_url,
    filter_reported_listings,
    report_bad_result,
)


def test_ebay_item_id_from_url_handles_standard_item_url():
    assert ebay_item_id_from_url("https://www.ebay.com/itm/377191325248?campid=123") == "377191325248"


def test_report_bad_result_hides_matching_product_listing(tmp_path, monkeypatch):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    bad = Listing(
        provider="eBay",
        title="EOS RP Camera Accessories",
        price=10,
        shipping=0,
        total_price=10,
        condition="Used",
        url="https://www.ebay.com/itm/123456789012?customid=scoutly",
    )
    good = Listing(
        provider="eBay",
        title="Canon EOS RP Mirrorless Camera Body",
        price=599,
        shipping=0,
        total_price=599,
        condition="Used",
        url="https://www.ebay.com/itm/999999999999",
    )

    report_bad_result(
        BadResultReport(
            url=str(bad.url),
            title=bad.title,
            provider="eBay",
            category="cameras",
            product_id="camera-canon-eos-rp-body",
            query="Canon EOS RP Body",
            reason="accessory_or_part",
        )
    )

    filtered = filter_reported_listings(
        [bad, good],
        product_id="camera-canon-eos-rp-body",
        category="cameras",
    )

    assert filtered == [good]


def test_report_bad_result_is_product_scoped(tmp_path, monkeypatch):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    listing = Listing(
        provider="eBay",
        title="Shared marketplace item",
        price=100,
        shipping=0,
        total_price=100,
        condition="Used",
        url="https://www.ebay.com/itm/123456789012",
    )

    report_bad_result(
        BadResultReport(
            url=str(listing.url),
            category="cameras",
            product_id="camera-a",
            reason="wrong_item",
        )
    )

    assert filter_reported_listings([listing], product_id="camera-b", category="cameras") == [listing]
    assert filter_reported_listings([listing], product_id="camera-a", category="cameras") == []


def test_report_endpoint_saves_bad_result(tmp_path, monkeypatch):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.post(
        "/api/results/report",
        json={
            "url": "https://www.ebay.com/itm/123456789012",
            "title": "Camera Strap",
            "provider": "eBay",
            "category": "cameras",
            "product_id": "camera-sony-a7-iii-body",
            "query": "Sony A7 III Body",
            "reason": "accessory_or_part",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["link_key"] == "ebay:item:123456789012"
