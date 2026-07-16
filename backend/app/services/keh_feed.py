from __future__ import annotations

import csv
import gzip
import io
import json
import logging
import os
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import httpx

from app.catalog.catalog import list_products, listing_matches_product, suggest_products
from app.models.listing import Listing
from app.models.product import Product
from app.ranking.scorer import score_listing
from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_ITEMS = 10000
MAX_LENS_MODELS = 500
# KEH camera publication now follows the complete active camera-body catalog.
# The former three-model pilot whitelist is intentionally retired.
GRADE_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("LN", "Like New", re.compile(r"(?:^|\s)-?\s*LN\s*-?\s*-\s*Like New(?:\s|$)", re.I)),
    ("LN-", "Like New Minus", re.compile(r"(?:^|\s)-?\s*LN-\s*-\s*Like New Minus(?:\s|$)", re.I)),
    ("EX+", "Excellent Plus", re.compile(r"(?:^|\s)-?\s*EX\+\s*-\s*Excellent Plus(?:\s|$)", re.I)),
    ("EX", "Excellent", re.compile(r"(?:^|\s)-?\s*EX\s*-\s*Excellent(?:\s|$)", re.I)),
    ("BGN", "Bargain", re.compile(r"(?:^|\s)-?\s*BGN\s*-\s*Bargain(?:\s|$)", re.I)),
    ("UG", "Ugly", re.compile(r"(?:^|\s)-?\s*UG\s*-\s*Ugly(?:\s|$)", re.I)),
]

LENS_MOUNT_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Canon EF-M", re.compile(r"\b(?:canon\s+ef[- ]?m|ef[- ]?m[- ]mount|for\s+canon\s+ef[- ]?m)\b", re.I)),
    ("Canon RF", re.compile(r"\b(?:canon\s+rf(?:-s)?|rf(?:-s)?[- ]mount|for\s+canon\s+rf(?:-s)?)\b", re.I)),
    ("Canon EF", re.compile(r"\b(?:canon\s+ef(?:-s)?|ef(?:-s)?[- ]mount|for\s+canon\s+ef(?:-s)?)\b", re.I)),
    ("Sony E", re.compile(r"\b(?:sony\s+(?:fe|e)|(?:fe|e)[- ]mount|for\s+sony\s+(?:fe|e))\b", re.I)),
    ("Sony A", re.compile(r"\b(?:(?:sony|minolta)\s+a|a[- ]mount|for\s+(?:sony|minolta)\s+a)\b", re.I)),
    ("Nikon Z", re.compile(r"\b(?:nikon\s+z|z[- ]mount|for\s+nikon\s+z)\b", re.I)),
    ("Nikon F", re.compile(r"\b(?:nikon\s+f|f[- ]mount|for\s+nikon\s+f)\b", re.I)),
    ("Fujifilm G", re.compile(r"\b(?:(?:fuji|fujifilm)\s+(?:gf|gfx)|(?:gf|gfx)[- ]mount|for\s+(?:fuji|fujifilm)\s+(?:gf|gfx))\b", re.I)),
    ("Fujifilm X", re.compile(r"\b(?:(?:fuji|fujifilm)\s+x|x[- ]mount|for\s+(?:fuji|fujifilm)\s+x)\b", re.I)),
    ("Micro Four Thirds", re.compile(r"\b(?:micro\s+four\s+thirds|micro\s*4/3|m4/3|mft)\b", re.I)),
    ("L-Mount", re.compile(r"\b(?:l[- ]mount|for\s+l[- ]mount)\b", re.I)),
    ("Leica M", re.compile(r"\b(?:leica\s+m|m[- ]mount|for\s+leica\s+m)\b", re.I)),
    ("Pentax 645", re.compile(r"\bpentax\s+645\b", re.I)),
    ("Pentax K", re.compile(r"\b(?:pentax\s+k|k[- ]mount|for\s+pentax\s+k)\b", re.I)),
    ("Four Thirds", re.compile(r"\bfour\s+thirds\b", re.I)),
]

