from __future__ import annotations

from typing import Any

from app.services.qa_store import list_qa_evaluations, load_qa_cases


CAMERA_CASES = [
    ("canon-5d-iii", "Canon EOS 5D Mark III", "camera-canon-eos-5d-mark-iii-body", "Canon EOS 5D Mark III Body", "Separate Mark III from Mark IV and reject kits, lenses, accessories, and broken bodies."),
    ("canon-5d-iv", "Canon EOS 5D Mark IV", "camera-canon-eos-5d-mark-iv-body", "Canon EOS 5D Mark IV Body", "Separate Mark IV from earlier 5D generations and reject kits, lenses, accessories, and broken bodies."),
    ("canon-r8", "Canon EOS R8", "camera-canon-eos-r8-body", "Canon EOS R8 Body", "Keep R8 distinct from R5, R6, R7, RP, kits, and accessory-only listings."),
    ("canon-rp", "Canon EOS RP", "camera-canon-eos-rp-body", "Canon EOS RP Body", "Keep EOS RP distinct from similar Canon RF bodies and reject kits, accessories, and broken bodies."),
    ("canon-rebel-t7", "Canon EOS Rebel T7", "camera-canon-eos-rebel-t7-body", "Canon EOS Rebel T7 Body", "Accept the complete T7 / 2000D body while rejecting lenses, kits, accessories, and other Rebel generations."),
    ("fuji-x-e4", "Fujifilm X-E4", "camera-fujifilm-x-e4-body", "Fujifilm X-E4 Body", "Keep X-E4 separate from X-E3, X-T bodies, grips, accessories, and lens bundles."),
    ("fuji-x-h2", "Fujifilm X-H2", "camera-fujifilm-x-h2-body", "Fujifilm X-H2 Body", "Keep X-H2 separate from X-H2S and reject cages, grips, lenses, kits, and broken bodies."),
    ("fuji-x-h2s", "Fujifilm X-H2S", "camera-fujifilm-x-h2s-body", "Fujifilm X-H2S Body", "Require the X-H2S suffix and reject ordinary X-H2 bodies, accessories, kits, and damaged cameras."),
    ("fuji-x100v", "Fujifilm X100V", "camera-fujifilm-x100v", "Fujifilm X100V", "Return the fixed-lens X100V camera while rejecting X100VI, conversion lenses, hoods, filters, cases, and accessories."),
    ("nikon-d750", "Nikon D750", "camera-nikon-d750-body", "Nikon D750 Body", "Keep D750 separate from D7500 and reject kits, lenses, accessories, and broken bodies."),
    ("nikon-z5", "Nikon Z5", "camera-nikon-z5-body", "Nikon Z5 Body", "Keep the original Z5 separate from Z5 II and reject kits, lenses, accessories, and damaged bodies."),
    ("nikon-z7-ii", "Nikon Z7 II", "camera-nikon-z7-ii-body", "Nikon Z7 II Body", "Require the II generation and reject original Z7 bodies, kits, accessories, and broken cameras."),
    ("nikon-zf", "Nikon Zf", "camera-nikon-zf-body", "Nikon Zf Body", "Keep the full-frame Zf separate from APS-C Zfc and reject grips, cages, kits, and accessories."),
    ("om-system-om1", "OM System OM-1", "camera-om-system-om-1-body", "OM System OM-1 Body", "Return the modern OM System OM-1 without mixing in vintage film cameras, accessories, kits, or broken bodies."),
    ("panasonic-gh6", "Panasonic Lumix GH6", "camera-panasonic-lumix-gh6-body", "Panasonic Lumix GH6 Body", "Keep GH6 separate from GH5-family bodies and reject cages, kits, lenses, accessories, and damaged cameras."),
    ("panasonic-s1", "Panasonic Lumix S1", "camera-panasonic-lumix-s1-body", "Panasonic Lumix S1 Body", "Keep S1 separate from S1H, S1R, and S5 bodies while rejecting kits, lenses, and accessories."),
    ("sony-a7r-iv", "Sony A7R IV", "camera-sony-a7r-iv-body", "Sony A7R IV Body", "Require the A7R IV generation and reject A7 IV, other A7R generations, kits, accessories, and broken bodies."),
    ("sony-a7r-v", "Sony A7R V", "camera-sony-a7r-v-body", "Sony A7R V Body", "Require the A7R V generation and reject earlier A7R bodies, kits, accessories, and broken cameras."),
]

