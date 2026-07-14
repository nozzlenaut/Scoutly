import json
import re
from functools import lru_cache
from pathlib import Path

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch
from app.catalog.ram import ram_product_match, ram_title_matches_product
from app.catalog.consoles import console_builder_title_matches_product, parse_console_query

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "product_catalog.json"

GLOBAL_BAD_LISTING_TERMS = [
    "as is",
    "as-is",
    "box only",
    "box & insert only",
    "box and insert only",
    "box inserts only",
    "inserts only",
    "broken",
    "camera error",
    "damaged",
    "does not work",
    "error please read",
    "for parts",
    "not working",
    "parts only",
    "local pickup only",
    "local pick up only",
    "pickup only",
    "pick up only",
    "repair",
    "salvage",
    "no power",
    "service",
    "spares",
    "untested",
]

REVIEW_ONLY_TITLE_TERMS = [
    "read",
    "read desc",
    "read description",
    "see description",
    "please read",
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
    "core only",
    "chip only",
    "gpu core",
    "graphics processor only",
    "fan only",
    "gpu cooler",
    "gpu fan",
    "fan missing",
    "missing fan",
    "fan problem",
    "fan problems",
    "fan issue",
    "fan issues",
    "fan not working",
    "fan does not work",
    "single fan missing",
    "missing fans",
    "no cooler",
    "no heatsink",
    "no heat sink",
    "shell only",
    "1x fan missing",
    "one fan missing",
    "mining rig",
    "no display",
    "replacement fan",
    "replacement heatsink",
    "shroud only",
    "water block",
    "waterblock",
    "parts",
    "failed",
    "port failed",
    "ports failed",
    "dead port",
    "dead ports",
    "displayport failed",
    "display port failed",
    "hdmi failed",
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
    "missing fig",
    "missing figs",
    "missing figure",
    "missing figures",
    "missing 1 fig",
    "missing one fig",
    "missing 1 figure",
    "missing one figure",
    "minifigures not included",
    "minifigs not included",
    "no minifig",
    "no minifigs",
    "no minifigure",
    "no minifigures",
    "without minifig",
    "without minifigs",
    "without minifigure",
    "without minifigures",
    "no fig",
    "no figs",
    "no figure",
    "no figures",
    "figure only",
    "minifig only",
    "minifigure only",
    "minifigures only",
    "fig only",
    "figs only",
    "figure only",
    "figures only",
    "parts lot",
    "parts only",
    "pieces only",
    "spare pieces only",
    "spare lego pieces only",
    "just pieces",
    "base only",
    "towers only",
    "base towers only",
    "base and towers only",
    "base & towers only",
    "main build only",
    "build only",
    "cartridge only",
    "cartridge part",
    "cartridge for lego",
    "cartridge for",
    "mario bros cartridge",
    "cart only",
    "bag only",
    "bags only",
    "bag 1 only",
    "bag 2 only",
    "bag 3 only",
    "bag 4 only",
    "bag 5 only",
    "bag 6 only",
    "bag 7 only",
    "bag 8 only",
    "bag 9 only",
    "bag 10 only",
    "bag 11 only",
    "bag 12 only",
    "bag 13 only",
    "bag 14 only",
    "bag 15 only",
    "lot of 2",
    "lot of two",
    "taxi only",
    "taxi cab only",
    "loose bricks",
    "random pieces",
    "bulk lot",
    "lot",
    "bulk",
]

LEGO_LOOSE_PART_TERMS = [
    "horse",
    "bed",
    "animal",
    "wagon",
    "cart",
    "tree",
    "stand",
    "display stand",
    "fence",
    "barrier",
    "driver",
]