LENS_RANGE_PATTERN = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*[-–]\s*(\d{1,3}(?:\.\d+)?)\s*mm\b", re.I)
LENS_PRIME_PATTERN = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*mm\b", re.I)


def _now() -> datetime:
    return datetime.now(UTC)


def keh_feed_url() -> str | None:
    value = os.getenv("AWIN_KEH_FEED_URL", "").strip()
    if not value or value.startswith("${{"):
        return None
    return value


def keh_feed_enabled() -> bool:
    return os.getenv("KEH_FEED_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


def keh_public_results_enabled() -> bool:
    return os.getenv("KEH_PUBLIC_RESULTS", "false").strip().lower() in {"1", "true", "yes", "on"}


def public_product_ids() -> set[str]:
    return {
        product.id
        for product in list_products("cameras")
        if product.product_type == "camera_body"
    }


def product_is_public(product_id: str | None) -> bool:
    return bool(
        product_id
        and keh_public_results_enabled()
        and product_id in public_product_ids()
    )


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _inventory_path() -> Path:
    return _data_dir() / "keh_inventory.json"


def _runs_path() -> Path:
    return _data_dir() / "keh_sync_runs.json"


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
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _serialize(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in record.items()
    }


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "in stock", "available"}


def _float(value: Any) -> float | None:
    try:
        return round(float(str(value).strip()), 2)
    except (TypeError, ValueError):
        return None


def parse_keh_grade(title: str, description: str = "") -> tuple[str | None, str | None]:
    haystack = f"{title} {description}"
    # Check LN- before LN because the codes overlap.
    ordered = [GRADE_PATTERNS[1], GRADE_PATTERNS[0], *GRADE_PATTERNS[2:]]
    for code, label, pattern in ordered:
        if pattern.search(haystack):
            return code, label
    return None, None


def classify_keh_product(row: dict[str, str]) -> str | None:
    title = str(row.get("product_name") or "").lower()
    category = " ".join(
        [
            str(row.get("merchant_category") or ""),
            str(row.get("merchant_product_category_path") or ""),
            str(row.get("category_name") or ""),
        ]
    ).lower()

    if "used camera lenses" in category or "camera lenses" in category:
        if any(term in title for term in ["conversion lens", "converter", "teleconverter", "extender", "adapter"]):
            return None
        if LENS_RANGE_PATTERN.search(title) or LENS_PRIME_PATTERN.search(title):
            return "lens"
        return None

    body_category = (
        "used digital cameras" in category
        or "cameras > digital cameras" in category
        or "used cameras >" in category
    )
    if body_category and any(term in title for term in ["camera", "body", "dslr", "mirrorless"]):
        # A body listing may legitimately include a battery, charger, flash, or
        # case. The category path is a safer signal than accessory words in the
        # title for KEH's structured feed.
        if " lens" not in title or "body" in title:
            return "camera_body"
    return None


def pilot_product_ids() -> set[str]:
    """Backward-compatible admin label for the full active camera-body catalog."""
    return public_product_ids()


def _lens_model_name(title: str) -> str:
    first_segment = title.split("|", 1)[0].strip()
    first_segment = re.sub(
        r"\s+-\s+(?:LN-|LN|EX\+|EX|BGN|UG)\s+-.*$",
        "",
        first_segment,
        flags=re.I,
    ).strip()
    return first_segment or title.strip()


def _lens_mount(title: str, category_path: str = "") -> str:
    haystack = f"{title} {category_path}"
    for label, pattern in LENS_MOUNT_RULES:
        if pattern.search(haystack):
            return label
    return "Other / unknown"


