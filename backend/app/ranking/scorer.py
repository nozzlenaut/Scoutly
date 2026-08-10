import re

from app.catalog.catalog import GLOBAL_BAD_LISTING_TERMS, listing_match_rejection_reasons
from app.catalog.normalizer import compact_text, has_term
from app.models.listing import Listing
from app.models.product import Product
from app.services.filter_rules import manual_filter_rejection_reasons

BAD_TITLE_WORDS = [
    *GLOBAL_BAD_LISTING_TERMS,
    "no display",
]

BAD_CONDITION_WORDS = [
    "defective",
    "for parts",
    "not working",
    "parts only",
    "repair",
    "untested",
    "as-is",
    "as is",
    "salvage",
    "no power",
]

REVIEW_WORDS = [
    "please read",
    "read description",
    "read desc",
    "see description",
    "read",
]

REVIEW_WARNING = "Seller asks you to review the description"

HARDWARE_DEFECT_PATTERNS = [
    ("bad fan", re.compile(r"\bbad\s+fans?\b", re.I)),
    ("fan issue", re.compile(r"\bfan\s+issues?\b", re.I)),
    ("overheating", re.compile(r"\boverheat(?:s|ing)?\b", re.I)),
    ("shuts off", re.compile(r"\bshuts?\s+off\b", re.I)),
    ("powers off", re.compile(r"\bpowers?\s+off\b", re.I)),
    ("power issue", re.compile(r"\bpower\s+issues?\b", re.I)),
    ("thermal issue", re.compile(r"\bthermal\s+issues?\b", re.I)),
    ("intermittent", re.compile(r"\bintermittent(?:ly)?\b", re.I)),
    ("repair needed", re.compile(r"\b(?:repairs?\s+(?:is\s+)?needed|needs?\s+repair)\b", re.I)),
    ("not fully functional", re.compile(r"\bnot\s+fully\s+functional\b", re.I)),
]

NEGATED_DEFECT_PREFIX = re.compile(
    r"(?:"
    r"\bno\s+(?:known\s+)?(?:signs?\s+of\s+)?|"
    r"\bwithout\s+(?:any\s+)?(?:signs?\s+of\s+)?|"
    r"\b(?:does|do|did|is|was|will)\s+not\s+|"
    r"\b(?:doesn|isn|wasn|won)['’]?t\s+|"
    r"\bnever\s+|"
    r"\b(?:tested|testing|checked|checking|inspected|inspecting|screened|screening)"
    r"\s+(?:it\s+)?(?:for|against)\s+"
    r")$",
    re.I,
)

TEST_ONLY_DEFECT_SUFFIX = re.compile(
    r"^(?:"
    r"\s+(?:test|testing|check|inspection)\b|"
    r"\s+(?:tested|checked|inspected)\b|"
    r"[\s:;,—-]+(?:none|not\s+(?:present|found|detected)|no\s+(?:issue|issues|problem|problems))\b"
    r")",
    re.I,
)

TEST_CONTEXT_START = re.compile(
    r"\b(?:tested|testing|checked|checking|inspected|inspecting|screened|screening)"
    r"\s+(?:it\s+)?(?:for|against)\s+",
    re.I,
)

TEST_CONTEXT_BREAK = re.compile(
    r"\b(?:but|however|although|yet|now|currently|found|shows?|developed|has|have|with|it)\b",
    re.I,
)


def _defect_mention_is_negated_or_test_only(text: str, match: re.Match[str]) -> bool:
    prefix = text[max(0, match.start() - 80) : match.start()]
    suffix = text[match.end() : match.end() + 50]
    if NEGATED_DEFECT_PREFIX.search(prefix) or TEST_ONLY_DEFECT_SUFFIX.search(suffix):
        return True

    clause_prefix = re.split(r"[.;:!?]", prefix)[-1]
    test_context = TEST_CONTEXT_START.search(clause_prefix)
    if test_context and not TEST_CONTEXT_BREAK.search(clause_prefix[test_context.end() :]):
        return True

    return False


def _hardware_defect_mentions(text: str | None) -> list[str]:
    if not text:
        return []

    mentions: list[str] = []
    for label, pattern in HARDWARE_DEFECT_PATTERNS:
        for match in pattern.finditer(text):
            if _defect_mention_is_negated_or_test_only(text, match):
                continue
            mentions.append(label)
            break
    return mentions


def _console_title_quality_adjustment(listing: Listing, product: Product | None) -> float:
    if product is None or product.category != "consoles":
        return 0

    adjustment = 0.0
    title = listing.title

    # Review-caveated listings may still be functional, so keep them eligible
    # but make a clean listing win even when it costs noticeably more.
    if any(has_term(title, word) for word in REVIEW_WORDS):
        adjustment -= 130

    if any(has_term(title, word) for word in ["tested", "working", "fully functional"]):
        adjustment += 30
    if any(has_term(title, word) for word in ["complete", "complete console", "full system"]):
        adjustment += 25
    if any(has_term(title, word) for word in ["console", "system", "handheld", "unit"]):
        adjustment += 15

    return adjustment


