#!/usr/bin/env python3
"""Download title-matched images for KORVANTO KAO product cards."""
from __future__ import annotations

import json
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

# Wikimedia Commons — kaolin / china clay only (no unrelated uploads)
KAO_PRODUCT_IMAGES = {
    "korvanto-kao-crude": "https://upload.wikimedia.org/wikipedia/commons/1/11/Kaolin_%28China_Clay%29_-_geograph.org.uk_-_3178670.jpg",
    "korvanto-kao-levigated-noodles": "https://upload.wikimedia.org/wikipedia/commons/4/42/Kaolinite_-_USGS_bws00008.jpg",
    "korvanto-kao-levigated-lumps": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Kazn%C4%9Bjov_kaolin_quarry_2021_%2801%29.jpg/1280px-Kazn%C4%9Bjov_kaolin_quarry_2021_%2801%29.jpg",
    "korvanto-kao-hydrous": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Mus%C3%A9um_de_Nantes_-_178_-_Kaolinite_%28Nantes%2C_France%29.jpg/1280px-Mus%C3%A9um_de_Nantes_-_178_-_Kaolinite_%28Nantes%2C_France%29.jpg",
    "korvanto-kao-calcined": "https://upload.wikimedia.org/wikipedia/commons/7/72/China_clay_spoil_heaps_in_the_eighties_-_geograph.org.uk_-_1512218.jpg",
    "korvanto-kao-metakaolin": "https://upload.wikimedia.org/wikipedia/commons/7/70/Microstructure-of-metakaolin-through-field-emission-scanning-electron-microscope-FESEM-showing-particle-size-distributio.jpg",
}

KAO_FAMILY_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Kaolin_auf_Lipari.JPG/1280px-Kaolin_auf_Lipari.JPG"


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "KorvantoImageSync/1.0"}
    ctx = ssl.create_default_context()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
                data = resp.read()
            if len(data) < 8000:
                print(f"  skip small: {dest.name} ({len(data)} bytes)")
                return False
            dest.write_bytes(data)
            print(f"  saved {dest.relative_to(ROOT)} ({len(data)} bytes)")
            return True
        except Exception as exc:
            if attempt < 3:
                wait = 12 * (attempt + 1)
                print(f"  retry in {wait}s: {dest.name} ({exc})")
                time.sleep(wait)
            else:
                print(f"  failed {dest.name}: {exc}")
                return False
    return False


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    ok = 0

    if download(KAO_FAMILY_IMAGE, ROOT / "assets/images/families/korvanto-kao.jpg"):
        for family in data.get("catalog", {}).get("families", []):
            if family.get("slug") == "korvanto-kao":
                family["image"] = "assets/images/families/korvanto-kao.jpg"
        legacy = ROOT / "assets/images/Product-Images/Kaolin-China-Clay.jpg"
        if legacy.parent.exists():
            legacy.write_bytes((ROOT / "assets/images/families/korvanto-kao.jpg").read_bytes())
        time.sleep(3)

    for slug, url in KAO_PRODUCT_IMAGES.items():
        rel = f"assets/images/products/{slug}.jpg"
        if download(url, ROOT / rel):
            ok += 1
            for product in data.get("products", []):
                if product.get("slug") == slug:
                    product["image"] = rel
                    break
        time.sleep(3)

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {ok}/{len(KAO_PRODUCT_IMAGES)} KAO product images")


if __name__ == "__main__":
    main()
