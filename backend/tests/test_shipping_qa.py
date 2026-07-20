from app.providers.ebay import EbayConfig
from app.services.shipping_qa import _context_header, _item_result, _search_params, _shipping_option


class _FakeProvider:
    def __init__(self):
        self.config = EbayConfig(
            client_id="client",
            client_secret="secret",
            affiliate_campaign_id="1234567890",
            affiliate_reference_id="shipping-lab",
        )

    def _category_id_for(self, category: str | None) -> str | None:
        return "31388" if category == "cameras" else None


def test_shipping_context_header_preserves_affiliate_and_uses_requested_zip():
    header = _context_header(_FakeProvider(), "US", "48035")

    assert "affiliateCampaignId=1234567890" in header
    assert "affiliateReferenceId=shipping-lab" in header
    assert "contextualLocation=country%3DUS%2Czip%3D48035" in header


def test_shipping_search_filters_to_requested_delivery_location():
    params = _search_params(_FakeProvider(), "Sony a6700", "cameras", "US", "48035", 5)

    assert params["category_ids"] == "31388"
    assert "deliveryCountry:US" in params["filter"]
    assert "deliveryPostalCode:48035" in params["filter"]
    assert params["limit"] == "5"


def test_shipping_option_maps_method_dates_and_import_charges():
    option = _shipping_option(
        {
            "shippingCost": {"value": "12.99", "currency": "USD"},
            "shippingCostType": "CALCULATED",
            "shippingCarrierCode": "USPS",
            "shippingServiceCode": "USPS Ground Advantage",
            "type": "STANDARD",
            "minEstimatedDeliveryDate": "2026-07-22T00:00:00.000Z",
            "maxEstimatedDeliveryDate": "2026-07-25T00:00:00.000Z",
            "importCharges": {"value": "4.00", "currency": "USD"},
            "shipToLocationUsedForEstimate": {"country": "US", "postalCode": "48035"},
        }
    )

    assert option["cost"] == 12.99
    assert option["carrier"] == "USPS"
    assert option["service"] == "USPS Ground Advantage"
    assert option["min_delivery"].startswith("2026-07-22")
    assert option["import_charges"] == 4.0
    assert option["estimate_postal_code"] == "48035"


def test_item_result_prefers_detailed_shipping_method_over_summary_cost_only():
    result = _item_result(
        {
            "itemId": "v1|123|0",
            "title": "Sony a6700 Camera Body",
            "price": {"value": "1099.00", "currency": "USD"},
            "itemWebUrl": "https://www.ebay.com/itm/123",
            "shippingOptions": [{"shippingCost": {"value": "19.00", "currency": "USD"}}],
        },
        {
            "itemId": "v1|123|0",
            "title": "Sony a6700 Camera Body",
            "price": {"value": "1099.00", "currency": "USD"},
            "shippingOptions": [
                {
                    "shippingCost": {"value": "14.00", "currency": "USD"},
                    "shippingCarrierCode": "FedEx",
                    "shippingServiceCode": "FedEx Ground",
                }
            ],
        },
        None,
    )

    assert result["shipping_cost"] == 14.0
    assert result["total_price"] == 1113.0
    assert result["best_shipping_option"]["service"] == "FedEx Ground"
    assert result["detail_loaded"] is True
