import re
from dataclasses import dataclass

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch


RAM_SPEEDS = {
    "ddr3": {1066, 1333, 1600, 1866, 2133},
    "ddr4": {2133, 2400, 2666, 2933, 3000, 3200, 3600, 4000},
    "ddr5": {4800, 5200, 5600, 6000, 6400, 6800, 7200, 7600, 8000},
}

RAM_BRANDS = {
    "corsair": ["corsair"],
    "g.skill": ["g skill", "gskill", "g.skill"],
    "kingston": ["kingston", "kingston fury", "fury beast", "fury impact"],
    "crucial": ["crucial"],
    "teamgroup": ["teamgroup", "team group", "t force", "t-force", "t create", "t-create"],
    "samsung": ["samsung"],
    "sk hynix": ["sk hynix", "hynix"],
    "micron": ["micron"],
    "patriot": ["patriot", "viper"],
    "adata": ["adata", "xpg"],
}

PC_SPEED_EQUIVALENTS = {
    ("ddr3", 1066): ["pc3 8500", "pc3-8500"],
    ("ddr3", 1333): ["pc3 10600", "pc3-10600"],
    ("ddr3", 1600): ["pc3 12800", "pc3-12800"],
    ("ddr3", 1866): ["pc3 14900", "pc3-14900"],
    ("ddr3", 2133): ["pc3 17000", "pc3-17000"],
    ("ddr4", 2133): ["pc4 17000", "pc4-17000"],
    ("ddr4", 2400): ["pc4 19200", "pc4-19200"],
    ("ddr4", 2666): ["pc4 21300", "pc4-21300"],
    ("ddr4", 2933): ["pc4 23400", "pc4-23400"],
    ("ddr4", 3000): ["pc4 24000", "pc4-24000"],
    ("ddr4", 3200): ["pc4 25600", "pc4-25600"],
    ("ddr4", 3600): ["pc4 28800", "pc4-28800"],
    ("ddr5", 4800): ["pc5 38400", "pc5-38400"],
    ("ddr5", 5200): ["pc5 41600", "pc5-41600"],
    ("ddr5", 5600): ["pc5 44800", "pc5-44800"],
    ("ddr5", 6000): ["pc5 48000", "pc5-48000"],
    ("ddr5", 6400): ["pc5 51200", "pc5-51200"],
}

RAM_ACCESSORY_OR_UNCLEAR_TERMS = [
    "assorted ram",
    "assorted memory",
    "mixed ram",
    "mixed memory",
    "mixed lot",
    "random ram",
    "random memory",
    "dummy ram",
    "dummy memory",
    "dummy module",
    "rgb enhancement kit",
    "light enhancement kit",
    "ram heatsink",
    "memory heatsink",
    "heat spreader only",
    "heatsink only",
    "empty box",
    "box only",
    "packaging only",
    "label only",
    "sticker only",
]


@dataclass(frozen=True)
class RamSpec:
    form_factor: str
    generation: str
    total_capacity_gb: int
    stick_count: int
    capacity_per_stick_gb: int
    speed_mts: int | None = None
    brand: str | None = None

    @property
    def form_factor_label(self) -> str:
        return "Desktop" if self.form_factor == "desktop" else "Laptop"

    @property
    def module_term(self) -> str:
        return "UDIMM" if self.form_factor == "desktop" else "SODIMM"

    @property
    def canonical_query(self) -> str:
        parts = [
            self.generation.upper(),
            self.form_factor_label,
            f"{self.total_capacity_gb}GB",
            f"{self.stick_count}x{self.capacity_per_stick_gb}GB",
        ]
        if self.speed_mts:
            parts.append(f"{self.speed_mts} MT/s")
        if self.brand:
            parts.append(self.brand)
        return " ".join(parts)

    @property
    def provider_query(self) -> str:
        parts = []
        if self.brand:
            parts.append(self.brand)
        parts.extend(
            [
                self.generation.upper(),
                f"{self.total_capacity_gb}GB",
                f"{self.stick_count}x{self.capacity_per_stick_gb}GB",
            ]
        )
        if self.speed_mts:
            parts.append(str(self.speed_mts))
        parts.extend([self.module_term, "RAM"])
        return " ".join(parts)


def _parse_brand(query: str) -> str | None:
    for brand, aliases in RAM_BRANDS.items():
        if any(has_term(query, alias) for alias in aliases):
            return brand.title() if brand != "g.skill" else "G.Skill"
    return None


