import re
from dataclasses import dataclass

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch


@dataclass(frozen=True)
class ConsoleSpec:
    brand: str
    family: str
    model: str | None = None
    storage: str | None = None
    edition: str | None = None

    @property
    def canonical_query(self) -> str:
        if self.brand == "Xbox":
            base = "Xbox Series" if self.family == "xbox-series" else "Xbox One"
            if self.model:
                base = f"Xbox {self.model}"
        elif self.brand == "PlayStation":
            generation = "5" if self.family == "playstation-5" else "4"
            base = f"PlayStation {generation}"
            if self.model == "standard":
                base += " Standard"
            elif self.model:
                base += f" {self.model.title()}"
        elif self.family == "nintendo-switch":
            base = "Nintendo Switch"
            if self.model == "standard":
                base += " Standard"
            elif self.model == "switch2":
                base += " 2"
            elif self.model:
                base += f" {self.model.upper() if self.model == 'oled' else self.model.title()}"
        elif self.family == "nintendo-wii-u":
            base = "Nintendo Wii U"
        else:
            base = "Nintendo 3DS XL"

        if self.storage:
            base += f" {self.storage.upper()}"
        if self.edition == "disc":
            base += " Disc Edition"
        elif self.edition == "digital":
            base += " Digital Edition"
        return base

    @property
    def provider_query(self) -> str:
        # Avoid "Standard" in marketplace queries; it is a builder distinction,
        # not a term sellers reliably use. The title matcher enforces the scope.
        value = self.canonical_query.replace(" Standard", "")
        return f"{value} console"


_STORAGE_PATTERN = re.compile(r"(?<!\d)(512\s*gb|825\s*gb|1\s*tb|2\s*tb)(?!\d)", re.I)


def _raw_has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text, strip_filler=False)
    normalized_term = normalize_text(term, strip_filler=False)
    if not normalized_term:
        return False
    return bool(re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized))


def parse_console_query(query: str) -> ConsoleSpec | None:
    normalized = normalize_text(query, strip_filler=False)
    compact = compact_text(query, strip_filler=False)

    brand: str | None = None
    family: str | None = None
    model: str | None = None
    edition: str | None = None

    if "xbox" in compact:
        brand = "Xbox"
        if "series" in normalized or "seriesx" in compact or "seriess" in compact:
            family = "xbox-series"
            if has_term(query, "series x") or "seriesx" in compact:
                model = "Series X"
            elif has_term(query, "series s") or "seriess" in compact:
                model = "Series S"
        elif has_term(query, "xbox one") or "xboxone" in compact:
            family = "xbox-one"
            if has_term(query, "one x") or "onex" in compact:
                model = "One X"
            elif has_term(query, "one s") or "ones" in compact:
                model = "One S"
    elif "playstation" in compact or "ps5" in compact or "ps4" in compact:
        brand = "PlayStation"
        if "ps5" in compact or "playstation5" in compact:
            family = "playstation-5"
        elif "ps4" in compact or "playstation4" in compact:
            family = "playstation-4"
        if family:
            if has_term(query, "pro"):
                model = "pro"
            elif has_term(query, "slim"):
                model = "slim"
            else:
                # PS4 and PS5 are core models. Storage and Disc/Digital are
                # grouped variants rather than separate searchable products.
                model = "standard"
            if _raw_has_term(query, "digital") or "digitaledition" in compact:
                edition = "digital"
            elif _raw_has_term(query, "disc") or _raw_has_term(query, "disk"):
                edition = "disc"
    elif "nintendo" in compact or "switch" in compact or "3ds" in compact or "wiiu" in compact:
        brand = "Nintendo"
        if "3dsxl" in compact or ("3ds" in compact and has_term(query, "xl")):
            family = "nintendo-3ds-xl"
            model = "3ds-xl"
        elif "wiiu" in compact:
            family = "nintendo-wii-u"
            model = "wii-u"
        elif "switch" in compact:
            family = "nintendo-switch"
            if has_term(query, "switch 2") or "switch2" in compact:
                model = "switch2"
            elif has_term(query, "oled"):
                model = "oled"
            elif has_term(query, "lite"):
                model = "lite"
            else:
                # V1 and V2 are variants under the original Switch model.
                model = "standard"

    if not brand or not family:
        return None

    storage_match = _STORAGE_PATTERN.search(query)
    storage = re.sub(r"\s+", "", storage_match.group(1)).upper() if storage_match else None

    return ConsoleSpec(
        brand=brand,
        family=family,
        model=model,
        storage=storage,
        edition=edition,
    )