LEGO_INSTRUCTIONS_OR_BOX_ONLY_TERMS = [
    "box only",
    "empty box",
    "empty outer box",
    "outer box only",
    "inner box only",
    "inner boxes only",
    "box + instructions only",
    "box and instructions only",
    "box no lego",
    "box no bricks",
    "packaging only",
    "instructions only",
    "instruction book only",
    "building instructions only",
    "instructions no bricks",
    "manual only",
    "manuals only",
    "box with manuals only",
    "box and manuals only",
    "base shell",
    "mid frame",
    "mid-frame",
    "heat sink",
    "heat sync",
    "disc drive",
    "optical drive",
    "disc only",
    "disk only",
    "mixamp",
    "headset",
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

LEGO_UNAUTHENTIC_TERMS = [
    "moc",
    "custom moc",
    "custom build",
    "custom set",
    "bootleg",
    "lepin",
    "knockoff",
    "knock off",
    "clone",
    "not lego",
    "lego compatible",
    "compatible with lego",
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
    "service manual",
    "parts list",
    "manual only",
    "sensor cleaning",
    "spare part",
    "strap lug",
    "top cover",
    "viewfinder",
]

CONSOLE_PART_ACCESSORY_TERMS = [
    "base shell",
    "board card",
    "bracket",
    "cover only",
    "cover set",
    "console cover",
    "disk games",
    "disc games",
    "drive bracket",
    "empty box",
    "empty box with packing material",
    "game disc only",
    "game only",
    "games only",
    "release games",
    "console checklist",
    "heat shield",
    "heat shield frame",
    "lcd screen",
    "local pickup only",
    "local pick up only",
    "metal frame",
    "package japan used w towel",
    "packing material",
    "replacement",
    "replacement part",
    "supporters package",
    "supporter package",
    "tpu cover",
    "trade",
    "trade for",
    "will trade",
    "swap for",
    "variety disk games",
    "variety disc games",
    "all original slim pro models",
    "all original slim and pro models",
    "original slim pro models",
    "video game only",
    "wifi board",
    "wifi card",
    "wifi module",
    "account only",
    "battery only",
    "blu ray drive",
    "blu-ray drive",
    "box only",
    "box & tray only",
    "box and tray only",
    "case only",
    "case collection",
    "carrying case",
    "hard case",
    "slim hard case",
    "smart pouch",
    "charge dock",
    "charging dock",
    "dock with charger",
    "dock and charger",
    "manual only",
    "manuals only",
    "tray only",
    "controller only",
    "controllers only",
    "disc drive only",
    "external drive",
    "external hard drive",
    "portable hard drive",
    "external hdd",
    "external ssd",
    "external storage",
    "storage expansion card",
    "memory expansion card",
    "expansion card",
    "game drive",
    "hard drive only",
    "hdd only",
    "ssd only",
    "drive model",
    "dock only",
    "faceplate",
    "face plate",
    "face plates",
    "plates",
    "chrome plates",
    "crome plates",
    "poster only",
    "cover",
    "ps5 cover",
    "playstation cover",
    "digital edition cover",
    "disc edition cover",
    "stick drift",
    "drift",
    "external disc drive",
    "external disk drive",
    "drive only",
    "for parts",
    "hdmi port",
    "housing shell",
    "mid frame",
    "mid-frame",
    "fan only",
    "replacement fan",
    "cooling fan",
    "heat sink",
    "heat sync",
    "joy con only",
    "joy-con only",
    "left joy con",
    "left joy-con",
    "motherboard",
    "mainboard",
    "processor",
    "procesor",
    "apu",
    "gpu apu",
    "cpu chip",
    "chip only",
    "no console",
    "no consoles",
    "parts only",
    "power brick",
    "power supply",
    "replacement shell",
    "right joy con",
    "right joy-con",
    "screen only",
    "shell only",
    "stand only",
    "tablet only",
    "thumbstick",
]

CONSOLE_INCOMPLETE_TERMS = [
    "no cables",
    "no controller",
    "no controllers",
    "no cords",
    "no dock",
    "no hdmi",
    "no power cord",
    "no power supply",
    "missing cables",
    "missing controller",
    "missing controllers",
    "missing dock",
]


def _has_any_term(text: str, terms: list[str]) -> bool:
    return any(has_term(text, term) for term in terms)


def _raw_has_term(text: str, term: str) -> bool:
    normalized = normalize_text(text, strip_filler=False)
    normalized_term = normalize_text(term, strip_filler=False)
    if not normalized_term:
        return False
    return bool(re.search(rf"(^|\s){re.escape(normalized_term)}($|\s)", normalized))


def _has_exact_code(text: str, code: str) -> bool:
    """Match short model codes like P4 without matching P40."""
    lowered = text.lower()
    if len(code) >= 2 and code[0].isalpha() and code[1:].isdigit():
        pattern = rf"(?<![a-z0-9]){re.escape(code[0].lower())}\s*{re.escape(code[1:])}(?![a-z0-9])"
        return bool(re.search(pattern, lowered))
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(code.lower())}(?![a-z0-9])", lowered))


def _gpu_modifier_conflicts(title: str, product: Product) -> bool:
    """Reject explicit GPU suffix conflicts for an exact selected model."""

    product_raw = normalize_text(
        f"{product.model} {product.variant or ''}", strip_filler=False
    )
    title_raw = normalize_text(title, strip_filler=False)
    product_compact = compact_text(product_raw, strip_filler=False)
    title_compact = compact_text(title_raw, strip_filler=False)

    product_has_ti = bool(re.search(r"(^|\s)ti($|\s)", product_raw)) or "tisuper" in product_compact
    product_has_super = _raw_has_term(product_raw, "super") or "tisuper" in product_compact
    title_has_ti = bool(re.search(r"(^|\s)ti($|\s)", title_raw)) or "tisuper" in title_compact
    title_has_super = _raw_has_term(title_raw, "super") or "tisuper" in title_compact

    if _raw_has_term(title_raw, "non ti") or "nonti" in title_compact:
        if product_has_ti:
            return True
    if _raw_has_term(title_raw, "non super") or "nonsuper" in title_compact:
        if product_has_super:
            return True

    # NVIDIA suffixes are mutually exclusive exact identities.
    if product_has_ti != title_has_ti or product_has_super != title_has_super:
        if any(token in product_compact for token in ["rtx", "gtx"]):
            return True

    product_has_xtx = bool(re.search(r"(^|\s)xtx($|\s)", product_raw)) or "xtx" in product_compact
    product_has_xt = (bool(re.search(r"(^|\s)xt($|\s)", product_raw)) or product_compact.endswith("xt")) and not product_has_xtx
    title_has_xtx = bool(re.search(r"(^|\s)xtx($|\s)", title_raw)) or "xtx" in title_compact
    title_has_xt = (bool(re.search(r"(^|\s)xt($|\s)", title_raw)) or title_compact.endswith("xt")) and not title_has_xtx
    title_says_non_xt = bool(re.search(r"\bnon[ -]?xt\b", title.lower())) or "nonxt" in title_compact

    if title_says_non_xt:
        if product_has_xt or product_has_xtx:
            return True
        title_has_xt = False
        title_has_xtx = False
    if "rx" in product_compact and (product_has_xt != title_has_xt or product_has_xtx != title_has_xtx):
        return True

    return False


