import json
import re
from functools import lru_cache
from pathlib import Path

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "product_catalog.json"

GLOBAL_BAD_LISTING_TERMS = [
    "as is",
    "as-is",
    "box only",
    "broken",
    "camera error",
    "damaged",
    "does not work",
    "error please read",
    "for parts",
    "not working",
    "parts only",
    "please read",
    "read description",
    "repair",
    "spares",
    "untested",
]

LENS_PART_ACCESSORY_TERMS = [
    "adapter only",
    "adapter ring",
    "bayonet mount",
    "bayonet ring",
    "cap only",
    "case only",
    "decal",
    "decoration ring",
    "decorative ring",
    "filter only",
    "filter ring",
    "focus gear",
    "gear ring",
    "hood only",
    "metal ring",
    "lens cap",
    "lens cap only",
    "lens coat",
    "lens cover",
    "lens hood",
    "lens hood only",
    "lens protector",
    "lens skin",
    "mount ring",
    "rear bayonet",
    "rear mount",
    "rubber grip",
    "rubber ring",
    "rear cap",
    "rear cap only",
    "ring gear",
    "skin",
    "step down ring",
    "step up ring",
    "step-down ring",
    "step-up ring",
    "tripod collar only",
]

GPU_PART_ACCESSORY_TERMS = [
    "artifacting",
    "artifacts",
    "backplate only",
    "bracket only",
    "cooler only",
    "cooling fan",
    "fan only",
    "gpu cooler",
    "gpu fan",
    "mining rig",
    "no display",
    "replacement fan",
    "replacement heatsink",
    "shroud only",
    "water block",
    "waterblock",
]

LENS_SAFE_CONTEXT_TERMS = {"aperture ring", "focus ring", "zoom ring"}

CAMERA_BODY_BUNDLE_TERMS = [
    "kit lens",
    "lens kit",
    "w/ lens",
    "with lens",
]

# LEGO complete-set listings often mention normal context like
# "with instructions" or "manual included". Do not reject those broad
# words by themselves; the LEGO-specific detector below rejects
# instructions-only/manual-only listings.
LEGO_SAFE_CONTEXT_TERMS = {"instructions", "instruction book", "manual"}

LEGO_INCOMPLETE_OR_PART_TERMS = [
    "partial",
    "partial build",
    "partial lot",
    "incomplete",
    "not complete",
    "missing piece",
    "missing pieces",
    "missing minifig",
    "missing minifigs",
    "missing minifigure",
    "missing minifigures",
    "minifigures not included",
    "minifigs not included",
    "no minifig",
    "no minifigs",
    "no minifigure",
    "no minifigures",
    "no figures",
    "figure only",
    "minifig only",
    "minifigure only",
    "minifigures only",
    "parts lot",
    "parts only",
    "pieces only",
    "spare pieces only",
    "spare lego pieces only",
    "just pieces",
]

LEGO_INSTRUCTIONS_OR_BOX_ONLY_TERMS = [
    "box only",
    "empty box",
    "box + instructions only",
    "box and instructions only",
    "instructions only",
    "instruction book only",
    "building instructions only",
    "manual only",
]

LEGO_ACCESSORY_TERMS = [
    "acrylic case",
    "display case",
    "light kit",
    "led kit",
    "lighting kit",
    "replacement stickers",
    "sticker sheet only",
    "stickers only",
    "storage case",
    "zip bin",
]

LEGO_CHARACTER_ONLY_TERMS = [
    "han solo",
    "chewbacca",
    "princess leia",
    "luke skywalker",
    "darth vader",
    "finn",
    "rey",
    "poe dameron",
    "r2-d2",
    "c-3po",
    "stormtrooper",
    "clone trooper",
    "minifigure",
    "minifig",
]


CAMERA_PART_ACCESSORY_TERMS = [
    "accessories only",
    "accessory kit",
    "accessory only",
    "adapter",
    "battery charger bundle",
    "battery door",
    "button",
    "cable",
    "camera accessories",
    "circuit board",
    "contact flex",
    "cover",
    "dial",
    "display screen",
    "door cover",
    "dummy",
    "filter",
    "lens filter",
    "uv filter",
    "cpl filter",
    "nd filter",
    "variable nd",
    "polarizer",
    "polarizing filter",
    "clear filter",
    "protection filter",
    "flex",
    "flex cable",
    "hot shoe",
    "lcd",
    "lens bayonet",
    "lens mount",
    "lens mount contact",
    "main board",
    "mount ring",
    "motherboard",
    "pcb",
    "port cover",
    "repair part",
    "replacement",
    "replacement part",
    "ribbon",
    "screen repair",
    "sensor cleaning",
    "spare part",
    "strap lug",
    "top cover",
    "viewfinder",
]


