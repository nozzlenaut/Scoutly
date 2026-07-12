from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.catalog.normalizer import has_term
from app.models.product import Product

MAX_FILTER_RULES = 500


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _rules_path() -> Path:
    return _data_dir() / "manual_filter_rules.json"


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_json_list(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(path)


@dataclass
class ManualFilterRule:
    phrase: str
    category: str | None = None
    product_id: str | None = None
    except_phrases: list[str] = field(default_factory=list)
    note: str | None = None
    source_title: str | None = None
    source_item_id: str | None = None
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: _now().isoformat())


def _clean_phrase(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_rule_record(record: dict[str, Any]) -> dict[str, Any] | None:
    phrase = _clean_phrase(str(record.get("phrase") or ""))
    if not phrase:
        return None

    except_phrases = record.get("except_phrases") or []
    if isinstance(except_phrases, str):
        except_phrases = [part.strip() for part in except_phrases.split(",")]
    if not isinstance(except_phrases, list):
        except_phrases = []

    cleaned_exceptions = [_clean_phrase(str(item)) for item in except_phrases]
    cleaned_exceptions = [item for item in cleaned_exceptions if item]

    return {
        "id": str(record.get("id") or uuid.uuid4().hex[:12]),
        "phrase": phrase,
        "category": _clean_phrase(str(record.get("category") or "")).lower() or None,
        "product_id": _clean_phrase(str(record.get("product_id") or "")) or None,
        "except_phrases": cleaned_exceptions,
        "note": _clean_phrase(str(record.get("note") or "")) or None,
        "source_title": _clean_phrase(str(record.get("source_title") or "")) or None,
        "source_item_id": _clean_phrase(str(record.get("source_item_id") or "")) or None,
        "enabled": bool(record.get("enabled", True)),
        "created_at": str(record.get("created_at") or _now().isoformat()),
    }


def list_manual_filter_rules(include_disabled: bool = False) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in _read_json_list(_rules_path()):
        normalized = _normalize_rule_record(raw)
        if normalized is None:
            continue
        if not include_disabled and not normalized.get("enabled", True):
            continue
        records.append(normalized)
    return records[-MAX_FILTER_RULES:]


def add_manual_filter_rule(rule: ManualFilterRule) -> dict[str, Any]:
    record = _normalize_rule_record(asdict(rule))
    if record is None:
        raise ValueError("Filter phrase is required.")

    records = list_manual_filter_rules(include_disabled=True)
    # Replace exact duplicate scope+phrase rules instead of growing forever.
    records = [
        existing
        for existing in records
        if not (
            existing.get("phrase", "").lower() == record["phrase"].lower()
            and existing.get("category") == record.get("category")
            and existing.get("product_id") == record.get("product_id")
        )
    ]
    records.append(record)
    records = records[-MAX_FILTER_RULES:]
    _write_json_list(_rules_path(), records)
    return record


def delete_manual_filter_rule(rule_id: str) -> bool:
    records = list_manual_filter_rules(include_disabled=True)
    kept = [record for record in records if record.get("id") != rule_id]
    if len(kept) == len(records):
        return False
    _write_json_list(_rules_path(), kept)
    return True


def _rule_applies_to_scope(rule: dict[str, Any], product: Product | None, category: str | None = None) -> bool:
    rule_category = rule.get("category")
    candidate_category = product.category if product is not None else category
    if rule_category and candidate_category and rule_category != candidate_category:
        return False
    if rule_category and not candidate_category:
        return False

    rule_product_id = rule.get("product_id")
    if rule_product_id and (product is None or product.id != rule_product_id):
        return False

    return True


def manual_filter_rejection_reasons(
    title: str,
    product: Product | None = None,
    category: str | None = None,
) -> list[str]:
    reasons: list[str] = []
    for rule in list_manual_filter_rules():
        if not _rule_applies_to_scope(rule, product, category):
            continue

        phrase = str(rule.get("phrase") or "")
        if not has_term(title, phrase):
            continue

        exceptions = [str(item) for item in rule.get("except_phrases") or []]
        if any(has_term(title, exception) for exception in exceptions):
            continue

        scope = rule.get("product_id") or rule.get("category") or "global"
        reasons.append(f"manual filter ({scope}): {phrase}")
    return reasons