def _console_product_from_spec(spec: ConsoleSpec) -> Product:
    if spec.brand == "Xbox":
        model = "Series" if spec.family == "xbox-series" else "One"
        if spec.model:
            model = spec.model
    elif spec.brand == "PlayStation":
        model = "5" if spec.family == "playstation-5" else "4"
        if spec.model == "slim":
            model += " Slim"
        elif spec.model == "pro":
            model += " Pro"
        elif spec.model == "standard":
            model += " Standard"
    elif spec.family == "nintendo-switch":
        model = "Switch"
        if spec.model == "oled":
            model = "Switch OLED"
        elif spec.model == "lite":
            model = "Switch Lite"
        elif spec.model == "switch2":
            model = "Switch 2"
        elif spec.model == "standard":
            model = "Switch"
    elif spec.family == "nintendo-wii-u":
        model = "Wii U"
    else:
        model = "3DS XL"

    variant_parts: list[str] = []
    if spec.storage:
        variant_parts.append(spec.storage)
    if spec.edition == "disc":
        variant_parts.append("Disc Edition")
    elif spec.edition == "digital":
        variant_parts.append("Digital Edition")

    canonical = spec.canonical_query
    return Product(
        id=(
            "console-builder-"
            + re.sub(r"[^a-z0-9]+", "-", canonical.lower()).strip("-")
        ),
        category="consoles",
        category_label="Consoles",
        product_type="console_builder",
        brand=spec.brand,
        model=model,
        variant=" ".join(variant_parts) or None,
        aliases=[canonical],
        metadata={
            "builder": "consoles",
            "family": spec.family,
            "model_scope": spec.model,
            "storage": spec.storage,
            "edition": spec.edition,
            "provider_query": spec.provider_query,
        },
    )


def console_product_match(query: str) -> ProductMatch | None:
    spec = parse_console_query(query)
    if spec is None:
        return None

    product = _console_product_from_spec(spec)
    return ProductMatch(product=product, confidence=1.0, matched_alias=spec.canonical_query)


_FAMILY_MODEL_SCOPES: dict[str, tuple[str, ...]] = {
    "xbox-series": ("Series S", "Series X"),
    "xbox-one": ("One S", "One X"),
    "playstation-5": ("standard", "slim", "pro"),
    "playstation-4": ("standard", "slim", "pro"),
    "nintendo-switch": ("standard", "oled", "lite", "switch2"),
}

_MODEL_STORAGE_SUPPORT: dict[tuple[str, str], set[str]] = {
    ("xbox-series", "Series S"): {"512GB", "1TB"},
    ("xbox-series", "Series X"): {"1TB"},
    ("xbox-one", "One S"): {"1TB"},
    ("xbox-one", "One X"): {"1TB"},
    ("playstation-5", "standard"): {"825GB"},
    ("playstation-5", "slim"): {"1TB"},
    ("playstation-5", "pro"): {"2TB"},
}