def _has_any_term(text: str, terms: list[str]) -> bool:
    return any(has_term(text, term) for term in terms)


def _looks_like_gpu_accessory(title: str, product: Product | None = None) -> bool:
    normalized = normalize_text(title)
    raw = title.lower()

    if product is not None:
        product_name = normalize_text(product.display_name)
        disallowed_server_form_factors = [
            "sxm",
            "sxm2",
            "sxm3",
            "sxm4",
            # Common seller typo for SXM/SXM2 modules.
            "smx",
            "smx2",
            "smx3",
            "smx4",
            "mezzanine",
            "module",
        ]
        is_normal_tesla_pcie_search = (
            product.category == "gpus"
            and (has_term(product_name, "tesla p100") or has_term(product_name, "tesla v100"))
            and not any(has_term(product_name, term) for term in disallowed_server_form_factors)
        )
        if is_normal_tesla_pcie_search and _has_any_term(title, disallowed_server_form_factors):
            return True

    if _has_any_term(title, GPU_PART_ACCESSORY_TERMS):
        return True

    explicit_heatsink_only = [
        "heatsink only",
        "heat sink only",
        "only heatsink",
        "only heat sink",
        "gpu heatsink",
        "gpu heat sink",
    ]
    if any(term in raw for term in explicit_heatsink_only):
        return True

    # Data-center GPUs can legitimately mention passive cooling or a heatsink,
    # but accessory listings usually sell only the cooler/heatsink/fan assembly.
    # Catch those without rejecting real cards like "Tesla V100 16GB PCIe GPU".
    accessory_words = [
        "adapter",
        "bracket",
        "cooler",
        "fan",
        "heat sink",
        "heatsink",
        "mount",
        "replacement",
        "screw",
        "shroud",
        "water block",
        "waterblock",
    ]
    if normalized.startswith("for ") and _has_any_term(title, accessory_words):
        return True

    if has_term(title, "heatsink") or has_term(title, "heat sink"):
        strong_card_words = ["graphics card", "video card", "gpu card", "accelerator", "pcie", "pci-e"]
        memory_words = ["8gb", "12gb", "16gb", "20gb", "24gb", "32gb", "40gb", "48gb", "80gb"]
        if not _has_any_term(title, strong_card_words + memory_words):
            return True

    return False


def _looks_like_lens_accessory(title: str) -> bool:
    normalized = normalize_text(title)
    if _has_any_term(title, LENS_PART_ACCESSORY_TERMS):
        return True

    # Many eBay accessory/repair-part titles include the real lens model but
    # describe replacement rings, rubber grips, or bayonet mounts. Those should
    # never beat a real used lens listing.
    if has_term(title, "ring") and _has_any_term(title, ["rubber", "metal", "bayonet", "mount", "replacement"]):
        return True

    if has_term(title, "bayonet") and _has_any_term(title, ["mount", "rear", "ring", "replacement"]):
        return True

    accessory_words = [
        "adapter",
        "bayonet",
        "coat",
        "cover",
        "gear",
        "mount",
        "protector",
        "replacement",
        "ring",
        "rubber",
        "skin",
    ]
    return normalized.startswith("for ") and _has_any_term(title, accessory_words)


def _looks_like_camera_body_accessory(title: str) -> bool:
    normalized = normalize_text(title)
    if _has_any_term(title, CAMERA_PART_ACCESSORY_TERMS):
        return True

    # Marketplace accessory listings often start with "for Sony/Canon/etc."
    # Legitimate camera bodies usually start with the product name itself.
    # Only use the prefix as a reject signal when the title also has accessory
    # words so we do not reject a rare legitimate title just because it says "for".
    accessory_words = ["bayonet", "mount", "ring", "contact", "part", "repair", "cable"]
    return normalized.startswith("for ") and _has_any_term(title, accessory_words)