def _lens_focal_data(title: str) -> tuple[str, float | None, float | None]:
    range_match = LENS_RANGE_PATTERN.search(title)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return "Zoom", min(low, high), max(low, high)
    prime_match = LENS_PRIME_PATTERN.search(title)
    if prime_match:
        focal = float(prime_match.group(1))
        return "Prime", focal, focal
    return "Other", None, None


def _lens_focal_group(lens_type: str, focal_min: float | None, focal_max: float | None) -> str:
    if focal_min is None or focal_max is None:
        return "Other / unknown"
    if lens_type == "Prime":
        if focal_min < 20:
            return "Under 20mm"
        if focal_min <= 35:
            return "20–35mm"
        if focal_min <= 60:
            return "36–60mm"
        if focal_min <= 105:
            return "61–105mm"
        if focal_min <= 200:
            return "106–200mm"
        return "Over 200mm"
    if lens_type == "Zoom":
        ratio = focal_max / focal_min if focal_min > 0 else 0
        if ratio >= 5 and focal_min <= 35:
            return "All-in-one / travel zoom"
        if focal_min < 16:
            return "Ultra-wide zoom"
        if focal_min < 24:
            return "Wide zoom"
        if focal_min < 50:
            return "Standard zoom"
        if focal_min < 100:
            return "Telephoto zoom"
        return "Super-telephoto zoom"
    return "Other / unknown"


def lens_metadata(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or "")
    category_path = str(item.get("merchant_category_path") or "")
    lens_type, focal_min, focal_max = _lens_focal_data(title)
    model_name = _lens_model_name(title)
    normalized_key = re.sub(r"[^a-z0-9]+", " ", model_name.lower()).strip()
    return {
        "model_key": normalized_key,
        "model_name": model_name,
        "mount": _lens_mount(title, category_path),
        "lens_type": lens_type,
        "focal_min": focal_min,
        "focal_max": focal_max,
        "focal_group": _lens_focal_group(lens_type, focal_min, focal_max),
        "brand": str(item.get("brand") or "Unknown").strip() or "Unknown",
    }


def _match_row(row: dict[str, str], product_type: str) -> dict[str, Any]:
    title = str(row.get("product_name") or "").strip()
    matches = suggest_products(title, category="cameras", limit=3)
    pilot_ids = pilot_product_ids()
    eligible = [
        match
        for match in matches
        if match.product.id in pilot_ids and match.product.product_type == product_type
    ]
    best = eligible[0] if eligible else None

    status = "unmatched"
    reason = "No pilot catalog match"
    if best is not None and best.confidence >= 0.7:
        close_second = eligible[1] if len(eligible) > 1 else None
        if close_second is not None and close_second.confidence >= best.confidence - 0.03:
            status = "ambiguous"
            reason = f"Close match with {close_second.product.display_name}"
        elif best.product.product_type != product_type:
            status = "unmatched"
            reason = "Catalog product type conflict"
        elif not listing_matches_product(title, best.product):
            status = "unmatched"
            reason = "Title failed exact-product listing rules"
        else:
            status = "matched"
            reason = "Pilot product matched"

    return {
        "pilot_candidate": best is not None,
        "match_status": status,
        "match_reason": reason,
        "matched_product_id": best.product.id if best is not None else None,
        "matched_product_label": best.product.display_name if best is not None else None,
        "match_confidence": best.confidence if best is not None else None,
    }


