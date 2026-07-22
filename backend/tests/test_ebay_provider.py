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
    assert provider.last_params["limit"] == "35"
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


def test_ebay_search_uses_deeper_pool_for_exhausted_console_models():
    provider = _CaptureEbayProvider()

    queries = [
        "PlayStation 5 console",
        "PlayStation 5 Slim console",
        "PlayStation 4 Slim console",
        "Xbox Series S console",
        "Xbox Series X console",
    ]

    for query in queries:
        asyncio.run(provider.search(query, category="consoles"))

        assert provider.last_params["category_ids"] == "139971"
        assert provider.last_params["limit"] == "100"


def test_ebay_search_keeps_other_console_pool_at_65():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search("Nintendo Switch OLED console", category="consoles"))

    assert provider.last_params["category_ids"] == "139971"
    assert provider.last_params["limit"] == "65"


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


def test_ddr3l_listing_gets_voltage_compatibility_warning():
    item = {
        "title": "Samsung 16GB 2x8GB DDR3L PC3L-12800S SODIMM Laptop Memory",
        "price": {"value": "24.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/111111111111",
    }
    listing = ebay_item_to_listing(item)
    assert listing is not None
    assert "DDR3L — verify voltage compatibility" in listing.warning_labels


def test_ebay_item_flags_description_review_language_without_rejecting_listing():
    variants = [
        "Sony A7R IV Camera Body *Read",
        "Sony A7R IV Camera Body Read Desc",
        "Sony A7R IV Camera Body Read Description",
        "Sony A7R IV Camera Body See Description",
    ]
    for index, title in enumerate(variants, start=1):
        listing = ebay_item_to_listing(
            {
                "title": title,
                "price": {"value": "999.00", "currency": "USD"},
                "condition": "Used",
                "itemWebUrl": f"https://www.ebay.com/itm/90000000000{index}",
                "seller": {},
                "shippingOptions": [],
            }
        )
        assert listing is not None
        assert "Seller asks you to review the description" in listing.warning_labels


def test_ebay_search_adds_cpu_category_id():
    provider = _CaptureEbayProvider()
    asyncio.run(provider.search("Intel Core i7-12700K CPU", category="cpus"))
    assert provider.last_params["category_ids"] == "164"


def test_ebay_gtin_search_uses_exact_isbn_and_books_category():
    provider = _CaptureEbayProvider()

    asyncio.run(provider.search_gtin("9780306406157", category="books"))

    assert provider.last_params["gtin"] == "9780306406157"
    assert "q" not in provider.last_params
    assert provider.last_params["category_ids"] == "261186"
    assert provider.last_params["filter"] == "conditions:{USED},buyingOptions:{FIXED_PRICE}"


def test_ebay_search_can_limit_results_to_us_item_location():
    provider = _CaptureEbayProvider()

    asyncio.run(
        provider.search(
            "Sony A7 IV Body",
            category="cameras",
            item_location_country="US",
        )
    )

    assert provider.last_params["filter"] == "conditions:{USED},buyingOptions:{FIXED_PRICE},itemLocationCountry:US"


def test_ebay_gtin_search_can_limit_results_to_us_item_location():
    provider = _CaptureEbayProvider()

    asyncio.run(
        provider.search_gtin(
            "9780306406157",
            category="books",
            item_location_country="US",
        )
    )

    assert provider.last_params["filter"] == "conditions:{USED},buyingOptions:{FIXED_PRICE},itemLocationCountry:US"


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------


class _TwoPageEbayProvider(EbayProvider):
    """Captures request count and params, returns different results per page."""

    def __init__(self, marketplace_id: str = "EBAY_US", second_page_items=None, second_page_error=None):
        self.config = EbayConfig(client_id="client", client_secret="secret", marketplace_id=marketplace_id)
        self.tokens = _FakeTokenService()
        self.request_count = 0
        self.last_params: dict[str, str] = {}
        self.second_page_items = second_page_items or []
        self.second_page_error = second_page_error

    async def _search_request(self, headers: dict[str, str], params: dict[str, str]) -> dict:
        self.request_count += 1
        self.last_params = params
        offset = int(params.get("offset", "0"))
        if offset == 0:
            return {
                "next": "https://api.ebay.com/buy/browse/v1/item_summary/search?limit=100&offset=100&q=Xbox+Series+S",
                "itemSummaries": [
                    {
                        "title": "Xbox Series S Controller Only",
                        "price": {"value": "59.99", "currency": "USD"},
                        "condition": "Used",
                        "itemWebUrl": "https://www.ebay.com/itm/111111111111",
                        "seller": {"feedbackPercentage": "99.0", "feedbackScore": 100},
                        "shippingOptions": [{"shippingCost": {"value": "0", "currency": "USD"}}],
                    }
                ],
            }
        if self.second_page_error is not None:
            raise self.second_page_error
        return {"itemSummaries": self.second_page_items}


def _console_item(title, price="249.99"):
    return {
        "title": title,
        "price": {"value": price, "currency": "USD"},
        "condition": "Used - Good",
        "itemWebUrl": "https://www.ebay.com/itm/999999999999",
        "seller": {"feedbackPercentage": "99.5", "feedbackScore": 500},
        "shippingOptions": [{"shippingCost": {"value": "0", "currency": "USD"}}],
    }


def test_ebay_search_next_field_triggers_second_page_request():
    provider = _TwoPageEbayProvider(second_page_items=[_console_item("Page 2 Console")])

    asyncio.run(provider.search("Xbox Series S console", category="consoles"))

    assert provider.request_count == 2
    assert provider.last_params.get("offset") == "100"


def test_ebay_search_no_next_field_means_single_request():
    provider = _TwoPageEbayProvider()

    # Override _search_request to return no "next" field on page 1
    async def single_page_request(headers, params):
        provider.request_count += 1
        provider.last_params = params
        return {
            "itemSummaries": [
                {
                    "title": "Xbox Series S Console",
                    "price": {"value": "249.99", "currency": "USD"},
                    "condition": "Used",
                    "itemWebUrl": "https://www.ebay.com/itm/111111111111",
                    "seller": {"feedbackPercentage": "99.0", "feedbackScore": 100},
                    "shippingOptions": [{"shippingCost": {"value": "0", "currency": "USD"}}],
                }
            ]
        }

    provider._search_request = single_page_request

    asyncio.run(provider.search("Xbox Series S console", category="consoles"))

    assert provider.request_count == 1
    assert "offset" not in provider.last_params


def test_ebay_search_combines_first_and_second_page_results():
    provider = _TwoPageEbayProvider(second_page_items=[_console_item("Page 2 Console")])

    listings = asyncio.run(provider.search("Xbox Series S console", category="consoles"))

    assert len(listings) == 2
    titles = [listing.title for listing in listings]
    assert "Xbox Series S Controller Only" in titles
    assert "Page 2 Console" in titles


def test_ebay_search_page_two_failure_returns_page_one_listings():
    provider = _TwoPageEbayProvider(
        second_page_items=[],
        second_page_error=RuntimeError("simulated eBay API failure"),
    )

    listings = asyncio.run(provider.search("Xbox Series S console", category="consoles"))

    assert provider.request_count == 2
    assert len(listings) == 1
    assert listings[0].title == "Xbox Series S Controller Only"


def test_ebay_search_non_deep_console_does_not_fetch_second_page():
    provider = _TwoPageEbayProvider(second_page_items=[_console_item("Page 2 Console")])

    asyncio.run(provider.search("Nintendo Switch OLED console", category="consoles"))

    assert provider.request_count == 1
    assert "offset" not in provider.last_params