def console_search_products(product: Product) -> list[Product]:
    """Expand an unrefined console family into exact model searches.

    A builder selection such as "Xbox Series" should not rely on one broad
    marketplace query. Each active model is searched independently, filtered
    with its own exact product rules, then merged by the search service.
    """
    if product.category != "consoles" or product.metadata.get("builder") != "consoles":
        return [product]

    family = str(product.metadata.get("family") or "")
    model_scope = product.metadata.get("model_scope")
    if model_scope or family not in _FAMILY_MODEL_SCOPES:
        return [product]

    storage = str(product.metadata.get("storage") or "") or None
    edition = str(product.metadata.get("edition") or "") or None
    expanded: list[Product] = []
    for model in _FAMILY_MODEL_SCOPES[family]:
        supported_storage = _MODEL_STORAGE_SUPPORT.get((family, model))
        if storage and supported_storage is not None and storage not in supported_storage:
            continue
        # PS5 Pro does not expose a builder-level disc-edition option. A disc
        # family search should cover the standard and slim disc models instead.
        if family == "playstation-5" and model == "pro" and edition == "disc":
            continue
        spec = ConsoleSpec(
            brand=product.brand,
            family=family,
            model=model,
            storage=storage,
            edition=edition,
        )
        expanded.append(_console_product_from_spec(spec))

    return expanded or [product]


def console_provider_query(product: Product) -> str:
    value = product.metadata.get("provider_query")
    return str(value) if value else f"{product.display_name} console"


def _is_standard_switch_product(product: Product) -> bool:
    family = str(product.metadata.get("family") or "").lower()
    model_scope = str(product.metadata.get("model_scope") or "").lower()
    product_identity = compact_text(
        f"{product.id} {product.brand} {product.model} {product.variant or ''}",
        strip_filler=False,
    )
    return (
        product.category == "consoles"
        and product.brand.lower() == "nintendo"
        and (
            (family == "nintendo-switch" and model_scope == "standard")
            or product.id in {"console-nintendo-switch", "console-nintendo-switch-v1-v2"}
            or (
                "switch" in product_identity
                and "switcholed" not in product_identity
                and "switchlite" not in product_identity
                and "switch2" not in product_identity
            )
        )
    )


def console_provider_queries(product: Product) -> list[str]:
    """Return every marketplace query needed for a console product scope.

    Standard Nintendo Switch sellers use inconsistent revision wording. Search
    V1, V2, both HAC model numbers, the builder's Standard label, and a generic
    console query, then let the exact title filters merge and deduplicate them.
    """
    if _is_standard_switch_product(product):
        return [
            "Nintendo Switch V1 console",
            "Nintendo Switch V2 console",
            "Nintendo Switch HAC-001 console",
            "Nintendo Switch HAC-001(-01) console",
            "Nintendo Switch Standard console",
            "Nintendo Switch console",
        ]
    return [console_provider_query(product)]


def _has_storage(title: str, storage: str) -> bool:
    compact = compact_text(title, strip_filler=False)
    return storage.lower() in compact


def _switch_has_complete_controls(title: str) -> bool:
    clues = [
        "joy con",
        "joy-con",
        "joycon",
        "with controller",
        "with controllers",
        "controller included",
        "controllers included",
        "with dock",
        "dock included",
        "complete",
        "complete set",
        "complete console",
        "full console",
        "full system",
        "console bundle",
        "system bundle",
    ]
    return any(has_term(title, clue) for clue in clues)


def _switch_has_standard_identity(title: str) -> bool:
    compact = compact_text(title, strip_filler=False)
    revision_clues = [
        "v1",
        "v2",
        "standard",
        "hac 001",
        "hac-001",
        "hac 001 01",
        "hac-001-01",
        "hac-001(-01)",
    ]
    has_revision = any(has_term(title, clue) for clue in revision_clues) or any(
        clue in compact for clue in ["hac001", "hac00101"]
    )
    has_console_identity = any(
        has_term(title, clue)
        for clue in ["console", "system", "complete console", "full system"]
    )
    return has_revision or has_console_identity or _switch_has_complete_controls(title)