def normalize_feed_row(row: dict[str, str], synced_at: datetime) -> dict[str, Any] | None:
    product_type = classify_keh_product(row)
    if product_type is None:
        return None
    title = str(row.get("product_name") or "").strip()
    aw_product_id = str(row.get("aw_product_id") or "").strip()
    affiliate_url = str(row.get("aw_deep_link") or "").strip()
    price = _float(row.get("search_price"))
    if not aw_product_id or not title or not affiliate_url or price is None:
        return None

    grade_code, grade_label = parse_keh_grade(title, str(row.get("description") or ""))
    if product_type == "lens":
        match = {
            "match_status": "lens_inventory",
            "match_reason": "Available KEH lens inventory",
            "matched_product_id": None,
            "matched_product_label": None,
            "match_confidence": None,
        }
    else:
        match = _match_row(row, product_type)
        if not match.pop("pilot_candidate", False):
            return None
    return {
        "aw_product_id": aw_product_id,
        "merchant_product_id": str(row.get("merchant_product_id") or "").strip() or None,
        "title": title,
        "description": str(row.get("description") or "").strip() or None,
        "product_type": product_type,
        "merchant_category_path": str(row.get("merchant_product_category_path") or "").strip() or None,
        "price": price,
        "currency": str(row.get("currency") or "USD").strip() or "USD",
        "condition_grade_code": grade_code,
        "condition_grade_label": grade_label,
        "affiliate_url": affiliate_url,
        "merchant_url": str(row.get("merchant_deep_link") or "").strip() or None,
        "image_url": str(row.get("merchant_image_url") or row.get("large_image") or "").strip() or None,
        "brand": str(row.get("brand_name") or "").strip() or None,
        "mpn": str(row.get("mpn") or "").strip() or None,
        "upc": str(row.get("upc") or "").strip() or None,
        "in_stock": _truthy(row.get("in_stock")) or _truthy(row.get("stock_status")),
        "is_for_sale": _truthy(row.get("is_for_sale")) or _truthy(row.get("web_offer")),
        "feed_last_updated": str(row.get("last_updated") or "").strip() or None,
        "active": True,
        "synced_at": synced_at,
        **match,
    }


def _decode_feed(content: bytes, content_type: str = "") -> str:
    if content[:2] == b"\x1f\x8b" or "gzip" in content_type.lower():
        content = gzip.decompress(content)
    elif content[:4] == b"PK\x03\x04" or "zip" in content_type.lower():
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            if not names:
                raise ValueError("Awin feed archive did not contain a file.")
            content = archive.read(names[0])
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("cp1252")


def parse_feed_text(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader if row]


def _download_feed(url: str) -> tuple[list[dict[str, str]], dict[str, str | None]]:
    with httpx.Client(timeout=httpx.Timeout(120.0, connect=20.0), follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "PriceSift-KEH-Pilot/0.6.27"})
        response.raise_for_status()
    text = _decode_feed(response.content, response.headers.get("content-type", ""))
    return parse_feed_text(text), {
        "etag": response.headers.get("etag"),
        "last_modified": response.headers.get("last-modified"),
    }


def _replace_inventory_file(items: list[dict[str, Any]]) -> None:
    _write_json_list(_inventory_path(), [_serialize(item) for item in items[-MAX_FILE_ITEMS:]])


def _save_run_file(run: dict[str, Any]) -> None:
    runs = _read_json_list(_runs_path())
    runs.append(_serialize(run))
    _write_json_list(_runs_path(), runs[-100:])


