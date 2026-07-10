import re


def normalize_text(value: str) -> str:
    value = value.lower()
    value = value.replace("geforce", "")
    value = value.replace("radeon", "")
    value = value.replace("nvidia", "")
    value = value.replace("amd", "")
    value = value.replace("intel", "")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text)
    normalized_term = normalize_text(term)
    return re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized) is not None
