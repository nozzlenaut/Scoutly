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


def normalize_text(value: str, *, strip_filler: bool = True) -> str:
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
        if strip_filler and token in FILLER_WORDS:
            continue
        tokens.append(token)
    return " ".join(tokens)


def compact_text(value: str, *, strip_filler: bool = True) -> str:
    return normalize_text(value, strip_filler=strip_filler).replace(" ", "")


def _exact_normalized_match(normalized: str, normalized_term: str) -> bool:
    return bool(re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized))


def has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)
    compact = compact_text(text)
    compact_term = compact_text(term)

    if not normalized_term:
        return False

    raw_normalized = normalize_text(text, strip_filler=False)
    raw_normalized_term = normalize_text(term, strip_filler=False)
    raw_compact = compact_text(text, strip_filler=False)
    raw_compact_term = compact_text(term, strip_filler=False)

    # If a multi-word phrase loses important filler words such as "only",
    # "gpu", or "lens" during normalization, treat it as a phrase. Otherwise
    # terms like "fan only" collapse to "fan" and reject valid dual-fan GPUs.
    term_token_count = len(raw_normalized_term.split())
    stripped_token_count = len(normalized_term.split())
    lost_filler_context = term_token_count > 1 and stripped_token_count < term_token_count
    if lost_filler_context:
        if _exact_normalized_match(raw_normalized, raw_normalized_term):
            return True
        return len(raw_compact_term) >= 3 and raw_compact_term in raw_compact

    if _exact_normalized_match(normalized, normalized_term):
        return True

    # Numeric search terms should match unit-attached listing tokens such as
    # 85mm and 12GB without making every short word use compact substring logic.
    if normalized_term.isdigit() and re.search(rf"(^|\s){re.escape(normalized_term)}(mm|gb)?($|\s)", normalized):
        return True

    # Compact matching is useful for terms like RTX4070Ti, A7III, RX6700XT,
    # G2, and LEGO set-number aliases. It is too broad for tiny text-only
    # modifier terms like "ti" because it can match "edition" or "condition".
    compact_has_letter = any(char.isalpha() for char in compact_term)
    compact_has_digit = any(char.isdigit() for char in compact_term)
    compact_safe = len(compact_term) >= 3 or (compact_has_letter and compact_has_digit)
    if not compact_safe:
        return False

    return compact_term in compact