def _replace_inventory_db(items: list[dict[str, Any]]) -> None:
    with database_connection() as connection:
        connection.execute("UPDATE scoutly_keh_inventory SET active = FALSE")
        if items:
            values = [
                (
                    item["aw_product_id"], item["merchant_product_id"], item["title"], item["description"],
                    item["product_type"], item["merchant_category_path"], item["price"], item["currency"],
                    item["condition_grade_code"], item["condition_grade_label"], item["affiliate_url"],
                    item["merchant_url"], item["image_url"], item["brand"], item["mpn"], item["upc"],
                    item["in_stock"], item["is_for_sale"], item["matched_product_id"],
                    item["matched_product_label"], item["match_confidence"], item["match_status"],
                    item["match_reason"], item["feed_last_updated"], item["synced_at"], item["active"],
                )
                for item in items
            ]
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO scoutly_keh_inventory (
                        aw_product_id, merchant_product_id, title, description, product_type,
                        merchant_category_path, price, currency, condition_grade_code,
                        condition_grade_label, affiliate_url, merchant_url, image_url, brand,
                        mpn, upc, in_stock, is_for_sale, matched_product_id, matched_product_label,
                        match_confidence, match_status, match_reason, feed_last_updated, synced_at, active
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (aw_product_id) DO UPDATE SET
                        merchant_product_id = EXCLUDED.merchant_product_id,
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        product_type = EXCLUDED.product_type,
                        merchant_category_path = EXCLUDED.merchant_category_path,
                        price = EXCLUDED.price,
                        currency = EXCLUDED.currency,
                        condition_grade_code = EXCLUDED.condition_grade_code,
                        condition_grade_label = EXCLUDED.condition_grade_label,
                        affiliate_url = EXCLUDED.affiliate_url,
                        merchant_url = EXCLUDED.merchant_url,
                        image_url = EXCLUDED.image_url,
                        brand = EXCLUDED.brand,
                        mpn = EXCLUDED.mpn,
                        upc = EXCLUDED.upc,
                        in_stock = EXCLUDED.in_stock,
                        is_for_sale = EXCLUDED.is_for_sale,
                        matched_product_id = EXCLUDED.matched_product_id,
                        matched_product_label = EXCLUDED.matched_product_label,
                        match_confidence = EXCLUDED.match_confidence,
                        match_status = EXCLUDED.match_status,
                        match_reason = EXCLUDED.match_reason,
                        feed_last_updated = EXCLUDED.feed_last_updated,
                        synced_at = EXCLUDED.synced_at,
                        active = EXCLUDED.active
                    """,
                    values,
                )


def _save_run_db(run: dict[str, Any]) -> None:
    with database_connection() as connection:
        connection.execute(
            """
            INSERT INTO scoutly_keh_sync_runs (
                id, started_at, completed_at, status, feed_items, scoped_items,
                matched_items, unmatched_items, ambiguous_items, error_items,
                etag, last_modified, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run["id"], run["started_at"], run["completed_at"], run["status"],
                run["feed_items"], run["scoped_items"], run["matched_items"],
                run["unmatched_items"], run["ambiguous_items"], run["error_items"],
                run.get("etag"), run.get("last_modified"), run.get("error_message"),
            ),
        )


def sync_keh_feed(*, feed_rows: Iterable[dict[str, str]] | None = None) -> dict[str, Any]:
    started_at = _now()
    run: dict[str, Any] = {
        "id": str(uuid4()),
        "started_at": started_at,
        "completed_at": None,
        "status": "running",
        "feed_items": 0,
        "scoped_items": 0,
        "matched_items": 0,
        "unmatched_items": 0,
        "ambiguous_items": 0,
        "error_items": 0,
        "etag": None,
        "last_modified": None,
        "error_message": None,
    }

    try:
        if feed_rows is None:
            if not keh_feed_enabled():
                raise RuntimeError("KEH_FEED_ENABLED is not true.")
            url = keh_feed_url()
            if not url:
                raise RuntimeError("AWIN_KEH_FEED_URL is not configured.")
            rows, metadata = _download_feed(url)
            run.update(metadata)
        else:
            rows = list(feed_rows)

        run["feed_items"] = len(rows)
        items: list[dict[str, Any]] = []
        synced_at = _now()
        for row in rows:
            try:
                item = normalize_feed_row(row, synced_at)
            except Exception:
                logger.exception("KEH feed row normalization failed.")
                run["error_items"] += 1
                continue
            if item is None:
                continue
            items.append(item)

        run["scoped_items"] = len(items)
        run["matched_items"] = sum(item["match_status"] == "matched" for item in items)
        run["unmatched_items"] = sum(item["match_status"] == "unmatched" for item in items)
        run["ambiguous_items"] = sum(item["match_status"] == "ambiguous" for item in items)

        if database_configured():
            try:
                _replace_inventory_db(items)
            except Exception:
                logger.exception("PostgreSQL KEH inventory write failed; using file fallback.")
                _replace_inventory_file(items)
        else:
            _replace_inventory_file(items)

        run["status"] = "success"
    except Exception as error:
        run["status"] = "failed"
        run["error_message"] = str(error)[:1000]
    finally:
        run["completed_at"] = _now()
        if database_configured():
            try:
                _save_run_db(run)
            except Exception:
                logger.exception("PostgreSQL KEH sync-run write failed; using file fallback.")
                _save_run_file(run)
        else:
            _save_run_file(run)

    return _serialize(run)


