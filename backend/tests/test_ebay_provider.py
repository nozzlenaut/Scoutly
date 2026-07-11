from app.providers.ebay import ebay_item_to_listing


def test_ebay_item_maps_to_listing():
    item = {
        "title": "Sony Alpha A7 III Mirrorless Camera Body",
        "price": {"value": "879.99", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/1234567890",
        "image": {"imageUrl": "https://i.ebayimg.com/images/test.jpg"},
        "seller": {"feedbackPercentage": "99.5"},
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


def test_ebay_item_prefers_affiliate_url():
    item = {
        "title": "Sony FE 24-70mm f/2.8 GM Lens",
        "price": {"value": "1099.00", "currency": "USD"},
        "condition": "Used",
        "itemWebUrl": "https://www.ebay.com/itm/plain",
        "itemAffiliateWebUrl": "https://rover.ebay.com/affiliate-link",
        "seller": {},
        "shippingOptions": [],
    }

    listing = ebay_item_to_listing(item)

    assert listing is not None
    assert str(listing.url) == "https://rover.ebay.com/affiliate-link"


def test_ebay_item_without_price_or_url_is_ignored():
    assert ebay_item_to_listing({"title": "Sony A7 III"}) is None
    assert ebay_item_to_listing({"price": {"value": "10"}, "itemWebUrl": "https://www.ebay.com/itm/1"}) is None