def _apply_review_warning(listing: Listing) -> bool:
    has_review_language = any(has_term(listing.title, word) for word in REVIEW_WORDS)
    if has_review_language and REVIEW_WARNING not in listing.warning_labels:
        listing.warning_labels.append(REVIEW_WARNING)
    return has_review_language


def rejection_reasons(listing: Listing, product: Product | None = None) -> list[str]:
    title = listing.title.lower()
    condition = listing.condition.lower()
    reasons: list[str] = []

    for word in BAD_TITLE_WORDS:
        if word in title:
            reasons.append(f"bad title term: {word}")
            break

    for word in BAD_CONDITION_WORDS:
        if word in condition:
            reasons.append(f"bad condition: {word}")
            break

    title_defects = _hardware_defect_mentions(listing.title)
    if title_defects:
        reasons.append(f"hardware defect in title: {title_defects[0]}")

    description_defects = _hardware_defect_mentions(listing.description)
    if description_defects:
        reasons.append(f"hardware defect in description: {description_defects[0]}")

    if product is not None and product.category == "gpus":
        for word in ["laptop", "notebook", "mobile"]:
            if has_term(listing.title, word):
                reasons.append(f"bad GPU form factor: {word}")
                break

    if (
        product is not None
        and product.category == "consoles"
        and (has_term(listing.title, "controller") or has_term(listing.title, "controllers"))
        and not has_term(listing.title, "console")
    ):
        reasons.append("controller listing without console evidence")

    if (
        product is not None
        and product.category == "consoles"
        and str(product.metadata.get("family") or "").lower() == "nintendo-wii"
        and "wiiu" in compact_text(listing.title, strip_filler=False)
    ):
        reasons.append("console model conflict: wii u")

    if listing.seller_feedback_score == 0:
        reasons.append("seller feedback score is zero")

    manual_reasons = manual_filter_rejection_reasons(listing.title, product)
    reasons.extend(manual_reasons)

    # eBay seller-defined variation groups can advertise a console/GPU parent
    # while the displayed price belongs to an accessory, lower-spec model, or
    # an explicit "no console" option. Exact-item categories reject them rather
    # than trusting the cheapest variation price.
    if (
        product is not None
        and product.category in {"consoles", "gpus", "ram", "cpus"}
        and (listing.item_group_type or "").upper() == "SELLER_DEFINED_VARIATIONS"
    ):
        reasons.append("seller-defined variation listing")

    if product is not None:
        reasons.extend(listing_match_rejection_reasons(listing.title, product))

    return reasons


def is_bad_listing(listing: Listing, product: Product | None = None) -> bool:
    return bool(rejection_reasons(listing, product))


def score_listing(listing: Listing, product: Product | None = None) -> float:
    """Higher is better. Price matters, but junk listings should never win."""
    if is_bad_listing(listing, product):
        return 0

    has_review_language = _apply_review_warning(listing)
    price_score = max(0, 500 - listing.total_price)
    seller_score = (listing.seller_rating if listing.seller_rating is not None else 88) * 0.45
    seller_feedback = listing.seller_feedback_score
    if seller_feedback is None:
        seller_score -= 12
    elif 1 <= seller_feedback <= 2:
        seller_score -= 55
    elif seller_feedback <= 5:
        seller_score -= 40
    elif seller_feedback <= 10:
        seller_score -= 24
    elif seller_feedback <= 25:
        seller_score -= 10
    elif seller_feedback >= 100:
        seller_score += 5

    if listing.seller_rating is not None:
        if listing.seller_rating < 95:
            seller_score -= 22
        elif listing.seller_rating < 98:
            seller_score -= 10

    condition_bonus = 15 if "used" in listing.condition.lower() else 5
    shipping_bonus = 10 if listing.shipping == 0 else 0
    product_match_bonus = 35 if product is not None else 0
    bundle_penalty = 15 if "Bundle / extras included" in listing.warning_labels else 0
    console_title_adjustment = _console_title_quality_adjustment(listing, product)
    review_penalty = 45 if has_review_language and (product is None or product.category != "consoles") else 0

    return round(
        price_score
        + seller_score
        + condition_bonus
        + shipping_bonus
        + product_match_bonus
        + console_title_adjustment
        - bundle_penalty
        - review_penalty,
        2,
    )


def top_listings(listings: list[Listing], product: Product | None = None, limit: int = 3) -> list[Listing]:
    valid_listings = [listing for listing in listings if not is_bad_listing(listing, product)]
    if not valid_listings:
        return []

    for listing in valid_listings:
        listing.score = score_listing(listing, product)

    deduped: list[Listing] = []
    seen: set[str] = set()
    for listing in sorted(valid_listings, key=lambda item: item.score, reverse=True):
        key = str(listing.url).split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(listing)
        if len(deduped) >= max(1, limit):
            break

    return deduped


def best_listing(listings: list[Listing], product: Product | None = None) -> Listing | None:
    top = top_listings(listings, product, limit=1)
    return top[0] if top else None
