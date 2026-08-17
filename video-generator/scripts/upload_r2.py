from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    story = json.loads((project / "work" / "story.json").read_text(encoding="utf-8"))
    video = project / "out" / "pricesift-short.mp4"
    if not video.is_file() or video.stat().st_size == 0:
        raise RuntimeError("Rendered video is missing")

    product = re.sub(r"[^a-z0-9-]+", "-", str(story["product_id"]).lower()).strip("-")
    day = datetime.now(ZoneInfo("America/Detroit")).strftime("%Y-%m-%d")
    key = f"pricesift-shorts/{day}-{product}.mp4"

    endpoint = os.environ["R2_ENDPOINT"]
    bucket = os.environ["R2_BUCKET"]
    public_base = os.environ["R2_PUBLIC_BASE_URL"].rstrip("/")
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
    client.upload_file(str(video), bucket, key, ExtraArgs={"ContentType": "video/mp4"})
    public_url = f"{public_base}/{key}"
    (project / "work" / "public-url.txt").write_text(public_url, encoding="utf-8")
    print(public_url)


if __name__ == "__main__":
    main()
