import re

FILLER_WORDS = [
    "used",
    "new",
    "camera",
    "digital",
    "mirrorless",
    "dslr",
    "lens",
    "body",
    "only",
    "graphics",
    "card",
    "gpu",
]

ROMAN_NUMERALS = {
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
}


def normalize_text(value: str) -> str:
    value = value.lower()
    value = value.replace("f/", "f ")

    # Turn RTX3060 / RX6600XT / A7III / 24-70mm into token-friendly text.
    value = re.sub(r"([a-z])([0-9])", r"\1 \2", value)
    value = re.sub(r"([0-9])([a-z])", r"\1 \2", value)
    value = re.sub(r"(\d+)\s*(gb|mm)\b", r"\1\2", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    tokens = []
    for token in value.split():
        token = ROMAN_NUMERALS.get(token, token)
        if token not in FILLER_WORDS:
            tokens.append(token)
    return " ".join(tokens)


def compact_text(value: str) -> str:
    return normalize_text(value).replace(" ", "")


def has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)
    compact = compact_text(text)
    compact_term = compact_text(term)

    if not normalized_term:
        return False

    if re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized):
        return True

    return compact_term in compact