def _looks_like_gpu_accessory(title: str, product: Product | None = None) -> bool:
    normalized = normalize_text(title)
    raw = title.lower()

    if product is not None and product.category == "gpus":
        if _gpu_modifier_conflicts(title, product):
            return True
        product_name = product.display_name

        # Consumer desktop cards should not silently resolve to passive server
        # modules or external/eGPU enclosures that share the same GPU chip.
        product_compact_identity = compact_text(product.model, strip_filler=False)
        is_consumer_desktop_gpu = bool(
            re.search(r"(?:rtx|gtx)\d{3,4}", product_compact_identity)
            or re.search(r"rx\d{3,4}", product_compact_identity)
            or re.search(r"arca\d{3,4}", product_compact_identity)
        ) and not product_compact_identity.startswith("rtxa")
        if is_consumer_desktop_gpu and _has_any_term(
            title,
            [
                "passive",
                "passively cooled",
                "server gpu",
                "server card",
                "server",
                "egpu",
                "e gpu",
                "external gpu",
                "external graphics",
                "graphics amplifier",
                "gaming box",
                "thunderbolt enclosure",
            ],
        ):
            return True
        datacenter_models = ["p4", "p40", "k80", "m40", "p100", "v100", "t4", "a40", "a100"]
        searched_model = next((model for model in datacenter_models if _has_exact_code(product_name, model)), None)
        if searched_model:
            mentioned_models = {model for model in datacenter_models if _has_exact_code(title, model)}
            # Generic compatibility/listing-spam titles like "P4 P40 K80 M40 P100"
            # are usually not the exact card. Keep true single-model listings.
            if mentioned_models - {searched_model}:
                return True

        # Reject variation/compatibility listings that name several GPUs and
        # advertise the cheapest option. Keep workstation model numbers such as
        # Dell Precision 7760 out of this check by requiring a GPU-family prefix.
        product_compact = compact_text(product.model, strip_filler=False)
        title_lower = title.lower()

        gpu_model_groups: list[tuple[str, set[str]]] = []
        if re.search(r"rtxa\d{4}", product_compact):
            gpu_model_groups.append(
                (
                    re.search(r"a\d{4}", product_compact).group(0),
                    set(re.findall(r"(?<![a-z0-9])a(?:2000|3000|4000|4500|5000|5500|6000)(?![a-z0-9])", title_lower)),
                )
            )
        elif re.search(r"rtx\d{4}", product_compact):
            gpu_model_groups.append(
                (
                    re.search(r"rtx\d{4}", product_compact).group(0),
                    {f"rtx{model}" for model in re.findall(r"(?<![a-z0-9])rtx\s*(\d{4})(?![a-z0-9])", title_lower)},
                )
            )
        elif re.search(r"gtx\d{3,4}", product_compact):
            gpu_model_groups.append(
                (
                    re.search(r"gtx\d{3,4}", product_compact).group(0),
                    {f"gtx{model}" for model in re.findall(r"(?<![a-z0-9])gtx\s*(\d{3,4})(?![a-z0-9])", title_lower)},
                )
            )
        elif re.search(r"rx\d{3,4}", product_compact):
            gpu_model_groups.append(
                (
                    re.search(r"rx\d{3,4}", product_compact).group(0),
                    {f"rx{model}" for model in re.findall(r"(?<![a-z0-9])rx\s*(\d{3,4})(?![a-z0-9])", title_lower)},
                )
            )

        for searched_gpu_model, mentioned_gpu_models in gpu_model_groups:
            if mentioned_gpu_models - {searched_gpu_model}:
                return True

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

    # Hardware issue notes should not win, but do not reject normal titles like
    # "tested, no problems" or "no issues".
    issue_terms = ["problem", "problems", "issue", "issues", "fan problem", "fan issue", "problem notes"]
    safe_issue_context = [
        "no problem",
        "no problems",
        "no issue",
        "no issues",
        "without issue",
        "without issues",
        "problem free",
        "problem-free",
        "issue free",
        "issue-free",
    ]
    if _has_any_term(title, issue_terms) and not _has_any_term(title, safe_issue_context):
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


def _older_console_needs_hardware_evidence(product: Product) -> bool:
    family = compact_text(str(product.metadata.get("family") or ""), strip_filler=False)
    identity = compact_text(
        f"{product.brand} {product.model} {product.variant or ''}", strip_filler=False
    )
    combined = f"{family} {identity}"
    return any(
        marker in combined
        for marker in ["playstation4", "ps4", "xboxone", "nintendo3dsxl", "3dsxl"]
    )


def _console_has_hardware_evidence(title: str) -> bool:
    if _has_any_term(title, ["console", "system", "handheld", "unit"]):
        return True

    raw = title.lower()
    model_code_patterns = [
        r"\bcuh[-\s]?\d{4}[a-z]?\b",  # PlayStation 4
        r"\b(?:model\s*)?(?:1540|1681|1787)\b",  # Xbox One revisions
        r"\b(?:spr|red|ktr)[-\s]?001\b",  # Nintendo 3DS XL families
    ]
    return any(re.search(pattern, raw, re.I) for pattern in model_code_patterns)


