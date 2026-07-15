from __future__ import annotations

import json
import sys

from dotenv import load_dotenv

load_dotenv()

from app.services.database import initialize_database
from app.services.keh_feed import sync_keh_feed


def main() -> int:
    initialize_database()
    result = sync_keh_feed()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
