#!/usr/bin/env python3
"""Download ball clay images for KORVANTO CLAY BALL page."""
from __future__ import annotations

import json
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

# Raw ball clay / kaolinite material — not trucks or industrial yards
CLAY_PRODUCT = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Kaolinite_from_Twiggs_County_in_Georgia_in_USA.jpg/1280px-Kaolinite_from_Twiggs_County_in_Georgia_in_USA.jpg"
CLAY_FAMILY = "https://upload.wikimedia.org/wikipedia/commons/3/37/Frozen_spoil%2C_Newbridge_ball_clay_quarry_-_geograph.org.uk_-_1654551.jpg"


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KorvantoImageSync/1.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
                data = resp.read()
            if len(data) < 8000:
                return False
            dest.write_bytes(data)
            print(f"  saved {dest.relative_to(ROOT)} ({len(data)} bytes)")
            return True
        except Exception as exc:
            if attempt < 3:
                time.sleep(12 * (attempt + 1))
            else:
                print(f"  failed {dest.name}: {exc}")
                return False
    return False


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    product_dest = ROOT / "assets/images/products/korvanto-clay.jpg"
    family_dest = ROOT / "assets/images/families/korvanto-clay.jpg"
    legacy_dest = ROOT / "assets/images/Product-Images/Ball-Clay.jpg"

    if download(CLAY_PRODUCT, product_dest):
        for product in data.get("products", []):
            if product.get("slug") == "korvanto-clay":
                product["image"] = "assets/images/products/korvanto-clay.jpg"

    time.sleep(2)
    if download(CLAY_FAMILY, family_dest):
        for family in data.get("catalog", {}).get("families", []):
            if family.get("slug") == "korvanto-clay":
                family["image"] = "assets/images/families/korvanto-clay.jpg"
        if legacy_dest.parent.exists():
            legacy_dest.write_bytes(family_dest.read_bytes())

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated KORVANTO CLAY BALL product and family images")


if __name__ == "__main__":
    main()