def _looks_like_lego_bundle_or_multi_set(title: str, product: Product) -> bool:
    set_number = str(product.metadata.get("set_number") or product.variant or "").strip()
    if not set_number:
        return False

    if _has_any_term(title, LEGO_INCOMPLETE_OR_PART_TERMS):
        return True

    if _has_any_term(title, LEGO_INSTRUCTIONS_OR_BOX_ONLY_TERMS):
        return True

    if _has_any_term(title, LEGO_ACCESSORY_TERMS):
        return True

    clearly_full_set = _has_any_term(
        title,
        ["complete", "complete set", "sealed", "new in box", "with box", "building kit"],
    )

    # A lone minifigure/person listing can reference the parent set number.
    # Do not reject complete sets that mention included minifigures, but reject
    # character/minifigure-style titles that are not clearly full-set listings.
    if _has_any_term(title, LEGO_CHARACTER_ONLY_TERMS) and not clearly_full_set:
        return True

    # Mentions of manuals/instructions are fine when the title also says the set
    # is complete. Otherwise, sellers often list only manuals or partial bags.
    if _has_any_term(title, ["manual", "instructions", "instruction book"]) and not clearly_full_set:
        return True

    # If a title says "parts to <set>" or "pieces to <set>", it is not the set.
    if _has_any_term(title, ["parts to", "pieces to"]):
        return True

    # If a listing title includes the requested set plus other modern 5-digit
    # LEGO set numbers, it is usually a bundle/lot rather than the exact item.
    # Example: "75192 75376 75383 75386" should not win for 75192.
    found_set_numbers = set(re.findall(r"(?<!\d)\d{5}(?!\d)", title))
    other_set_numbers = found_set_numbers - {set_number}
    if set_number in found_set_numbers and other_set_numbers:
        return True

    # Be conservative around obvious bundles/lots when another set-like number
    # appears, while still allowing normal exact-set titles like "complete set".
    if _has_any_term(title, ["bundle", "lot", "multiple sets"]) and other_set_numbers:
        return True

    return False


def _lego_title_matches_product(title: str, product: Product) -> bool:
    set_number = str(product.metadata.get("set_number") or product.variant or "").strip()
    if set_number and has_term(title, set_number):
        return True

    # Some legitimate eBay titles omit the set number but include the exact model
    # name plus a complete-set clue. Allow those so UCS/Botanical listings do
    # not disappear just because the seller left the number out.
    model_terms = [term for term in normalize_text(product.model).split() if term not in {"lego", "star", "wars", "the", "and", "of"}]
    if len(model_terms) < 2:
        return False

    model_hits = sum(1 for term in model_terms if has_term(title, term))
    return model_hits == len(model_terms) and _has_any_term(title, ["complete", "complete set", "sealed", "new in box"])

def _camera_alias_matches_title(candidate: str, title: str, title_has_brand: bool) -> bool:
    """Match compact camera aliases without letting A7R3 match A7R36.4MP."""

    candidate_normalized = normalize_text(candidate)
    title_normalized = normalize_text(title)
    if candidate_normalized and re.search(rf"(^|\s){re.escape(candidate_normalized)}($|\s)", title_normalized):
        return True

    candidate_compact = compact_text(candidate)
    title_compact = compact_text(title)
    if not candidate_compact:
        return False

    # Compact matching catches eBay titles like "A7RIII" and "A7R3", but it
    # must not treat "A7R 36.4MP" as A7R III simply because the compact text
    # contains the substring "a7r3" inside "a7r364".
    for match in re.finditer(re.escape(candidate_compact), title_compact):
        next_char = title_compact[match.end() : match.end() + 1]
        if next_char.isdigit():
            continue

        # Short aliases such as "a73" or "a7r3" are only safe when the title
        # also names the brand. Longer aliases include enough context.
        if len(candidate_compact) >= 5 or title_has_brand:
            return True

    return False


def _has_camera_model_alias(title: str, product: Product) -> bool:
    """Require a strong camera model clue so nearby Alpha bodies do not cross-match."""

    title_has_brand = has_term(title, product.brand)
    candidates = [product.display_name, product.model, *product.aliases]
    return any(_camera_alias_matches_title(candidate, title, title_has_brand) for candidate in candidates)

CATEGORY_ALIASES = {
    "gpu": "gpus",
    "graphics": "gpus",
    "graphics-cards": "gpus",
    "camera": "cameras",
    "camera-body": "cameras",
    "camera-bodies": "cameras",
    "lens": "lenses",
    "lego": "lego",
    "legos": "lego",
    "lego-set": "lego",
    "lego-sets": "lego",
    "sets": "lego",
}


def normalize_category(category: str | None) -> str | None:
    if category is None:
        return None
    cleaned = category.strip().lower()
    return CATEGORY_ALIASES.get(cleaned, cleaned)


@lru_cache(maxsize=1)
def load_products() -> list[Product]:
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        raw_products = json.load(file)
    return [Product(**item) for item in raw_products if item.get("active", True)]


def list_products(category: str | None = None) -> list[Product]:
    products = load_products()
    normalized_category = normalize_category(category)
    if normalized_category is None:
        return products
    return [product for product in products if product.category.lower() == normalized_category]