def _console_has_strong_hardware_evidence(title: str) -> bool:
    """Identify a real console rather than a title that merely names one.

    Marketplace accessories often contain the word ``console`` in phrases such
    as ``for console`` or ``Console Edition``. Strong evidence uses explicit
    system wording, storage/model codes, or normal sale-condition language.
    """
    normalized = normalize_text(title, strip_filler=False)
    scrubbed = re.sub(r"\bconsole edition\b", "", normalized)
    scrubbed = re.sub(r"\bfor (?:the )?console\b", "", scrubbed)

    if re.search(r"\b(?:video game|gaming|complete|full) console\b", scrubbed):
        return True
    if re.search(r"\bconsole (?:system|unit|bundle|with|and)\b", scrubbed):
        return True
    if _has_any_term(scrubbed, ["system", "unit", "handheld"]):
        return True
    if re.search(r"\b(?:32|64|256|500|512|825)\s*gb\b|\b(?:1|2)\s*tb\b", scrubbed):
        return True
    model_code_patterns = [
        r"\bcuh[-\s]?\d{4}[a-z]?\b",
        r"\b(?:model\s*)?(?:1540|1681|1787)\b",
        r"\b(?:spr|red|ktr)[-\s]?001\b",
    ]
    if any(re.search(pattern, scrubbed, re.I) for pattern in model_code_patterns):
        return True
    if _has_any_term(scrubbed, ["tested", "working", "fully functional", "powers on"]):
        return True
    return False


def _looks_like_standalone_console_drive(title: str) -> bool:
    drive_terms = [
        "disc drive",
        "disk drive",
        "optical drive",
        "blu ray drive",
        "blu-ray drive",
    ]
    if not _has_any_term(title, drive_terms):
        return False
    normalized = normalize_text(title, strip_filler=False)
    console_sale_evidence = bool(
        re.search(r"\bconsole (?:with|and|bundle|system|unit)\b", normalized)
        or re.search(r"\b(?:32|64|256|500|512|825)\s*gb\b|\b(?:1|2)\s*tb\b", normalized)
    )
    return not console_sale_evidence


def _looks_like_console_edition_game(title: str) -> bool:
    if not _has_any_term(title, ["console edition"]):
        return False
    game_signals = [
        "game",
        "video game",
        "disc",
        "disk",
        "cartridge",
        "rated",
        "esrb",
    ]
    return _has_any_term(title, game_signals) or not _console_has_strong_hardware_evidence(title)


