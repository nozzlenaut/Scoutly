import re

BRAND_WORDS = ["geforce", "radeon", "nvidia", "amd", "intel", "graphics", "card", "gpu"]


def normalize_text(value: str) -> str:
    value = value.lower()
    for word in BRAND_WORDS:
        value = re.sub(rf"\b{re.escape(word)}\b", " ", value)

    # Turn RTX3060 / RX6600XT / A77016GB into token-friendly text.
    value = re.sub(r"([a-z])([0-9])", r"\1 \2", value)
    value = re.sub(r"([0-9])([a-z])", r"\1 \2", value)
    value = re.sub(r"(\d+)\s*(gb)\b", r"\1gb", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def compact_text(value: str) -> str:
    return normalize_text(value).replace(" ", "")


def has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)
    compact = compact_text(text)
    compact_term = compact_text(term)

    if not normalized_term:
        return False

    # Direct token match covers normal terms like "3060", "ti", "12gb".
    if re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized):
        return True

    # Compact match covers terms like "rtx3060" and "a77016gb".
    return compact_term in compact
