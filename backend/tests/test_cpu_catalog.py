import asyncio

from app.catalog.catalog import list_products, listing_matches_product, match_product
from app.services.search_service import search_best_deals_with_auctions


def test_cpu_catalog_has_broad_desktop_coverage_and_unique_ids():
    products = list_products("cpus")
    assert len(products) >= 150
    assert len({product.id for product in products}) == len(products)
    assert {product.metadata["socket"] for product in products} >= {
        "AM4",
        "AM5",
        "LGA1151",
        "LGA1200",
        "LGA1700",
        "LGA1851",
    }


def test_cpu_builder_resolves_exact_amd_intel_and_core_ultra_models():
    assert match_product("AMD Ryzen 7 5800X3D", "cpus").product.id == "cpu-amd-ryzen-7-5800x3d"
    assert match_product("i7-12700K", "cpus").product.id == "cpu-intel-core-i7-12700k"
    assert match_product("Intel Core Ultra 9 285K", "cpus").product.id == "cpu-intel-core-ultra-9-285k"


def test_cpu_suffixes_remain_exact_products():
    k = match_product("Intel Core i7-12700K", "cpus").product
    kf = match_product("Intel Core i7-12700KF", "cpus").product
    x = match_product("AMD Ryzen 7 5800X", "cpus").product
    x3d = match_product("AMD Ryzen 7 5800X3D", "cpus").product

    assert k.id != kf.id
    assert x.id != x3d.id
    assert listing_matches_product("Intel Core i7-12700K CPU Processor Tested", k)
    assert not listing_matches_product("Intel Core i7-12700KF CPU Processor Tested", k)
    assert not listing_matches_product("AMD Ryzen 7 5800X3D Processor", x)


def test_cpu_accepts_tray_or_boxed_but_rejects_bundles_parts_samples_and_lots():
    product = match_product("AMD Ryzen 7 7800X3D", "cpus").product

    accepted = [
        "AMD Ryzen 7 7800X3D Desktop CPU Processor OEM Tray Tested",
        "AMD Ryzen 7 7800X3D 8-Core Processor Retail Boxed",
        "AMD Ryzen 7 7800X3D CPU Only Pulled From Working System",
    ]
    rejected = [
        "AMD Ryzen 7 7800X3D Motherboard Bundle",
        "AMD Ryzen 7 7800X3D CPU Cooler Only",
        "AMD Ryzen 7 7800X3D Engineering Sample Confidential",
        "AMD Ryzen 7 7800X3D Bent Pins",
        "Lot of 2 AMD Ryzen 7 7800X3D CPUs",
        "Gaming PC AMD Ryzen 7 7800X3D RTX 4080",
    ]

    assert all(listing_matches_product(title, product) for title in accepted)
    assert all(not listing_matches_product(title, product) for title in rejected)


def test_cpu_rejects_titles_with_multiple_model_codes():
    product = match_product("AMD Ryzen 7 5800X3D", "cpus").product
    assert not listing_matches_product(
        "AMD Ryzen 5600X 5700X 5800X3D AM4 CPU Processor Choose Model",
        product,
    )


def test_cpu_mock_search_returns_exact_cpu_and_filters_bundle():
    resolved, results, _auctions, diagnostics, price_context = asyncio.run(
        search_best_deals_with_auctions(
            "Intel Core i7-12700K",
            ["ebay"],
            category="cpus",
            include_auctions=False,
        )
    )
    assert resolved is not None
    assert resolved.product.id == "cpu-intel-core-i7-12700k"
    assert len(results) == 1
    assert "Tested Working" in results[0].title
    assert diagnostics.fixed_price_candidates == 2
    assert diagnostics.fixed_price_eligible == 1