def _console_title_has_hardware_evidence(title: str) -> bool:
    normalized = normalize_text(title, strip_filler=False)
    scrubbed = re.sub(r"\bconsole edition\b", "", normalized)
    scrubbed = re.sub(r"\bfor (?:the )?console\b", "", scrubbed)
    if re.search(r"\b(?:video game|gaming|complete|full) console\b", scrubbed):
        return True
    if re.search(r"\bconsole (?:system|unit|bundle|with|and)\b", scrubbed):
        return True
    if any(has_term(scrubbed, clue) for clue in ["system", "unit", "handheld", "tested", "working"]):
        return True
    if re.search(r"\b(?:32|64|256|500|512|825)\s*gb\b|\b(?:1|2)\s*tb\b", scrubbed):
        return True
    return False


def console_builder_title_matches_product(title: str, product: Product) -> bool:
    metadata = product.metadata
    family = str(metadata.get("family") or "")
    model = metadata.get("model_scope")
    storage = metadata.get("storage")
    edition = metadata.get("edition")
    compact = compact_text(title, strip_filler=False)

    if storage and not _has_storage(title, str(storage)):
        return False

    if family == "xbox-series":
        if "xbox" not in compact:
            return False
        if "xbox360" in compact or has_term(title, "xbox 360"):
            return False
        is_x = "seriesx" in compact
        is_s = "seriess" in compact
        if is_x == is_s:
            return False
        if model == "Series X" and not is_x:
            return False
        if model == "Series S" and not is_s:
            return False
        return "xboxone" not in compact and "onex" not in compact and "ones" not in compact

    if family == "xbox-one":
        if "xbox" not in compact or "xboxone" not in compact:
            return False
        is_x = "onex" in compact
        is_s = "ones" in compact
        if is_x == is_s:
            return False
        if model == "One X" and not is_x:
            return False
        if model == "One S" and not is_s:
            return False
        return "seriesx" not in compact and "seriess" not in compact

    if family in {"playstation-5", "playstation-4"}:
        generation = "5" if family.endswith("5") else "4"
        if f"ps{generation}" not in compact and f"playstation{generation}" not in compact:
            return False
        has_slim = has_term(title, "slim")
        has_pro = has_term(title, "pro")
        if model == "slim" and not has_slim:
            return False
        if model == "pro" and not has_pro:
            return False
        if model == "pro" and not _console_title_has_hardware_evidence(title):
            return False
        if model == "standard" and (has_slim or has_pro):
            return False
        title_has_digital = _raw_has_term(title, "digital") or "digitaledition" in compact
        title_has_disc = _raw_has_term(title, "disc") or _raw_has_term(title, "disk")
        if edition == "digital":
            if not title_has_digital:
                return False
            if _raw_has_term(title, "disc edition") or _raw_has_term(title, "disk edition"):
                return False
        if edition == "disc":
            if title_has_digital and not title_has_disc:
                return False
            if not title_has_disc:
                return False
        return True

    if family == "nintendo-switch":
        if "switch" not in compact or "switch2" in compact:
            return False
        is_oled = has_term(title, "oled")
        is_lite = has_term(title, "lite")
        is_heg = "heg001" in compact
        is_hac = "hac001" in compact
        if model == "oled" and not is_oled:
            return False
        if model == "lite" and not is_lite:
            return False
        if model == "standard" and (is_oled or is_lite or is_heg):
            return False
        if model == "switch2" and (is_oled or is_lite or is_heg or is_hac):
            return False
        # Standard Switch listings are inconsistently titled. Accept V1/V2,
        # HAC model codes, the word Standard, or normal console/system wording,
        # while the accessory detector still rejects tablet-only, dock-only,
        # Joy-Con-only, games, and other incomplete listings. OLED keeps the
        # stronger detachable-controls/dock evidence requirement.
        if model == "standard" and not _switch_has_standard_identity(title):
            return False
        if model == "oled" and not _switch_has_complete_controls(title):
            return False
        return True

    if family == "nintendo-3ds-xl":
        return "3dsxl" in compact and "2ds" not in compact

    return False