LENS_CASES = [
    ("Sony E", "Prime", ("Under 20mm", "20–35mm", "36–60mm", "61–105mm", "106–200mm", "Over 200mm")),
    ("Sony E", "Zoom", ("All-in-one / travel zoom", "Ultra-wide zoom", "Wide zoom", "Standard zoom", "Telephoto zoom", "Super-telephoto zoom")),
    ("Canon EF", "Prime", ("36–60mm", "61–105mm", "106–200mm")),
    ("Canon EF", "Zoom", ("Wide zoom", "Standard zoom", "Telephoto zoom", "Super-telephoto zoom")),
    ("Canon RF", "Prime", ("20–35mm", "36–60mm")),
    ("Canon RF", "Zoom", ("Standard zoom", "Telephoto zoom")),
    ("Nikon Z", "Prime", ("20–35mm", "36–60mm")),
    ("Nikon Z", "Zoom", ("Standard zoom", "Telephoto zoom")),
    ("Fujifilm X", "Prime", ("20–35mm",)),
    ("Fujifilm X", "Zoom", ("Standard zoom",)),
    ("Micro Four Thirds", "Prime", ("20–35mm",)),
    ("Micro Four Thirds", "Zoom", ("Telephoto zoom",)),
]


def _slug(value: str) -> str:
    return "-".join("".join(character if character.isalnum() else " " for character in value.lower()).split())


def _expansion_cases() -> list[dict[str, Any]]:
    cases = [
        {
            "id": f"camera-expansion-{slug}",
            "category": "cameras",
            "query": query,
            "expected_product_id": product_id,
            "expected_label": label,
            "goal": goal,
            "priority": "medium",
            "suite": "camera_lens_expansion",
        }
        for slug, query, product_id, label, goal in CAMERA_CASES
    ]
    for mount, lens_type, focal_groups in LENS_CASES:
        for focal_group in focal_groups:
            case_slug = f"{_slug(mount)}-{_slug(lens_type)}-{_slug(focal_group)}"
            label = f"{mount} · {lens_type} · {focal_group}"
            cases.append(
                {
                    "id": f"lens-expansion-{case_slug}",
                    "category": "lenses",
                    "query": label,
                    "expected_product_id": f"lens-filter-{case_slug}",
                    "expected_label": label,
                    "goal": f"Confirm the KEH Lens Lab returns only {mount} {lens_type.lower()} models classified as {focal_group}, with no mount or focal-group leakage.",
                    "priority": "medium",
                    "suite": "camera_lens_expansion",
                    "runner": "keh_lens",
                    "lens_filters": {
                        "mount": mount,
                        "lens_type": lens_type,
                        "focal_group": focal_group,
                    },
                }
            )
    return cases


def load_all_qa_cases() -> list[dict[str, Any]]:
    combined = [*load_qa_cases(), *_expansion_cases()]
    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for case in combined:
        case_id = str(case.get("id") or "").strip()
        if not case_id or case_id in seen_ids or not case.get("query") or not case.get("category"):
            continue
        seen_ids.add(case_id)
        cases.append(case)
    return cases


def qa_cases_with_latest() -> list[dict[str, Any]]:
    evaluations = list_qa_evaluations(limit=5000)
    latest_by_case: dict[str, dict[str, Any]] = {}
    attempts_by_case: dict[str, int] = {}
    for evaluation in evaluations:
        case_id = str(evaluation.get("case_id") or "")
        if not case_id:
            continue
        attempts_by_case[case_id] = attempts_by_case.get(case_id, 0) + 1
        latest_by_case.setdefault(case_id, evaluation)

    return [
        {
            **case,
            "attempt_count": attempts_by_case.get(str(case["id"]), 0),
            "latest_evaluation": latest_by_case.get(str(case["id"])),
        }
        for case in load_all_qa_cases()
    ]


def qa_summary() -> dict[str, Any]:
    cases = qa_cases_with_latest()
    counts = {"pass": 0, "top3_only": 0, "fail": 0, "no_inventory": 0, "untested": 0}
    category_counts: dict[str, dict[str, int]] = {}
    for case in cases:
        category = str(case.get("category") or "unknown")
        category_counts.setdefault(category, {key: 0 for key in counts})
        outcome = str((case.get("latest_evaluation") or {}).get("outcome") or "untested")
        if outcome not in counts:
            outcome = "untested"
        counts[outcome] += 1
        category_counts[category][outcome] += 1

    tested = len(cases) - counts["untested"]
    available = counts["pass"] + counts["top3_only"] + counts["fail"]
    usable = counts["pass"] + counts["top3_only"]
    return {
        "total_cases": len(cases),
        "tested_cases": tested,
        "available_inventory_cases": available,
        "counts": counts,
        "category_counts": category_counts,
        "quality_rate": round((usable / available) * 100, 1) if available else None,
        "overall_rate": round((usable / tested) * 100, 1) if tested else None,
    }