def _parse_speed(query: str, generation: str) -> int | None:
    valid_speeds = RAM_SPEEDS[generation]
    values = {
        int(value)
        for value in re.findall(r"(?<!\d)(\d{4})(?:\s*(?:mhz|mt\s*/?\s*s|mts))?(?!\d)", query.lower())
        if int(value) in valid_speeds
    }
    if len(values) == 1:
        return next(iter(values))
    return None


def parse_ram_query(query: str) -> RamSpec | None:
    lowered = query.lower()
    compact = compact_text(query, strip_filler=False)

    generation = next((value for value in ["ddr3", "ddr4", "ddr5"] if value in compact), None)
    if generation is None:
        generation = next((f"ddr{number}" for number in [3, 4, 5] if f"pc{number}" in compact), None)
    if generation is None:
        return None

    laptop_clues = ["laptop", "notebook", "sodimm", "so dimm", "so-dimm"]
    desktop_clues = ["desktop", "udimm", "u dimm", "u-dimm"]
    has_laptop = any(has_term(query, clue) for clue in laptop_clues)
    has_desktop = any(has_term(query, clue) for clue in desktop_clues)
    if has_laptop == has_desktop:
        return None
    form_factor = "laptop" if has_laptop else "desktop"

    config_match = re.search(r"(?<!\d)(\d+)\s*[x×]\s*(\d+)\s*gb\b", lowered)
    if not config_match:
        config_match = re.search(r"(?<!\d)(\d+)\s*gb\s*[x×]\s*(\d+)(?!\d)", lowered)
        if config_match:
            capacity_per_stick = int(config_match.group(1))
            stick_count = int(config_match.group(2))
        else:
            return None
    else:
        stick_count = int(config_match.group(1))
        capacity_per_stick = int(config_match.group(2))

    total_capacity = stick_count * capacity_per_stick
    explicit_totals = [
        int(value)
        for value in re.findall(r"(?<![x×\d])(\d+)\s*gb\b", lowered)
        if int(value) != capacity_per_stick
    ]
    if explicit_totals and total_capacity not in explicit_totals:
        return None

    if stick_count < 1 or capacity_per_stick < 1 or total_capacity > 512:
        return None

    speed = _parse_speed(query, generation)
    brand = _parse_brand(query)
    return RamSpec(
        form_factor=form_factor,
        generation=generation,
        total_capacity_gb=total_capacity,
        stick_count=stick_count,
        capacity_per_stick_gb=capacity_per_stick,
        speed_mts=speed,
        brand=brand,
    )


def ram_product_match(query: str) -> ProductMatch | None:
    spec = parse_ram_query(query)
    if spec is None:
        return None

    variant = f"{spec.speed_mts} MT/s" if spec.speed_mts else None
    product = Product(
        id=(
            f"ram-{spec.form_factor}-{spec.generation}-{spec.total_capacity_gb}gb-"
            f"{spec.stick_count}x{spec.capacity_per_stick_gb}gb"
            + (f"-{spec.speed_mts}" if spec.speed_mts else "")
            + (f"-{re.sub(r'[^a-z0-9]+', '-', spec.brand.lower()).strip('-')}" if spec.brand else "")
        ),
        category="ram",
        category_label="RAM",
        product_type="memory_kit",
        brand=spec.brand or "",
        model=f"{spec.generation.upper()} {spec.form_factor_label} {spec.total_capacity_gb}GB {spec.stick_count}x{spec.capacity_per_stick_gb}GB",
        variant=variant,
        aliases=[spec.canonical_query],
        metadata={
            "builder": "ram",
            "form_factor": spec.form_factor,
            "generation": spec.generation,
            "total_capacity_gb": spec.total_capacity_gb,
            "stick_count": spec.stick_count,
            "capacity_per_stick_gb": spec.capacity_per_stick_gb,
            "speed_mts": spec.speed_mts,
            "brand": spec.brand,
            "provider_query": spec.provider_query,
        },
    )
    return ProductMatch(product=product, confidence=1.0, matched_alias=spec.canonical_query)


def ram_provider_query(product: Product) -> str:
    value = product.metadata.get("provider_query")
    return str(value) if value else product.display_name


def _contains_generation(title: str, generation: str) -> bool:
    compact = compact_text(title, strip_filler=False)
    number = generation[-1]
    return generation in compact or f"pc{number}" in compact


def _contains_conflicting_generation(title: str, generation: str) -> bool:
    return any(_contains_generation(title, other) for other in ["ddr3", "ddr4", "ddr5"] if other != generation)


