import re
from functools import lru_cache

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product


# Consumer desktop CPUs only. Suffix variants remain exact products because
# K/KF/F/G/X3D and similar markers materially change the chip.
CPU_FAMILIES: dict[str, dict[str, dict[str, list[tuple[str, str]]]]] = {
    "amd": {
        "AM4": {
            "Ryzen 3000": [
                ("Ryzen 3", "3100"),
                ("Ryzen 3", "3300X"),
                ("Ryzen 5", "3500X"),
                ("Ryzen 5", "3600"),
                ("Ryzen 5", "3600X"),
                ("Ryzen 5", "3600XT"),
                ("Ryzen 7", "3700X"),
                ("Ryzen 7", "3800X"),
                ("Ryzen 7", "3800XT"),
                ("Ryzen 9", "3900X"),
                ("Ryzen 9", "3900XT"),
                ("Ryzen 9", "3950X"),
            ],
            "Ryzen 4000G": [
                ("Ryzen 3", "4100"),
                ("Ryzen 3", "4300G"),
                ("Ryzen 5", "4500"),
                ("Ryzen 5", "4600G"),
                ("Ryzen 7", "4700G"),
            ],
            "Ryzen 5000": [
                ("Ryzen 5", "5500"),
                ("Ryzen 5", "5600"),
                ("Ryzen 5", "5600G"),
                ("Ryzen 5", "5600GT"),
                ("Ryzen 5", "5600X"),
                ("Ryzen 7", "5700"),
                ("Ryzen 7", "5700G"),
                ("Ryzen 7", "5700X"),
                ("Ryzen 7", "5700X3D"),
                ("Ryzen 7", "5800X"),
                ("Ryzen 7", "5800XT"),
                ("Ryzen 7", "5800X3D"),
                ("Ryzen 9", "5900X"),
                ("Ryzen 9", "5900XT"),
                ("Ryzen 9", "5950X"),
            ],
        },
        "AM5": {
            "Ryzen 7000": [
                ("Ryzen 5", "7500F"),
                ("Ryzen 5", "7600"),
                ("Ryzen 5", "7600X"),
                ("Ryzen 7", "7700"),
                ("Ryzen 7", "7700X"),
                ("Ryzen 7", "7800X3D"),
                ("Ryzen 9", "7900"),
                ("Ryzen 9", "7900X"),
                ("Ryzen 9", "7900X3D"),
                ("Ryzen 9", "7950X"),
                ("Ryzen 9", "7950X3D"),
            ],
            "Ryzen 8000G": [
                ("Ryzen 3", "8300G"),
                ("Ryzen 5", "8500G"),
                ("Ryzen 5", "8600G"),
                ("Ryzen 7", "8700G"),
            ],
            "Ryzen 9000": [
                ("Ryzen 5", "9600X"),
                ("Ryzen 7", "9700X"),
                ("Ryzen 7", "9800X3D"),
                ("Ryzen 9", "9900X"),
                ("Ryzen 9", "9900X3D"),
                ("Ryzen 9", "9950X"),
                ("Ryzen 9", "9950X3D"),
            ],
        },
    },
    "intel": {
        "LGA1151": {
            "8th Gen Core": [
                ("Core i3", "8100"),
                ("Core i3", "8350K"),
                ("Core i5", "8400"),
                ("Core i5", "8500"),
                ("Core i5", "8600K"),
                ("Core i7", "8700"),
                ("Core i7", "8700K"),
            ],
            "9th Gen Core": [
                ("Core i3", "9100"),
                ("Core i3", "9100F"),
                ("Core i5", "9400"),
                ("Core i5", "9400F"),
                ("Core i5", "9600K"),
                ("Core i5", "9600KF"),
                ("Core i7", "9700"),
                ("Core i7", "9700F"),
                ("Core i7", "9700K"),
                ("Core i7", "9700KF"),
                ("Core i9", "9900"),
                ("Core i9", "9900K"),
                ("Core i9", "9900KF"),
                ("Core i9", "9900KS"),
            ],
        },
        "LGA1200": {
            "10th Gen Core": [
                ("Core i3", "10100"),
                ("Core i3", "10100F"),
                ("Core i5", "10400"),
                ("Core i5", "10400F"),
                ("Core i5", "10600K"),
                ("Core i5", "10600KF"),
                ("Core i7", "10700"),
                ("Core i7", "10700F"),
                ("Core i7", "10700K"),
                ("Core i7", "10700KF"),
                ("Core i9", "10850K"),
                ("Core i9", "10900"),
                ("Core i9", "10900F"),
                ("Core i9", "10900K"),
                ("Core i9", "10900KF"),
            ],
            "11th Gen Core": [
                ("Core i5", "11400"),
                ("Core i5", "11400F"),
                ("Core i5", "11600K"),
                ("Core i5", "11600KF"),
                ("Core i7", "11700"),
                ("Core i7", "11700F"),
                ("Core i7", "11700K"),
                ("Core i7", "11700KF"),
                ("Core i9", "11900"),
                ("Core i9", "11900F"),
                ("Core i9", "11900K"),
                ("Core i9", "11900KF"),
            ],
        },
        "LGA1700": {
            "12th Gen Core": [
                ("Core i3", "12100"),
                ("Core i3", "12100F"),
                ("Core i5", "12400"),
                ("Core i5", "12400F"),
                ("Core i5", "12600K"),
                ("Core i5", "12600KF"),
                ("Core i7", "12700"),
                ("Core i7", "12700F"),
                ("Core i7", "12700K"),
                ("Core i7", "12700KF"),
                ("Core i9", "12900"),
                ("Core i9", "12900F"),
                ("Core i9", "12900K"),
                ("Core i9", "12900KF"),
                ("Core i9", "12900KS"),
            ],
            "13th Gen Core": [
                ("Core i3", "13100"),
                ("Core i3", "13100F"),
                ("Core i5", "13400"),
                ("Core i5", "13400F"),
                ("Core i5", "13500"),
                ("Core i5", "13600K"),
                ("Core i5", "13600KF"),
                ("Core i7", "13700"),
                ("Core i7", "13700F"),
                ("Core i7", "13700K"),
                ("Core i7", "13700KF"),
                ("Core i9", "13900"),
                ("Core i9", "13900F"),
                ("Core i9", "13900K"),
                ("Core i9", "13900KF"),
                ("Core i9", "13900KS"),
            ],
            "14th Gen Core": [
                ("Core i3", "14100"),
                ("Core i3", "14100F"),
                ("Core i5", "14400"),
                ("Core i5", "14400F"),
                ("Core i5", "14500"),
                ("Core i5", "14600K"),
                ("Core i5", "14600KF"),
                ("Core i7", "14700"),
                ("Core i7", "14700F"),
                ("Core i7", "14700K"),
                ("Core i7", "14700KF"),
                ("Core i9", "14900"),
                ("Core i9", "14900F"),
                ("Core i9", "14900K"),
                ("Core i9", "14900KF"),
                ("Core i9", "14900KS"),
            ],
        },
        "LGA1851": {
            "Core Ultra Series 2": [
                ("Core Ultra 5", "225"),
                ("Core Ultra 5", "225F"),
                ("Core Ultra 5", "235"),
                ("Core Ultra 5", "245"),
                ("Core Ultra 5", "245K"),
                ("Core Ultra 5", "245KF"),
                ("Core Ultra 7", "265"),
                ("Core Ultra 7", "265F"),
                ("Core Ultra 7", "265K"),
                ("Core Ultra 7", "265KF"),
                ("Core Ultra 9", "285"),
                ("Core Ultra 9", "285K"),
            ],
        },
    },
}

