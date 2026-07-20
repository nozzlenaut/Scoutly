from app.models.listing import Listing
from app.ranking.scorer import is_bad_listing


def test_rejects_for_parts_condition():
    listing = Listing(
        provider="eBay",
        title="Sony Alpha A7 III Camera Body",
        price=500,
        shipping=0,
        total_price=500,
        condition="For parts or not working",
        url="https://example.com/item",
    )

    assert is_bad_listing(listing) is True


def test_top_listings_returns_multiple_valid_options():
    from app.catalog.catalog import match_product
    from app.ranking.scorer import top_listings

    product = match_product("RTX 3060 12GB", category="gpus").product
    listings = [
        Listing(provider="eBay", title="EVGA RTX 3060 12GB Graphics Card", price=190, shipping=0, total_price=190, condition="Used", url="https://example.com/1"),
        Listing(provider="eBay", title="ASUS RTX 3060 12GB Graphics Card", price=195, shipping=0, total_price=195, condition="Used", url="https://example.com/2"),
        Listing(provider="eBay", title="MSI RTX 3060 12GB Graphics Card", price=200, shipping=0, total_price=200, condition="Used", url="https://example.com/3"),
        Listing(provider="eBay", title="RTX 3060 12GB Box Only", price=20, shipping=0, total_price=20, condition="Used", url="https://example.com/4"),
    ]

    top = top_listings(listings, product, limit=3)
    assert len(top) == 3
    assert all("Box Only" not in item.title for item in top)


def test_rejects_zero_feedback_seller():
    listing = Listing(
        provider="eBay",
        title="Microsoft Xbox Series X 1TB Video Game Console",
        price=350,
        shipping=0,
        total_price=350,
        condition="Used",
        seller_feedback_score=0,
        url="https://example.com/xbox",
    )

    assert is_bad_listing(listing) is True


def test_low_feedback_seller_is_demoted():
    from app.models.listing import Listing
    from app.ranking.scorer import score_listing

    high_feedback = Listing(
        provider="eBay",
        title="NVIDIA RTX 3060 12GB Graphics Card",
        price=250,
        shipping=0,
        total_price=250,
        condition="Used",
        seller_rating=100,
        seller_feedback_score=500,
        url="https://www.ebay.com/itm/111111111111",
    )
    low_feedback = Listing(
        provider="eBay",
        title="NVIDIA RTX 3060 12GB Graphics Card",
        price=250,
        shipping=0,
        total_price=250,
        condition="Used",
        seller_rating=100,
        seller_feedback_score=2,
        url="https://www.ebay.com/itm/222222222222",
    )

    assert score_listing(high_feedback) > score_listing(low_feedback)


def test_rejects_seller_defined_variation_price_traps_for_exact_categories():
    from app.catalog.catalog import match_product

    console = match_product("Nintendo 3DS XL", category="consoles").product
    gpu = match_product("NVIDIA RTX A4000 16GB", category="gpus").product

    console_listing = Listing(
        provider="eBay",
        title="Nintendo 3DS XL Console - Choose Color",
        price=19.99,
        shipping=0,
        total_price=19.99,
        condition="Used",
        url="https://www.ebay.com/itm/188036851644",
        item_group_type="SELLER_DEFINED_VARIATIONS",
    )
    gpu_listing = Listing(
        provider="eBay",
        title="NVIDIA RTX A4000 16GB Video Card",
        price=49.99,
        shipping=0,
        total_price=49.99,
        condition="Used",
        url="https://www.ebay.com/itm/198381150500",
        item_group_type="SELLER_DEFINED_VARIATIONS",
    )

    assert is_bad_listing(console_listing, console) is True
    assert is_bad_listing(gpu_listing, gpu) is True


def test_clean_console_listing_ranks_above_same_price_bundle():
    from app.ranking.scorer import score_listing

    clean = Listing(
        provider="eBay",
        title="Nintendo Switch OLED Console with Joy-Con and Dock",
        price=220,
        shipping=0,
        total_price=220,
        condition="Used",
        seller_rating=99.8,
        seller_feedback_score=250,
        url="https://example.com/clean",
    )
    bundle = Listing(
        provider="eBay",
        title="Nintendo Switch OLED Console Bundle with Games",
        price=220,
        shipping=0,
        total_price=220,
        condition="Used",
        seller_rating=99.8,
        seller_feedback_score=250,
        warning_labels=["Bundle / extras included"],
        url="https://example.com/bundle",
    )

    assert score_listing(clean) > score_listing(bundle)