def _looks_like_console_accessory(title: str, product: Product | None = None) -> bool:
    normalized = normalize_text(title)

    if _has_any_term(title, CONSOLE_PART_ACCESSORY_TERMS + CONSOLE_INCOMPLETE_TERMS):
        return True

    if _looks_like_standalone_console_drive(title):
        return True

    if _looks_like_console_edition_game(title):
        return True

    if _looks_like_console_multi_variation_listing(title, product):
        return True

    # Bundles with games, accessories, storage, or a monitor can still be a
    # legitimate complete-console sale. Keep them when the title positively
    # identifies the console/system; reject bundle titles that only use a
    # platform name as compatibility metadata.
    accessory_bundle_terms = [
        "accessory bundle",
        "accessories bundle",
        "with accessories",
        "monitor bundle",
        "with monitor",
    ]
    if _has_any_term(title, accessory_bundle_terms):
        console_identity_terms = ["console", "system", "unit", "complete"]
        if not _has_any_term(title, console_identity_terms):
            return True

    # Marketplace repair-part listings often say "for PS5/Xbox/Switch".
    # Only use that prefix as a reject signal when it is paired with part words.
    accessory_words = [
        "adapter",
        "button",
        "cable",
        "case",
        "controller",
        "cover",
        "dock",
        "fan",
        "hdmi",
        "housing",
        "joystick",
        "port",
        "power",
        "replacement",
        "screen",
        "shell",
        "stand",
        "supply",
    ]
    if normalized.startswith("for ") and _has_any_term(title, accessory_words):
        return True

    # Switch listings are especially noisy. A full Switch should not be only
    # the tablet/screen, dock, Joy-Con pair, or cartridge/game.
    if product is not None and product.category == "consoles" and product.brand.lower() == "nintendo":
        nintendo_only_terms = [
            "tablet only",
            "console tablet",
            "console only",
            "handheld only",
            "handheld console only",
            "dock only",
            "joycon only",
            "joy-con only",
            "joy con only",
            "game only",
            "cartridge only",
            "cart only",
        ]
        if _has_any_term(title, nintendo_only_terms) and not _has_any_term(title, ["complete", "complete set", "complete console", "console bundle"]):
            return True

        product_text = normalize_text(f"{product.model} {product.variant or ''}", strip_filler=False)
        is_console_builder_family = product.metadata.get("builder") == "consoles" and not product.metadata.get("model_scope")
        is_full_size_switch = (
            "switch" in product_text
            and "lite" not in product_text
            and "switch 2" not in product_text
            and not is_console_builder_family
        )
        is_standard_switch = is_full_size_switch and "oled" not in product_text
        if is_standard_switch:
            # The original Switch is frequently sold as a bare tablet while the
            # title still says "console" and includes HAC-001. For the default
            # complete-system search, require explicit completeness language or
            # evidence that both the controls and dock are included.
            explicit_complete_clues = [
                "complete",
                "complete set",
                "complete console",
                "complete system",
                "full console",
                "full system",
                "console bundle",
                "system bundle",
                "all original accessories",
                "original accessories included",
            ]
            joycon_clues = [
                "with joy con",
                "with joy-con",
                "with joycon",
                "joy con included",
                "joy-con included",
                "joycon included",
                "joy cons included",
                "joy-cons included",
            ]
            dock_clues = [
                "dock",
                "docking station",
            ]
            has_complete_claim = _has_any_term(title, explicit_complete_clues)
            has_controls_and_dock = _has_any_term(title, joycon_clues) and _has_any_term(title, dock_clues)
            if not has_complete_claim and not has_controls_and_dock:
                return True
        elif is_full_size_switch:
            complete_controls_clues = [
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
            standard_switch_identity = [
                "console",
                "system",
                "standard",
                "v1",
                "v2",
                "hac 001",
                "hac-001",
                "hac 001 01",
                "hac-001-01",
                "hac-001(-01)",
            ]
            if not _has_any_term(title, complete_controls_clues + standard_switch_identity):
                title_compact = compact_text(title, strip_filler=False)
                if "hac001" not in title_compact and "hac00101" not in title_compact:
                    return True

    # For PlayStation/Xbox, a real listing usually says console/system/unit or
    # a storage/edition clue. Reject game/accessory-style titles that only use
    # the platform name as compatibility metadata.
    if product is not None and product.category == "consoles" and product.brand.lower() == "nintendo":
        product_text = normalize_text(f"{product.model} {product.variant or ''}", strip_filler=False)
        product_compact = compact_text(f"{product.model} {product.variant or ''}", strip_filler=False)
        is_nintendo_handheld = any(term in product_compact for term in ["3ds", "2ds", "dsi", "dslite"])
        if is_nintendo_handheld:
            accessory_or_media_terms = [
                "game",
                "video game",
                "cartridge",
                "cart only",
                "manual",
                "instructions",
                "pouch",
                "case",
                "ac adapter",
                "power adapter",
                "charger",
                "charger cable",
                "cable cord",
            ]
            console_identity_terms = ["console", "system", "handheld", "unit"]
            if _has_any_term(title, accessory_or_media_terms) and not _has_any_term(title, console_identity_terms):
                return True

    if product is not None and product.category == "consoles" and product.brand.lower() in {"xbox", "playstation"}:
        console_clues = [
            "console",
            "system",
            "unit",
            "1tb",
            "512gb",
            "2tb",
            "disc edition",
            "digital edition",
            "slim",
            "pro",
        ]
        obvious_game_or_merch = [
            "game",
            "video game",
            "games",
            "disc games",
            "disk games",
            "towel",
            "supporter",
            "supporters",
        ]
        if _has_any_term(title, obvious_game_or_merch) and not _has_any_term(title, console_clues):
            return True

        # A controller bundle can be a valid console bundle, but only when the
        # title has stronger hardware evidence than the platform name itself.
        if _has_any_term(title, ["controller bundle", "controller set"]) and not _console_has_strong_hardware_evidence(title):
            return True

    if (
        product is not None
        and product.category == "consoles"
        and _older_console_needs_hardware_evidence(product)
        and not _console_has_hardware_evidence(title)
    ):
        return True

    return False


def _looks_like_missing_lego_figures(title: str) -> bool:
    normalized = normalize_text(title, strip_filler=False)
    # Catch seller shorthand such as "MISSING 1 fig", "missing one fig",
    # "missing 2 figures", and "no figs" without rejecting normal
    # piece-count wording.
    return bool(
        re.search(r"\bmissing\s+(?:\d+|one|two|a|the)?\s*(?:mini\s*)?fig(?:ure)?s?\b", normalized)
        or re.search(r"\bno\s+(?:mini\s*)?fig(?:ure)?s?\b", normalized)
        or re.search(r"\b(?:mini\s*)?fig(?:ure)?s?\s+missing\b", normalized)
    )


def _looks_like_console_multi_variation_listing(title: str, product: Product | None = None) -> bool:
    if product is None or product.category != "consoles":
        return False
    normalized = normalize_text(title, strip_filler=False)
    compact = compact_text(title, strip_filler=False)
    if has_term(title, "original") and has_term(title, "slim") and has_term(title, "pro") and _has_any_term(title, ["model", "models"]):
        return True
    if "alloriginalslimpro" in compact or "originalslimpro" in compact:
        return True

    # Sellers commonly hide an accessory-only or "no console" variation behind
    # a parent console title. Search-result prices then reflect the cheap option,
    # not the console. These selection phrases are a strong variation-listing clue.
    variation_phrases = [
        "seller pick",
        "you pick",
        "pick your",
        "pick one",
        "choose option",
        "choose your",
        "select option",
        "select your",
        "multiple options",
        "various options",
        "options available",
    ]
    if _has_any_term(title, variation_phrases):
        return True

    return False


def _lego_missing_is_explicitly_negated(title: str) -> bool:
    normalized = normalize_text(title, strip_filler=False)
    return bool(
        re.search(
            r"\b(?:no|zero|nothing)\s+(?:parts?|pieces?|bricks?|figs?|figures?|minifigs?|minifigures?)?\s*missing\b",
            normalized,
        )
        or re.search(r"\bnot\s+missing\b", normalized)
    )


def _looks_like_lego_completeness_issue(title: str) -> bool:
    normalized = normalize_text(title, strip_filler=False)

    if re.search(r"\b(?:near|nearly|almost|mostly)\s+complete\b", normalized):
        return True

    for percentage in re.findall(
        r"(?<!\d)(\d{1,3})(?:\.\d+)?\s*%\s*(?:complete|completeness)\b",
        title.lower(),
    ):
        if int(percentage) < 100:
            return True

    # Missing-part titles are incomplete, but phrases such as "no missing
    # pieces" are positive completeness evidence and should remain eligible.
    safe_missing_context = _lego_missing_is_explicitly_negated(title)
    if re.search(r"\bmissing\b", normalized) and not safe_missing_context:
        return True

    return False


def _looks_like_lego_bundle_or_multi_set(title: str, product: Product) -> bool:
    set_number = str(product.metadata.get("set_number") or product.variant or "").strip()
    if not set_number:
        return False

    safe_missing_context = _lego_missing_is_explicitly_negated(title)
    incomplete_terms = LEGO_INCOMPLETE_OR_PART_TERMS
    if safe_missing_context:
        incomplete_terms = [term for term in incomplete_terms if "missing" not in term]
    if (
        _has_any_term(title, incomplete_terms)
        or (_looks_like_missing_lego_figures(title) and not safe_missing_context)
        or _looks_like_lego_completeness_issue(title)
    ):
        return True

    if _has_any_term(title, LEGO_INSTRUCTIONS_OR_BOX_ONLY_TERMS):
        return True

    # Sellers use several packaging-only variations that do not contain the
    # exact phrase "box only", including "3 Inner Boxes Only". Treat any
    # numbered or inner/outer packaging-only title as junk for complete-set
    # searches.
    raw_normalized = normalize_text(title, strip_filler=False)
    if re.search(r"\b(?:empty\s+)?(?:inner|outer)\s+box(?:es)?(?:\s+only)?\b", raw_normalized):
        return True
    if re.search(r"\b\d+\s+(?:inner|outer)\s+box(?:es)?(?:\s+only)?\b", raw_normalized):
        return True
    if re.search(r"\b(?:boxes?|packaging)\s+only\b", raw_normalized):
        return True

    # Common typo protection for strong packaging warnings. One-edit variants
    # such as EMPRY should not allow an empty-box listing through.
    def one_edit_from_empty(token: str) -> bool:
        target = "empty"
        if abs(len(token) - len(target)) > 1:
            return False
        previous = list(range(len(target) + 1))
        for index, char in enumerate(token, start=1):
            current = [index]
            for target_index, target_char in enumerate(target, start=1):
                current.append(
                    min(
                        current[-1] + 1,
                        previous[target_index] + 1,
                        previous[target_index - 1] + (char != target_char),
                    )
                )
            previous = current
        return previous[-1] <= 1

    packaging_words = {"box", "boxes", "packaging", "outer", "inner"}
    tokens = raw_normalized.split()
    if any(one_edit_from_empty(token) for token in tokens) and packaging_words.intersection(tokens):
        return True

    if _has_any_term(title, LEGO_ACCESSORY_TERMS):
        return True

    if _has_any_term(title, LEGO_UNAUTHENTIC_TERMS):
        return True

    clearly_full_set = _has_any_term(
        title,
        ["complete", "complete set", "sealed", "new in box", "with box", "building kit"],
    )

    # LEGO part listings can include the exact set number or model name while
    # selling only a horse, bed, display stand, cartridge piece, etc. Keep this
    # gated behind "not clearly full set" so normal complete sets that mention
    # included accessories do not get rejected.
    if not clearly_full_set and _has_any_term(title, LEGO_LOOSE_PART_TERMS):
        return True

    # A lone minifigure/person listing can reference the parent set number.
    # Do not reject complete sets that mention included minifigures, but reject
    # character/minifigure-style titles that are not clearly full-set listings.
    if _has_any_term(title, LEGO_CHARACTER_ONLY_TERMS) and not clearly_full_set:
        return True

    # Minifigure/item-code listings often include a parent set number without
    # saying "minifigure". Example: "LABRIA (sw1126) from Lego Star Wars 75290".
    if not clearly_full_set and (re.search(r"\b(?:sw|hp|col|sh|njo)\d{3,5}\b", normalize_text(title)) or has_term(title, "from lego")):
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
    if set_number:
        # LEGO titles are too noisy to trust model-name-only matches. Require the
        # exact set number so "Millennium Falcon" does not match a different set
        # or a minifigure that references the parent model.
        return has_term(title, set_number)

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


def _console_title_matches_product(title: str, product: Product) -> bool:
    normalized_title = normalize_text(title, strip_filler=False)
    compact_title = compact_text(title, strip_filler=False)
    product_text = normalize_text(f"{product.brand} {product.model} {product.variant or ''}", strip_filler=False)

    def has_raw(term: str) -> bool:
        return _raw_has_term(title, term)

    if product.brand.lower() == "playstation":
        is_ps5 = any(marker in compact_text(alias, strip_filler=False) for alias in product.aliases + [product.display_name] for marker in ["ps5", "playstation5"])
        is_ps4 = any(marker in compact_text(alias, strip_filler=False) for alias in product.aliases + [product.display_name] for marker in ["ps4", "playstation4"])
        if is_ps5 and not ("ps5" in compact_title or "playstation5" in compact_title):
            return False
        if is_ps4 and not ("ps4" in compact_title or "playstation4" in compact_title):
            return False
        if "pro" in product_text and not has_raw("pro"):
            return False
        if "pro" in product_text and not _console_has_strong_hardware_evidence(title):
            return False
        if "slim" in product_text and not has_raw("slim"):
            return False
        is_base_generation = not any(term in product_text for term in ["slim", "pro"])
        if is_base_generation and (has_raw("slim") or has_raw("pro")):
            return False
        if "digital" in product_text:
            if not (has_raw("digital") or "digitaledition" in compact_title):
                return False
            if has_raw("disc edition") or has_raw("disk edition"):
                return False
            return True
        # Disc edition/default PS5 should not return Digital Edition units.
        if "disc" in product_text and (has_raw("digital") or "digitaledition" in compact_title) and not has_raw("disc"):
            return False
        return True

    if product.brand.lower() == "xbox":
        if not has_raw("xbox"):
            return False
        if "xbox360" in compact_title or has_raw("xbox 360"):
            return False
        if "series x" in product_text:
            if has_raw("series s") or has_raw("xbox one") or has_raw("one x") or has_raw("one s"):
                return False
            return has_raw("series x") or "seriesx" in compact_title
        if "series s" in product_text:
            if has_raw("series x") or has_raw("xbox one") or has_raw("one x") or has_raw("one s"):
                return False
            if not (has_raw("series s") or "seriess" in compact_title):
                return False
            if "1tb" in compact_text(product.variant or "", strip_filler=False):
                return "1tb" in compact_title
            if "512gb" in compact_text(product.variant or "", strip_filler=False):
                return "1tb" not in compact_title
            return True
        if "one x" in product_text:
            return (has_raw("one x") or "onex" in compact_title) and not has_raw("series x") and not has_raw("series s")
        if "one s" in product_text:
            return (has_raw("one s") or "ones" in compact_title) and not has_raw("series x") and not has_raw("series s")
        return all(has_raw(required_term) for required_term in product.required_terms)

    if product.brand.lower() == "nintendo":
        if "switch 2" in product_text:
            return has_raw("switch 2") or "switch2" in compact_title
        if "switch oled" in product_text:
            return has_raw("switch") and has_raw("oled") and not has_raw("lite")
        if "switch lite" in product_text:
            return has_raw("switch") and has_raw("lite")
        if "switch" in product_text:
            return (
                has_raw("switch")
                and not has_raw("lite")
                and not has_raw("oled")
                and not has_raw("switch 2")
                and "heg001" not in compact_title
            )
        if "wii u" in product_text:
            return has_raw("wii u") or "wiiu" in compact_title
        return all(has_raw(required_term) for required_term in product.required_terms)

    return all(has_raw(required_term) for required_term in product.required_terms)

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
    "console": "consoles",
    "consoles": "consoles",
    "playstation": "consoles",
    "ps5": "consoles",
    "xbox": "consoles",
    "switch": "consoles",
    "nintendo": "consoles",
    "ram": "ram",
    "memory": "ram",
    "computer-memory": "ram",
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


STRICT_VERSION_NUMBERS = {
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
}


def _version_number(value: str) -> str | None:
    """Extract an explicit generation clue such as II or Mark II.

    Keep this intentionally conservative: a normal model number like A1 or R5
    is not itself treated as a generation suffix. This prevents "Sony A1 II"
    from silently falling back to the original A1 while leaving ordinary model
    numbers alone.
    """

    lowered = value.lower().replace("-", " ")
    mark_match = re.search(r"\b(?:mark|mk)\s*(ii|iii|iv|v|2|3|4|5)\b", lowered)
    if mark_match:
        token = mark_match.group(1)
        return STRICT_VERSION_NUMBERS.get(token, token)

    roman_match = re.search(r"\b(ii|iii|iv|v)\b", lowered)
    if roman_match:
        return STRICT_VERSION_NUMBERS[roman_match.group(1)]
    return None


def _storage_clues(value: str) -> set[str]:
    return {
        f"{amount}{unit.lower()}"
        for amount, unit in re.findall(r"(?i)(?<!\d)(\d+)\s*(gb|tb)\b", value)
    }


def _missing_strict_query_clue(query: str, product: Product) -> bool:
    product_corpus = " ".join(
        [
            product.display_name,
            product.model,
            product.variant or "",
            str(product.metadata.get("storage") or ""),
            str(product.metadata.get("drive") or ""),
            *product.aliases,
        ]
    )

    if product.category in {"cameras", "lenses"}:
        query_version = _version_number(query)
        if query_version is not None and _version_number(product_corpus) != query_version:
            return True

    if product.category == "gpus":
        for modifier in ["ti", "super", "xtx", "xt", "gre"]:
            if has_term(query, modifier) and not has_term(product_corpus, modifier):
                return True

    if product.category == "lego":
        query_set_numbers = set(re.findall(r"(?<!\d)\d{5}(?!\d)", query))
        selected_set_number = str(product.metadata.get("set_number") or product.variant or "").strip()
        if query_set_numbers and selected_set_number not in query_set_numbers:
            return True

    grouped_console_variants = (
        product.category == "consoles"
        and bool(product.metadata.get("variants_grouped"))
    )

    if product.category == "consoles" and not grouped_console_variants:
        query_raw = normalize_text(query, strip_filler=False)
        product_raw = normalize_text(product_corpus, strip_filler=False)
        if re.search(r"\bdigital(?:\s+edition)?\b", query_raw) and "digital" not in product_raw:
            return True
        if re.search(r"\b(?:disc|disk)\s+edition\b", query_raw) and not re.search(
            r"\b(?:disc|disk)\b", product_raw
        ):
            return True

    query_storage = _storage_clues(query)
    if (
        query_storage
        and not grouped_console_variants
        and not query_storage.issubset(_storage_clues(product_corpus))
    ):
        return True

    return False


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

        # Switch 2 is paused for now; do not let a Switch 2 query fall back
        # to regular Switch/OLED/Lite products just because the word Switch matches.
        if product.category == "consoles" and (has_term(normalized_query, "switch 2") or "switch2" in compact_query):
            product_compact = compact_text(f"{product.brand} {product.model} {product.variant or ''}", strip_filler=False)
            if "switch2" not in product_compact:
                confidence = 0.0

        if confidence > best_confidence:
            best_confidence = confidence
            best_alias = candidate

    if best_confidence <= 0 or _missing_strict_query_clue(query, product):
        return None
    return ProductMatch(product=product, confidence=round(best_confidence, 2), matched_alias=best_alias)


def _gpu_variant_resolution_is_ambiguous(query: str, matches: list[ProductMatch]) -> bool:
    """Do not silently choose one VRAM variant for a shared GPU model.

    RTX 3080 is the main current example: the 10GB and 12GB products share
    common aliases, so a bare query can otherwise resolve whichever catalog
    row sorts first at 100%. A storage clue makes the choice explicit.
    """

    if not matches or _storage_clues(query):
        return False

    best = matches[0]
    if best.product.category != "gpus":
        return False

    siblings = [
        match
        for match in matches
        if match.confidence >= max(0.7, best.confidence - 0.04)
        and match.product.category == best.product.category
        and match.product.brand.lower() == best.product.brand.lower()
        and normalize_text(match.product.model, strip_filler=False)
        == normalize_text(best.product.model, strip_filler=False)
    ]
    vram_values = {
        str(match.product.metadata.get("vram_gb") or "").strip()
        for match in siblings
        if match.product.metadata.get("vram_gb") is not None
    }
    return len(vram_values) > 1


def match_product(query: str, category: str | None = None) -> ProductMatch | None:
    normalized_category = normalize_category(category)
    if normalized_category == "ram":
        return ram_product_match(query)

    matches = suggest_products(query, category=normalized_category, limit=8)

    # Consoles resolve to core model records. Storage, color, bundle, and
    # Disc/Digital details remain grouped variants and do not create separate
    # searchable products in this release.
    if not matches:
        return None

    if normalized_category == "consoles":
        spec = parse_console_query(query)
        # Do not silently turn a genuinely broad Xbox family query into one
        # arbitrary model. PS4, PS5, and Nintendo Switch are themselves core
        # model identities, so their parser assigns an explicit model scope.
        if (
            spec is not None
            and spec.model is None
            and spec.storage is None
            and spec.edition is None
            and spec.family in {
                "xbox-series",
                "xbox-one",
                "playstation-5",
                "playstation-4",
            }
        ):
            return None

    best_match = matches[0]
    if best_match.confidence < 0.7:
        return None
    if _gpu_variant_resolution_is_ambiguous(query, matches):
        return None
    return best_match


def suggest_products(query: str, category: str | None = None, limit: int = 8) -> list[ProductMatch]:
    normalized_category = normalize_category(category)
    if normalized_category == "ram":
        match = ram_product_match(query)
        return [match] if match is not None else []

    if len(query.strip()) < 2:
        return []

    matches: list[ProductMatch] = []
    for product in list_products(normalized_category):
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
        if excluded_term in REVIEW_ONLY_TITLE_TERMS:
            continue
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

    if product.category == "ram":
        return ram_title_matches_product(title, product)

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

    if product.category == "consoles":
        if _looks_like_console_accessory(title, product):
            return False
        if product.metadata.get("builder") == "consoles":
            return console_builder_title_matches_product(title, product)
        return _console_title_matches_product(title, product)

    if product.category == "lego":
        if _looks_like_lego_bundle_or_multi_set(title, product):
            return False
        return _lego_title_matches_product(title, product)

    return all(has_term(title, required_term) for required_term in product.required_terms)


def listing_match_rejection_reasons(title: str, product: Product) -> list[str]:
    """Return a useful QA-facing reason when product matching rejects a title."""
    if product.category == "consoles":
        if _looks_like_console_accessory(title, product):
            return ["console accessory/part/incomplete"]
        if product.metadata.get("builder") == "consoles":
            matched = console_builder_title_matches_product(title, product)
        else:
            matched = _console_title_matches_product(title, product)
        return [] if matched else ["console model conflict"]

    return [] if listing_matches_product(title, product) else ["catalog/product match rejected"]