CPU_ACCESSORY_OR_UNCOMPARABLE_TERMS = [
    "box only",
    "empty box",
    "cooler only",
    "heatsink only",
    "heat sink only",
    "fan only",
    "replacement fan",
    "water block",
    "waterblock",
    "motherboard",
    "mainboard",
    "mobo",
    "cpu motherboard combo",
    "motherboard combo",
    "combo kit",
    "bundle",
    "gaming pc",
    "desktop computer",
    "complete computer",
    "complete pc",
    "mini pc",
    "laptop",
    "notebook",
    "keychain",
    "display model",
    "coaster",
    "sticker",
    "gold recovery",
    "scrap",
]

CPU_UNSAFE_TERMS = [
    "engineering sample",
    "qualification sample",
    "confidential",
    "intel confidential",
    "es cpu",
    "qs cpu",
    "delidded",
    "delid",
    "bent pin",
    "bent pins",
    "missing pin",
    "missing pins",
    "pin repair",
    "damaged pins",
    "cracked substrate",
]

CPU_LOT_PATTERNS = [
    r"\blot\s+of\s+\d+\b",
    r"\bqty\s*[:x-]?\s*[2-9]\d*\b",
    r"\b[2-9]\d*\s*(?:pcs?|pieces?|processors?|cpus?)\b",
    r"\bpair\s+of\b",
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _tier_alias(tier: str) -> str:
    if tier.startswith("Core i"):
        return tier.replace("Core ", "")
    return tier


@lru_cache(maxsize=1)
def cpu_catalog_products() -> list[Product]:
    products: list[Product] = []
    for manufacturer, sockets in CPU_FAMILIES.items():
        brand = "AMD" if manufacturer == "amd" else "Intel"
        for socket, generations in sockets.items():
            for generation, models in generations.items():
                for tier, code in models:
                    model = f"{tier} {code}"
                    aliases = [
                        model,
                        f"{brand} {model}",
                        f"{_tier_alias(tier)}-{code}" if tier.startswith("Core i") else f"{tier} {code}",
                        code,
                    ]
                    products.append(
                        Product(
                            id=f"cpu-{manufacturer}-{_slug(model)}",
                            category="cpus",
                            category_label="CPUs",
                            product_type="desktop_cpu",
                            brand=brand,
                            model=model,
                            aliases=list(dict.fromkeys(aliases)),
                            required_terms=[code],
                            excluded_terms=[],
                            metadata={
                                "builder": "cpus",
                                "manufacturer": manufacturer,
                                "socket": socket,
                                "generation": generation,
                                "tier": tier,
                                "model_code": code,
                                "provider_query": f"{brand} {model} CPU processor",
                            },
                        )
                    )
    return products


def cpu_provider_query(product: Product) -> str:
    value = product.metadata.get("provider_query")
    return str(value) if value else f"{product.display_name} CPU processor"


def _has_model_code(title: str, code: str) -> bool:
    match = re.fullmatch(r"(\d+)([A-Z0-9]*)", code.upper())
    if not match:
        return False
    number, suffix = match.groups()
    suffix_pattern = r"\s*[- ]?\s*" + re.escape(suffix) if suffix else ""
    return bool(
        re.search(
            rf"(?<![a-z0-9]){re.escape(number)}{suffix_pattern}(?![a-z0-9])",
            title,
            re.IGNORECASE,
        )
    )

def _mentioned_known_codes(title: str) -> set[str]:
    return {
        str(product.metadata.get("model_code"))
        for product in cpu_catalog_products()
        if _has_model_code(title, str(product.metadata.get("model_code")))
    }


def cpu_title_matches_product(title: str, product: Product) -> bool:
    code = str(product.metadata.get("model_code") or "").strip()
    tier = str(product.metadata.get("tier") or "").strip()
    manufacturer = str(product.metadata.get("manufacturer") or "").strip()
    if not code or not tier or not manufacturer:
        return False

    if any(has_term(title, term) for term in CPU_ACCESSORY_OR_UNCOMPARABLE_TERMS):
        return False
    if any(has_term(title, term) for term in CPU_UNSAFE_TERMS):
        return False
    if any(re.search(pattern, title, re.IGNORECASE) for pattern in CPU_LOT_PATTERNS):
        return False

    # Exact suffixes are exact products: 12700K must not accept 12700KF, and
    # 5800X3D must not accept 5800X or 5700X3D.
    if not _has_model_code(title, code):
        return False

    mentioned_codes = _mentioned_known_codes(title)
    if mentioned_codes - {code}:
        return False

    normalized = normalize_text(title, strip_filler=False)
    compact = compact_text(title, strip_filler=False)
    if manufacturer == "amd":
        if not ("amd" in normalized.split() or "ryzen" in normalized.split()):
            return False
        if "threadripper" in compact or "epyc" in compact:
            return False
    else:
        if tier.startswith("Core Ultra"):
            tier_number = tier.rsplit(" ", 1)[-1]
            if "ultra" not in normalized.split() or not has_term(title, tier_number):
                return False
        else:
            tier_alias = _tier_alias(tier).lower()
            if not (has_term(title, "intel") or has_term(title, tier_alias)):
                return False
        if any(has_term(title, term) for term in ["xeon", "celeron", "pentium"]):
            return False

    return True


def cpu_listing_rejection_reasons(title: str, product: Product) -> list[str]:
    if any(has_term(title, term) for term in CPU_ACCESSORY_OR_UNCOMPARABLE_TERMS):
        return ["CPU accessory/bundle/full system"]
    if any(has_term(title, term) for term in CPU_UNSAFE_TERMS):
        return ["CPU unsafe sample/damage"]
    if any(re.search(pattern, title, re.IGNORECASE) for pattern in CPU_LOT_PATTERNS):
        return ["CPU multi-item lot"]
    return [] if cpu_title_matches_product(title, product) else ["CPU model/suffix conflict"]