def _score_product_candidate(query: str, product: Product) -> ProductMatch | None:
    normalized_query = normalize_text(query)
    compact_query = compact_text(query)
    best_confidence = 0.0
    best_alias: str | None = None

    candidates = [product.display_name, product.model, *product.aliases]
    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)
        compact_candidate = compact_text(candidate)
        if not normalized_candidate:
            continue

        confidence = 0.0
        if normalized_query == normalized_candidate or compact_query == compact_candidate:
            confidence = 1.0
        elif normalized_candidate.startswith(normalized_query) or compact_candidate.startswith(compact_query):
            confidence = 0.94
        elif normalized_query in normalized_candidate or compact_query in compact_candidate:
            confidence = 0.88
        elif normalized_candidate in normalized_query or compact_candidate in compact_query:
            confidence = 0.86
        else:
            required_hits = sum(1 for term in product.required_terms if has_term(normalized_query, term))
            if product.required_terms and required_hits == len(product.required_terms):
                confidence = 0.82
            elif required_hits >= 2:
                confidence = 0.62
            elif required_hits > 0:
                confidence = 0.44

        # Exact variant/mount/focal clues should help, without making them mandatory.
        if product.variant and has_term(normalized_query, product.variant):
            confidence = min(1.0, confidence + 0.04)

        product_text = normalize_text(f"{product.model} {product.variant or ''}")

        # For GPUs, prefer the base card when the user types only the number.
        gpu_modifiers = ["ti", "super", "xtx", "xt", "gre"]
        if product.category == "gpus" and any(
            has_term(product_text, modifier) and not has_term(normalized_query, modifier) for modifier in gpu_modifiers
        ):
            confidence = max(0.0, confidence - 0.07)

        # For versioned lenses, do not let GM II / VR II entries beat the
        # original product when the user did not type the version clue.
        # We avoid has_term() here because roman numeral II normalizes to "2",
        # which would falsely match aperture terms like f/2.8.
        raw_query = query.lower()
        raw_product = f"{product.model} {product.variant or ''}".lower()
        lens_versioned = product.category == "lenses" and any(
            marker in raw_product for marker in [" ii", " iii", " iv", " v"]
        )
        query_has_version = any(
            marker in raw_query for marker in [" ii", " iii", " iv", " v", "gm2", "gm 2", "g2"]
        )
        if lens_versioned and not query_has_version:
            confidence = max(0.0, confidence - 0.05)

        if confidence > best_confidence:
            best_confidence = confidence
            best_alias = candidate

    if best_confidence <= 0:
        return None
    return ProductMatch(product=product, confidence=round(best_confidence, 2), matched_alias=best_alias)


def match_product(query: str, category: str | None = None) -> ProductMatch | None:
    matches = suggest_products(query, category=category, limit=1)
    if not matches:
        return None
    best_match = matches[0]
    if best_match.confidence < 0.7:
        return None
    return best_match


def suggest_products(query: str, category: str | None = None, limit: int = 8) -> list[ProductMatch]:
    if len(query.strip()) < 2:
        return []

    matches: list[ProductMatch] = []
    for product in list_products(category):
        match = _score_product_candidate(query, product)
        if match is not None and match.confidence >= 0.42:
            matches.append(match)

    matches.sort(
        key=lambda match: (
            match.confidence,
            match.product.category,
            match.product.display_name,
        ),
        reverse=True,
    )
    return matches[:limit]


def listing_matches_product(title: str, product: Product) -> bool:
    if _has_any_term(title, GLOBAL_BAD_LISTING_TERMS):
        return False

    for excluded_term in product.excluded_terms:
        # Real lens condition notes often say things like "smooth focus ring".
        # Do not reject those broad terms by themselves; the lens accessory
        # detector below catches actual rubber rings, bayonet rings, and gears.
        if product.category == "lenses" and excluded_term in LENS_SAFE_CONTEXT_TERMS:
            continue
        if product.category == "lego" and excluded_term in LEGO_SAFE_CONTEXT_TERMS:
            continue
        if has_term(title, excluded_term):
            return False

    if product.category == "gpus" and _looks_like_gpu_accessory(title, product):
        return False

    if product.category == "lenses" and _looks_like_lens_accessory(title):
        return False

    if product.category == "cameras" and product.product_type == "camera_body":
        if _looks_like_camera_body_accessory(title):
            return False
        if product.variant and product.variant.lower() == "body" and _has_any_term(title, CAMERA_BODY_BUNDLE_TERMS):
            return False
        return _has_camera_model_alias(title, product)

    if product.category == "cameras" and _has_any_term(title, CAMERA_PART_ACCESSORY_TERMS):
        return False

    if product.category == "lego":
        if _looks_like_lego_bundle_or_multi_set(title, product):
            return False
        return _lego_title_matches_product(title, product)

    return all(has_term(title, required_term) for required_term in product.required_terms)
