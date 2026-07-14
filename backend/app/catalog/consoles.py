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
            elif self.model:
                base += f" {self.model.upper() if self.model == 'oled' else self.model.title()}"
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
            elif has_term(query, "standard"):
                model = "standard"
            if has_term(query, "digital"):
                edition = "digital"
            elif has_term(query, "disc") or has_term(query, "disk"):
                edition = "disc"
    elif "nintendo" in compact or "switch" in compact or "3ds" in compact:
        brand = "Nintendo"
        if "3dsxl" in compact or ("3ds" in compact and has_term(query, "xl")):
            family = "nintendo-3ds-xl"
        elif "switch" in compact:
            family = "nintendo-switch"
            if has_term(query, "oled"):
                model = "oled"
            elif has_term(query, "lite"):
                model = "lite"
            elif has_term(query, "standard") or has_term(query, "v1") or has_term(query, "v2"):
                model = "standard"
            # Switch 2 remains paused and must never fall back to Switch.
            if has_term(query, "switch 2") or "switch2" in compact:
                return None

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
        elif spec.model == "standard":
            model = "Switch Standard"
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
    "nintendo-switch": ("standard", "oled", "lite"),
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
    return str(value) if value else product.display_name


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
        if model == "standard" and (has_slim or has_pro):
            return False
        if edition == "digital" and not has_term(title, "digital"):
            return False
        if edition == "disc":
            if has_term(title, "digital") and not (has_term(title, "disc") or has_term(title, "disk")):
                return False
            if not (has_term(title, "disc") or has_term(title, "disk")):
                return False
        return True

    if family == "nintendo-switch":
        if "switch" not in compact or "switch2" in compact:
            return False
        is_oled = has_term(title, "oled")
        is_lite = has_term(title, "lite")
        if model == "oled" and not is_oled:
            return False
        if model == "lite" and not is_lite:
            return False
        if model == "standard" and (is_oled or is_lite):
            return False
        # Standard and OLED units need detachable controls/dock evidence.
        # Lite has integrated controls and does not need Joy-Con evidence.
        if not is_lite and not _switch_has_complete_controls(title):
            return False
        return True

    if family == "nintendo-3ds-xl":
        return "3dsxl" in compact and "2ds" not in compact

    return False
