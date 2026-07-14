import asyncio

from app.providers.ebay import EbayConfig, EbayProvider, ebay_item_to_listing


def test_ebay_item_maps_to_listing():
    item = {
        "title": "Sony Alpha A7 III Mirrorless Camera Body",
        "price": {"value": "879.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/1234567890",
        "image": {"imageUrl": "https://i.ebayimg.com/images/test.jpg"},
        "seller": {"feedbackPercentage": "99.5", "feedbackScore": 42},
        "shippingOptions": [
            {"shippingCost": {"value": "14.99", "currency": "USD"}},
            {"shippingCost": {"value": "0.00", "currency": "USD"}},
        ],
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert listing.provider == "eBay"
    assert listing.title == "Sony Alpha A7 III Mirrorless Camera Body"
    assert listing.price == 879.99
    assert listing.shipping == 0
    assert listing.total_price == 879.99
    assert listing.seller_rating == 99.5
    assert listing.seller_feedback_score == 42


def test_ebay_item_prefers_affiliate_url():
    item = {
        "title": "Sony FE 24-70mm f/2.8 GM Lens",
        "price": {"value": "1099.00", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/plain",
        "itemAffiliateWebUrl": "https://www.ebay.com/itm/affiliate?campid=1234567890&customid=scoutly&toolid=10049",
        "seller": {},
        "shippingOptions": [],
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert str(listing.url) == "https://www.ebay.com/itm/affiliate?campid=1234567890&customid=scoutly&toolid=10049"
    assert listing.affiliate_url_used is True
    assert listing.affiliate_url_has_campaign_id is True


def test_ebay_item_adds_missing_campaign_to_partial_affiliate_url():
    item = {
        "title": "NVIDIA RTX 3060 12GB",
        "price": {"value": "219.00", "currency": "USD"},
        "condition": "Used",
        "itemAffiliateWebUrl": "https://www.ebay.com/itm/298498636414?_skw=NVIDIA+RTX+3060+12GB&customid=scoutly&toolid=10049",
        "seller": {},
        "shippingOptions": [],
    }

    listing = ebay_item_to_listing(item, affiliate_campaign_id="1234567890", affiliate_reference_id="scoutly")

    assert listing is not None
    url = str(listing.url)
    assert "campid=1234567890" in url
    assert "customid=scoutly" in url
    assert "toolid=10049" in url
    assert "mkevt=1" in url
    assert "mkcid=1" in url
    assert "mkrid=711-53200-19255-0" in url
    assert listing.affiliate_url_used is True
    assert listing.affiliate_url_has_campaign_id is True


def test_ebay_item_without_price_or_url_is_ignored():
    assert ebay_item_to_listing({"title": "Sony A7 III"}) is None
    assert ebay_item_to_listing({"price": {"value": "10"}, "itemWebUrl": "https://www.ebay.com/itm/1"}) is None



class _FakeTokenService:
    async def get_access_token(self) -> str:
        return "fake-token"


class _CaptureEbayProvider(EbayProvider):
    def __init__(self, marketplace_id: str = "EBAY_US"):
        self.config = EbayConfig(client_id="client", client_secret="secret", marketplace_id=marketplace_id)
        self.tokens = _FakeTokenService()
        self.last_headers: dict[str, str] = {}
        self.last_params: dict[str, str] = {}

    async def _search_request(self, headers: dict[str, str], params: dict[str, str]) -> dict:
        self.last_headers = headers
        self.last_params = params
        return {"itemSummaries": []}


def test_ebay_search_adds_camera_category_id():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("Sony A7 III Body", category="cameras"))

    assert provider.last_params["category_ids"] == "31388"
    assert provider.last_params["filter"] == "conditions:{USED},buyingOptions:{FIXED_PRICE}"


def test_ebay_search_adds_gpu_category_id():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("RTX 3060 12GB", category="gpus"))

    assert provider.last_params["category_ids"] == "27386"


def test_ebay_search_skips_category_id_for_non_us_marketplace():
    provider = _CaptureEbayProvider(marketplace_id="EBAY_GB")

    asyncio.run(provider.search("RTX 3060 12GB", category="gpus"))

    assert "category_ids" not in provider.last_params


def test_ebay_search_adds_affiliate_context_header():
    provider = _CaptureEbayProvider()
    provider.config.affiliate_campaign_id = "1234567890"
    provider.config.affiliate_reference_id = "scoutly-test"
    provider.config.delivery_postal_code = "90210"

    asyncio.run(provider.search("Tesla V100", category="gpus"))

    header = provider.last_headers["X-EBAY-C-ENDUSERCTX"]
    assert "affiliateCampaignId=1234567890" in header
    assert "affiliateReferenceId=scoutly-test" in header
    assert "contextualLocation=country%3DUS%2Czip%3D90210" in header


def test_ebay_auction_item_uses_current_bid_and_end_date():
    item = {
        "title": "NVIDIA Tesla P100 16GB GPU",
        "price": {"value": "450.00", "currency": "USD"},
        "currentBidPrice": {"value": "180.50", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/123456789012",
        "buyingOptions": ["AUCTION"],
        "bidCount": 7,
        "itemEndDate": "2099-01-01T00:00:00.000Z",
    }

    listing = ebay_item_to_listing(item, requested_listing_type="auction")

    assert listing is not None
    assert listing.listing_type == "auction"
    assert listing.price == 180.50
    assert listing.current_bid_price == 180.50
    assert listing.bid_count == 7
    assert listing.item_end_date == "2099-01-01T00:00:00.000Z"


def test_ebay_auction_search_uses_auction_filter_and_ending_soonest():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("NVIDIA Tesla P100", category="gpus", buying_option="auction"))

    assert provider.last_params["category_ids"] == "27386"
    assert provider.last_params["filter"] == "conditions:{USED},buyingOptions:{AUCTION}"
    assert provider.last_params["sort"] == "endingSoonest"


def test_ebay_search_adds_lego_category_id():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("LEGO 75192", category="lego"))

    assert provider.last_params["category_ids"] == "19006"


def test_ebay_search_adds_console_category_id():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("Xbox Series X", category="consoles"))

    assert provider.last_params["category_ids"] == "139971"


def test_ebay_seller_sentinel_values_become_unavailable():
    item = {
        "title": "Sony PlayStation 4 Pro 1TB Console",
        "price": {"value": "149.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/999999999999",
        "seller": {"feedbackPercentage": "0", "feedbackScore": -1},
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert listing.seller_rating is None
    assert listing.seller_feedback_score is None


def test_ebay_item_maps_seller_defined_variation_group():
    item = {
        "title": "Nintendo 3DS XL Console - Choose Color",
        "price": {"value": "19.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/188036851644",
        "itemGroupType": "SELLER_DEFINED_VARIATIONS",
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert listing.item_group_type == "SELLER_DEFINED_VARIATIONS"


def test_ebay_bundle_titles_receive_comparison_warning():
    item = {
        "title": "Nintendo Switch OLED Console Bundle with Games and SD Card",
        "price": {"value": "249.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/123123123123",
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert "Bundle / extras included" in listing.warning_labels


def test_ebay_search_adds_ram_category_id():
    provider = _CaptureEbayProvider()
    asyncio.run(provider.search("DDR4 32GB 2x16GB UDIMM RAM", category="ram"))
    assert provider.last_params["category_ids"] == "170083"
