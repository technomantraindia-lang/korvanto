#!/usr/bin/env python3
"""Install user-provided laterite photos across the site."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"
CURSOR_ASSETS = Path(r"C:\Users\LENOVO\.cursor\projects\c-Users-LENOVO-Desktop-korvanto\assets")

PRODUCT_HERO = ROOT / "assets/images/products/korvanto-lat.png"
PRODUCT_OVERVIEW = ROOT / "assets/images/products/korvanto-lat-closeup.png"
FAMILY = ROOT / "assets/images/families/korvanto-lat.png"
LEGACY = ROOT / "assets/images/Product-Images/Laterite.png"


def find(*name_parts: str) -> Path:
    for name_part in name_parts:
        matches = [p for p in sorted(CURSOR_ASSETS.glob(f"*{name_part}*")) if p.is_file()]
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No image matching {name_parts!r} in {CURSOR_ASSETS}")


def copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    dest.write_bytes(data)
    print(f"  copied {src.name} -> {dest.relative_to(ROOT)} ({len(data)} bytes)")


def main() -> None:
    mounds = find("laterite-image-69dc3d74")
    closeup = find(
        "WhatsApp_Image_2024-12-19_at_12.28.22",
        "e93e4152-66b7-4713-9569-8bc22f0c09ad",
    )

    copy(mounds, PRODUCT_HERO)
    copy(closeup, PRODUCT_OVERVIEW)
    copy(mounds, FAMILY)
    if LEGACY.parent.exists():
        copy(mounds, LEGACY)

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for family in data.get("catalog", {}).get("families", []):
        if family.get("slug") == "korvanto-lat":
            family["image"] = "assets/images/families/korvanto-lat.png"

    for product in data.get("products", []):
        if product.get("slug") == "korvanto-lat":
            product["image"] = "assets/images/products/korvanto-lat.png"
            product["overview_image"] = "assets/images/products/korvanto-lat-closeup.png"

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Updated products-data.json for KORVANTO LAT")


if __name__ == "__main__":
    main()
