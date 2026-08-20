"""Public catalog facade with small runtime catalog supplements.

The main matching/filtering implementation lives in ``catalog_core``. Keeping
small demand-backed additions outside the ~900 KB static JSON makes batches
reviewable without rewriting that generated/static file.
"""

from __future__ import annotations

import sys
from functools import lru_cache

from app.catalog import catalog_core as _core
from app.catalog.demand_cameras import demand_camera_products
from app.catalog.retro_consoles import retro_console_products


_base_load_products = getattr(
    _core,
    "_pricesift_base_load_products",
    _core.load_products,
)
_core._pricesift_base_load_products = _base_load_products


@lru_cache(maxsize=1)
def _pricesift_load_products():
    return [
        *_base_load_products(),
        *demand_camera_products(),
        *retro_console_products(),
    ]


# Core functions such as match_product() resolve load_products from their own
# module globals. Patch that one catalog hook, then expose the core module at
# the historical app.catalog.catalog import path so existing imports and
# monkeypatches continue to act on the same module object.
_core.load_products = _pricesift_load_products
sys.modules[__name__] = _core