def test_rejects_seller_defined_variations_for_ram():
    from app.catalog.catalog import match_product

    product = match_product("DDR5 Desktop 32GB 2x16GB 6000 MT/s", category="ram").product
    listing = Listing(
        provider="eBay",
        title="DDR5 Desktop RAM 32GB 2x16GB 6000 UDIMM - Choose Capacity",
        price=19.99,
        shipping=0,
        total_price=19.99,
        condition="Used",
        url="https://www.ebay.com/itm/123456789012",
        item_group_type="SELLER_DEFINED_VARIATIONS",
    )
    assert is_bad_listing(listing, product) is True


def test_rejects_faulty_cpu_and_partial_function_gpu_titles():
    from app.catalog.catalog import match_product

    cpu = match_product("Intel Core i9-9900K", category="cpus").product
    gpu = match_product("RTX 3070 8GB", category="gpus").product

    faulty_cpu = Listing(
        provider="eBay",
        title="Intel Core i9-9900K 3.6GHz Desktop Processor FAULTY",
        price=80,
        shipping=0,
        total_price=80,
        condition="Used",
        url="https://example.com/faulty-cpu",
    )
    partial_gpu = Listing(
        provider="eBay",
        title="NVIDIA GeForce RTX 3070 8GB Only DisplayPort Works",
        price=160,
        shipping=0,
        total_price=160,
        condition="Used",
        url="https://example.com/partial-gpu",
    )
    clean_cpu = Listing(
        provider="eBay",
        title="Intel Core i9-9900K Desktop Processor Tested Working",
        price=180,
        shipping=0,
        total_price=180,
        condition="Used",
        url="https://example.com/clean-cpu",
    )

    assert is_bad_listing(faulty_cpu, cpu) is True
    assert is_bad_listing(partial_gpu, gpu) is True
    assert is_bad_listing(clean_cpu, cpu) is False


def test_rejects_defective_console_even_when_ebay_calls_it_used():
    from app.catalog.catalog import match_product

    product = match_product("Xbox Series X", category="consoles")
    assert product is not None
    listing = Listing(
        provider="eBay",
        title="Microsoft Xbox Series X Black Defective READ DESCRIPTION",
        price=399.99,
        shipping=0,
        total_price=399.99,
        condition="Used",
        seller_rating=99.8,
        seller_feedback_score=500,
        url="https://www.ebay.com/itm/123456789012",
    )

    assert is_bad_listing(listing, product.product) is True


def test_gpu_cooling_defects_are_rejected_but_negated_noise_is_allowed():
    from app.catalog.catalog import match_product

    product = match_product("RTX 3090 24GB", category="gpus")
    assert product is not None
    bad_titles = [
        "NVIDIA RTX 3090 24GB Fan Defect",
        "NVIDIA RTX 3090 24GB Defective Fan",
        "NVIDIA RTX 3090 24GB Clicking Fan",
        "NVIDIA RTX 3090 24GB Grinding Fan",
        "NVIDIA RTX 3090 24GB Fan Noise",
        "NVIDIA RTX 3090 24GB Overheating",
    ]
    for index, title in enumerate(bad_titles):
        listing = Listing(
            provider="eBay",
            title=title,
            price=700 + index,
            shipping=0,
            total_price=700 + index,
            condition="Used",
            url=f"https://example.com/gpu-{index}",
        )
        assert is_bad_listing(listing, product.product) is True

    clean = Listing(
        provider="eBay",
        title="NVIDIA RTX 3090 24GB Tested - No Fan Noise",
        price=800,
        shipping=0,
        total_price=800,
        condition="Used",
        url="https://example.com/gpu-clean",
    )
    assert is_bad_listing(clean, product.product) is False


def test_read_language_adds_visible_warning_and_penalty_for_camera():
    from app.catalog.catalog import match_product
    from app.ranking.scorer import score_listing

    product = match_product("Nikon Z5", category="cameras")
    assert product is not None
    clean = Listing(
        provider="eBay",
        title="Nikon Z5 Mirrorless Camera Body Tested",
        price=700,
        shipping=0,
        total_price=700,
        condition="Used",
        url="https://example.com/z5-clean",
    )
    review = Listing(
        provider="eBay",
        title="Nikon Z5 Mirrorless Camera Body *Read",
        price=700,
        shipping=0,
        total_price=700,
        condition="Used",
        url="https://example.com/z5-read",
    )

    clean_score = score_listing(clean, product.product)
    review_score = score_listing(review, product.product)

    assert review_score < clean_score
    assert "Seller asks you to review the description" in review.warning_labels
