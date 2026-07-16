from __future__ import annotations

import os
import sys

import pytest

# Keep local test runs from creating tracked .pyc files inside the repository.
sys.dont_write_bytecode = True

# These must be blanked BEFORE pytest imports the application modules.
# app.main loads .env during import and search_service builds its provider registry
# during import, so an autouse fixture alone is too late to prevent real local
# credentials from selecting live providers.
PRODUCTION_ENV_VARS = (
    "DATABASE_URL",
    "EBAY_CLIENT_ID",
    "EBAY_CLIENT_SECRET",
    "EBAY_ENV",
    "EBAY_AFFILIATE_CAMPAIGN_ID",
    "EBAY_AFFILIATE_REFERENCE_ID",
    "AWIN_KEH_FEED_URL",
    "KEH_FEED_ENABLED",
    "KEH_PUBLIC_RESULTS",
    "KEH_PUBLIC_PRODUCT_IDS",
    "KEH_SHADOW_PRODUCT_IDS",
    "SCOUTLY_ADMIN_TOKEN",
)

for name in PRODUCTION_ENV_VARS:
    os.environ[name] = ""


@pytest.fixture(autouse=True)
def isolate_unit_tests_from_production(monkeypatch: pytest.MonkeyPatch) -> None:
    # Keep every test isolated, including tests that import application modules
    # later than normal collection.
    for name in PRODUCTION_ENV_VARS:
        monkeypatch.setenv(name, "")