def _db_inventory(limit: int, status: str | None, product_id: str | None) -> list[dict[str, Any]]:
    clauses = ["active = TRUE"]
    params: list[Any] = []
    if status:
        clauses.append("match_status = %s")
        params.append(status)
    if product_id:
        clauses.append("matched_product_id = %s")
        params.append(product_id)
    params.append(limit)
    with database_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT * FROM scoutly_keh_inventory
            WHERE {' AND '.join(clauses)}
            ORDER BY match_status, matched_product_label NULLS LAST, price ASC, title
            LIMIT %s
            """,
            tuple(params),
        ).fetchall()
    return [_serialize(dict(row)) for row in rows]


def list_keh_inventory(limit: int = 200, status: str | None = None, product_id: str | None = None) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_FILE_ITEMS))
    if database_configured():
        try:
            return _db_inventory(limit, status, product_id)
        except Exception:
            logger.exception("PostgreSQL KEH inventory read failed; using file fallback.")
    items = [item for item in _read_json_list(_inventory_path()) if item.get("active", True)]
    if status:
        items = [item for item in items if item.get("match_status") == status]
    if product_id:
        items = [item for item in items if item.get("matched_product_id") == product_id]
    return sorted(items, key=lambda item: (str(item.get("match_status")), str(item.get("matched_product_label") or ""), float(item.get("price") or 0)))[:limit]


def latest_sync_run() -> dict[str, Any] | None:
    if database_configured():
        try:
            with database_connection() as connection:
                row = connection.execute(
                    "SELECT * FROM scoutly_keh_sync_runs ORDER BY started_at DESC LIMIT 1"
                ).fetchone()
            return _serialize(dict(row)) if row else None
        except Exception:
            logger.exception("PostgreSQL KEH sync-run read failed; using file fallback.")
    runs = _read_json_list(_runs_path())
    return runs[-1] if runs else None


def keh_overview(limit: int = 200) -> dict[str, Any]:
    items = list_keh_inventory(limit=MAX_FILE_ITEMS)
    counts = {"matched": 0, "unmatched": 0, "ambiguous": 0}
    for item in items:
        status = str(item.get("match_status") or "unmatched")
        counts[status] = counts.get(status, 0) + 1
    product_counts: dict[str, int] = {}
    for item in items:
        product_id = item.get("matched_product_id")
        if item.get("match_status") == "matched" and product_id:
            product_counts[str(product_id)] = product_counts.get(str(product_id), 0) + 1
    camera_items = [item for item in items if item.get("product_type") == "camera_body"]
    return {
        "enabled": keh_feed_enabled(),
        "configured": keh_feed_url() is not None,
        "public_results_enabled": keh_public_results_enabled(),
        "public_product_ids": sorted(public_product_ids()),
        "pilot_product_ids": sorted(pilot_product_ids()),
        "latest_sync": latest_sync_run(),
        "active_item_count": len(items),
        "matched_count": counts.get("matched", 0),
        "unmatched_count": counts.get("unmatched", 0),
        "ambiguous_count": counts.get("ambiguous", 0),
        "lens_inventory_count": counts.get("lens_inventory", 0),
        "matched_product_count": len(product_counts),
        "items": camera_items[:limit],
    }


def _all_active_lens_inventory() -> list[dict[str, Any]]:
    if database_configured():
        try:
            with database_connection() as connection:
                rows = connection.execute(
                    """
                    SELECT * FROM scoutly_keh_inventory
                    WHERE active = TRUE AND product_type = 'lens'
                      AND in_stock = TRUE AND is_for_sale = TRUE
                    ORDER BY price ASC, title
                    LIMIT %s
                    """,
                    (MAX_FILE_ITEMS,),
                ).fetchall()
            return [_serialize(dict(row)) for row in rows]
        except Exception:
            logger.exception("PostgreSQL KEH lens inventory read failed; using file fallback.")
    return [
        item for item in _read_json_list(_inventory_path())
        if item.get("active", True)
        and item.get("product_type") == "lens"
        and item.get("in_stock")
        and item.get("is_for_sale")
    ][:MAX_FILE_ITEMS]


def _facet_values(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "Other / unknown")
        counts[value] = counts.get(value, 0) + 1
    return [
        {"value": value, "label": value, "count": count}
        for value, count in sorted(counts.items(), key=lambda pair: (pair[0] == "Other / unknown", pair[0].lower()))
    ]


def keh_lens_builder(
    *,
    mount: str | None = None,
    lens_type: str | None = None,
    focal_group: str | None = None,
    brand: str | None = None,
    query: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    raw_items = _all_active_lens_inventory()
    enriched = [{**item, **lens_metadata(item)} for item in raw_items]

    mount_items = enriched
    type_items = [item for item in mount_items if not mount or item["mount"] == mount]
    group_items = [item for item in type_items if not lens_type or item["lens_type"] == lens_type]
    brand_items = [item for item in group_items if not focal_group or item["focal_group"] == focal_group]
    model_items = [item for item in brand_items if not brand or item["brand"] == brand]

    cleaned_query = (query or "").strip().lower()
    if cleaned_query:
        model_items = [
            item for item in model_items
            if cleaned_query in item["model_name"].lower()
            or cleaned_query in str(item.get("mpn") or "").lower()
        ]

    grouped: dict[str, dict[str, Any]] = {}
    for item in model_items:
        key = item["model_key"] or str(item.get("aw_product_id"))
        group = grouped.setdefault(
            key,
            {
                "model_key": key,
                "model_name": item["model_name"],
                "mount": item["mount"],
                "lens_type": item["lens_type"],
                "focal_group": item["focal_group"],
                "focal_min": item["focal_min"],
                "focal_max": item["focal_max"],
                "brand": item["brand"],
                "listing_count": 0,
                "lowest_price": None,
                "highest_price": None,
                "currency": item.get("currency") or "USD",
                "condition_grades": [],
                "image_url": item.get("image_url"),
                "listings": [],
            },
        )
        group["listing_count"] += 1
        price = _float(item.get("price"))
        if price is not None and (group["lowest_price"] is None or price < group["lowest_price"]):
            group["lowest_price"] = price
        if price is not None and (group["highest_price"] is None or price > group["highest_price"]):
            group["highest_price"] = price
        grade_code = str(item.get("condition_grade_code") or "").strip()
        if grade_code and grade_code not in group["condition_grades"]:
            group["condition_grades"].append(grade_code)
        if not group.get("image_url") and item.get("image_url"):
            group["image_url"] = item.get("image_url")
        group["listings"].append({
            "aw_product_id": item.get("aw_product_id"),
            "title": item.get("title"),
            "price": price,
            "currency": item.get("currency") or "USD",
            "condition_grade_code": item.get("condition_grade_code"),
            "condition_grade_label": item.get("condition_grade_label"),
            "affiliate_url": item.get("affiliate_url"),
            "image_url": item.get("image_url"),
            "mpn": item.get("mpn"),
        })

    models = list(grouped.values())
    grade_order = {"LN": 0, "LN-": 1, "EX+": 2, "EX": 3, "BGN": 4, "UG": 5}
    for model in models:
        model["condition_grades"] = sorted(
            model["condition_grades"],
            key=lambda grade: (grade_order.get(grade, 99), grade),
        )
        model["listings"] = sorted(
            model["listings"],
            key=lambda listing: (float(listing.get("price") or 10**12), str(listing.get("title") or "")),
        )[:3]
    models.sort(key=lambda model: (-int(model["listing_count"]), float(model["lowest_price"] or 10**12), model["model_name"].lower()))
    limit = max(1, min(limit, MAX_LENS_MODELS))

    return {
        "summary": {
            "listing_count": len(enriched),
            "model_count": len({item["model_key"] for item in enriched if item["model_key"]}),
            "filtered_listing_count": len(model_items),
            "filtered_model_count": len(models),
        },
        "selected": {
            "mount": mount,
            "lens_type": lens_type,
            "focal_group": focal_group,
            "brand": brand,
            "query": query,
        },
        "facets": {
            "mounts": _facet_values(mount_items, "mount"),
            "lens_types": _facet_values(type_items, "lens_type"),
            "focal_groups": _facet_values(group_items, "focal_group"),
            "brands": _facet_values(brand_items, "brand"),
        },
        "models": models[:limit],
    }


def public_keh_listings(product: Product, limit: int = 50) -> list[Listing]:
    """Return public-pilot KEH listings for one exact camera product.

    The feed remains shadow-only for every product except the explicit public
    whitelist. KEH inventory is already exact-product matched during sync, so
    this adapter only exposes active, in-stock, for-sale rows as normal
    PriceSift fixed-price listings.
    """

    if (
        product.category != "cameras"
        or product.product_type != "camera_body"
        or not product_is_public(product.id)
    ):
        return []

    items = list_keh_inventory(
        limit=max(1, min(limit, 200)),
        status="matched",
        product_id=product.id,
    )
    listings: list[Listing] = []
    grade_bonus = {"LN": 12, "LN-": 10, "EX+": 8, "EX": 6, "BGN": 2, "UG": -5}

    for item in items:
        if not item.get("active", True):
            continue
        if not item.get("in_stock") or not item.get("is_for_sale"):
            continue

        price = _float(item.get("price"))
        affiliate_url = str(item.get("affiliate_url") or "").strip()
        title = str(item.get("title") or "").strip()
        if price is None or not affiliate_url or not title:
            continue

        grade_code = str(item.get("condition_grade_code") or "").strip()
        grade_label = str(item.get("condition_grade_label") or "").strip()
        condition_parts = ["Used"]
        if grade_code:
            condition_parts.append(grade_code)
        if grade_label:
            condition_parts.append(grade_label)

        warning_labels: list[str] = []
        # KEH currently offers free standard ground shipping on qualifying US
        # orders over $75. Every public pilot camera body should clear that
        # threshold; lower-price rows stay visible but do not claim free
        # shipping without a feed-provided delivery cost.
        shipping = 0.0
        if price < 75:
            warning_labels.append("Shipping confirmed at checkout")

        listing = Listing(
            provider="KEH",
            title=title,
            price=price,
            shipping=shipping,
            total_price=round(price + shipping, 2),
            condition=" · ".join(condition_parts),
            seller_rating=None,
            seller_feedback_score=None,
            url=affiliate_url,
            image_url=item.get("image_url") or None,
            affiliate_url_used=True,
            affiliate_url_has_campaign_id=True,
            listing_type="fixed_price",
            buying_options=["FIXED_PRICE"],
            warning_labels=warning_labels,
        )
        # Neutralize the generic missing-marketplace-feedback penalty for a
        # specialist retailer, then give a small structured-grade adjustment.
        listing.score = round(
            score_listing(listing, product) + 12 + grade_bonus.get(grade_code, 0),
            2,
        )
        listings.append(listing)

    return sorted(listings, key=lambda item: item.score, reverse=True)