def _is_non_ecc_title(title: str) -> bool:
    normalized = normalize_text(title, strip_filler=False)
    return "non ecc" in normalized or "no ecc" in normalized or "non-ecc" in title.lower()


def _has_selected_configuration(title: str, count: int, capacity: int) -> bool:
    lowered = title.lower()
    patterns = [
        rf"(?<!\d){count}\s*[x×]\s*{capacity}\s*gb\b",
        rf"(?<!\d){capacity}\s*gb\s*[x×]\s*{count}(?!\d)",
        rf"\b{count}\s*(?:pcs?|pieces?|pack)\s*(?:of\s*)?{capacity}\s*gb\b",
        rf"\b(?:kit|set)\s*(?:of\s*)?{count}\s*(?:x\s*)?{capacity}\s*gb\b",
    ]
    return any(re.search(pattern, lowered) for pattern in patterns)


def _conflicting_configurations(title: str, selected_count: int, selected_capacity: int) -> bool:
    lowered = title.lower()
    configurations: set[tuple[int, int]] = set()
    for count, capacity in re.findall(r"(?<!\d)(\d+)\s*[x×]\s*(\d+)\s*gb\b", lowered):
        configurations.add((int(count), int(capacity)))
    for capacity, count in re.findall(r"(?<!\d)(\d+)\s*gb\s*[x×]\s*(\d+)(?!\d)", lowered):
        configurations.add((int(count), int(capacity)))
    return any(config != (selected_count, selected_capacity) for config in configurations)


def ram_title_matches_product(title: str, product: Product) -> bool:
    metadata = product.metadata
    generation = str(metadata.get("generation") or "")
    form_factor = str(metadata.get("form_factor") or "")
    total_capacity = int(metadata.get("total_capacity_gb") or 0)
    stick_count = int(metadata.get("stick_count") or 0)
    capacity_per_stick = int(metadata.get("capacity_per_stick_gb") or 0)
    speed = metadata.get("speed_mts")
    brand = metadata.get("brand")

    if not generation or not form_factor or not total_capacity or not stick_count or not capacity_per_stick:
        return False

    if any(has_term(title, term) for term in RAM_ACCESSORY_OR_UNCLEAR_TERMS):
        return False

    if not _contains_generation(title, generation) or _contains_conflicting_generation(title, generation):
        return False

    normalized = normalize_text(title, strip_filler=False)
    compact = compact_text(title, strip_filler=False)

    # Consumer RAM only for the first builder release.
    server_terms = ["rdimm", "lrdimm", "registered", "server", "workstation", "buffered"]
    if any(term in compact or has_term(title, term) for term in server_terms):
        if "unbuffered" not in compact:
            return False
    if has_term(title, "ecc") and not _is_non_ecc_title(title):
        return False

    if form_factor == "laptop":
        positive = any(term in compact for term in ["sodimm", "laptop", "notebook"])
        conflicts = any(term in compact for term in ["udimm", "desktop", "rdimm", "lrdimm"])
    else:
        standalone_dimm = bool(re.search(r"\bdimm\b", normalized)) and not any(
            term in compact for term in ["sodimm", "rdimm", "lrdimm"]
        )
        positive = any(term in compact for term in ["udimm", "desktop"]) or standalone_dimm
        conflicts = any(term in compact for term in ["sodimm", "laptop", "notebook", "rdimm", "lrdimm"])
    if not positive or conflicts:
        return False

    if not _has_selected_configuration(title, stick_count, capacity_per_stick):
        return False
    if _conflicting_configurations(title, stick_count, capacity_per_stick):
        return False

    gb_values = {int(value) for value in re.findall(r"(?<!\d)(\d+)\s*gb\b", title.lower())}
    allowed_capacities = {total_capacity, capacity_per_stick}
    standard_capacities = {2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 256}
    if any(value in standard_capacities and value not in allowed_capacities for value in gb_values):
        return False

    if stick_count > 1 and any(
        has_term(title, term)
        for term in ["single stick", "one stick", "1 stick", "single module", "one module", "module only"]
    ):
        return False

    if speed:
        speed_value = int(speed)
        speed_clues = [str(speed_value), *PC_SPEED_EQUIVALENTS.get((generation, speed_value), [])]
        if not any(has_term(title, clue) for clue in speed_clues):
            return False

    if brand:
        aliases = RAM_BRANDS.get(str(brand).lower(), [str(brand)])
        if not any(has_term(title, alias) for alias in aliases):
            return False

    return True
