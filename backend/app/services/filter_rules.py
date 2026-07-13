from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.catalog.normalizer import has_term
from app.models.product import Product
from app.services.database import database_configured, database_connection, database_url

MAX_FILTER_RULES = 500
RULE_CACHE_SECONDS = 5.0

logger = logging.getLogger(__name__)
_RULE_CACHE: list[dict[str, Any]] | None = None
_RULE_CACHE_AT = 0.0
_RULE_CACHE_SOURCE: str | None = None


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
        try:
            decoded = json.loads(except_phrases)
            except_phrases = decoded if isinstance(decoded, list) else except_phrases.split(",")
        except json.JSONDecodeError:
            except_phrases = except_phrases.split(",")
    if not isinstance(except_phrases, list):
        except_phrases = []

    cleaned_exceptions = [_clean_phrase(str(item)) for item in except_phrases]
    cleaned_exceptions = [item for item in cleaned_exceptions if item]

    created_at = record.get("created_at") or _now().isoformat()
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

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
        "created_at": str(created_at),
    }


def _cache_source() -> str:
    return database_url() or str(_rules_path())


def _invalidate_cache() -> None:
    global _RULE_CACHE, _RULE_CACHE_AT, _RULE_CACHE_SOURCE
    _RULE_CACHE = None
    _RULE_CACHE_AT = 0.0
    _RULE_CACHE_SOURCE = None
_RULE_CACHE_SOURCE: str | None = None


def _load_file_rules() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in _read_json_list(_rules_path()):
        normalized = _normalize_rule_record(raw)
        if normalized is not None:
            records.append(normalized)
    return records[-MAX_FILTER_RULES:]


def _load_database_rules() -> list[dict[str, Any]]:
    with database_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM (
                SELECT id, phrase, category, product_id, except_phrases, note,
                       source_title, source_item_id, enabled, created_at
                FROM scoutly_manual_filter_rules
                ORDER BY created_at DESC
                LIMIT %s
            ) AS newest_rules
            ORDER BY created_at ASC
            """,
            (MAX_FILTER_RULES,),
        ).fetchall()
    records: list[dict[str, Any]] = []
    for row in rows:
        normalized = _normalize_rule_record(dict(row))
        if normalized is not None:
            records.append(normalized)
    return records


def _all_rules_cached() -> list[dict[str, Any]]:
    global _RULE_CACHE, _RULE_CACHE_AT, _RULE_CACHE_SOURCE
    now = time.monotonic()
    source = _cache_source()
    if (
        _RULE_CACHE is not None
        and _RULE_CACHE_SOURCE == source
        and now - _RULE_CACHE_AT < RULE_CACHE_SECONDS
    ):
        return list(_RULE_CACHE)

    if database_configured():
        try:
            records = _load_database_rules()
        except Exception:
            logger.exception("PostgreSQL filter-rule read failed; using file fallback.")
            records = _load_file_rules()
    else:
        records = _load_file_rules()

    _RULE_CACHE = records
    _RULE_CACHE_AT = now
    _RULE_CACHE_SOURCE = source
    return list(records)


def list_manual_filter_rules(include_disabled: bool = False) -> list[dict[str, Any]]:
    records = _all_rules_cached()
    if include_disabled:
        return records[-MAX_FILTER_RULES:]
    return [record for record in records if record.get("enabled", True)][-MAX_FILTER_RULES:]


def add_manual_filter_rule(rule: ManualFilterRule) -> dict[str, Any]:
    record = _normalize_rule_record(asdict(rule))
    if record is None:
        raise ValueError("Filter phrase is required.")

    if database_configured():
        try:
            created_at = datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
            with database_connection() as connection:
                connection.execute(
                    """
                    DELETE FROM scoutly_manual_filter_rules
                    WHERE LOWER(phrase) = LOWER(%s)
                      AND category IS NOT DISTINCT FROM %s
                      AND product_id IS NOT DISTINCT FROM %s
                    """,
                    (record["phrase"], record.get("category"), record.get("product_id")),
                )
                connection.execute(
                    """
                    INSERT INTO scoutly_manual_filter_rules (
                        id, phrase, category, product_id, except_phrases, note,
                        source_title, source_item_id, enabled, created_at
                    ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
                    """,
                    (
                        record["id"],
                        record["phrase"],
                        record.get("category"),
                        record.get("product_id"),
                        json.dumps(record.get("except_phrases") or []),
                        record.get("note"),
                        record.get("source_title"),
                        record.get("source_item_id"),
                        record.get("enabled", True),
                        created_at,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM scoutly_manual_filter_rules
                    WHERE id NOT IN (
                        SELECT id FROM scoutly_manual_filter_rules
                        ORDER BY created_at DESC
                        LIMIT %s
                    )
                    """,
                    (MAX_FILTER_RULES,),
                )
            _invalidate_cache()
            return record
        except Exception:
            logger.exception("PostgreSQL filter-rule write failed; using file fallback.")

    records = _load_file_rules()
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
    _write_json_list(_rules_path(), records[-MAX_FILTER_RULES:])
    _invalidate_cache()
    return record


def delete_manual_filter_rule(rule_id: str) -> bool:
    if database_configured():
        try:
            with database_connection() as connection:
                cursor = connection.execute(
                    "DELETE FROM scoutly_manual_filter_rules WHERE id = %s",
                    (rule_id,),
                )
                deleted = cursor.rowcount > 0
            if deleted:
                _invalidate_cache()
            return deleted
        except Exception:
            logger.exception("PostgreSQL filter-rule delete failed; using file fallback.")

    records = _load_file_rules()
    kept = [record for record in records if record.get("id") != rule_id]
    if len(kept) == len(records):
        return False
    _write_json_list(_rules_path(), kept)
    _invalidate_cache()
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
