#!/usr/bin/env python3
"""Quick patch for application images that failed in bulk sync."""
from __future__ import annotations

import json
import shutil
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"
W = "https://upload.wikimedia.org/wikipedia/commons"

PATCHES: dict[str, str] = {
    # rel path from assets/images/ -> url
    "grades/korvanto-bento-feed/feed.jpg": f"{W}/6/6f/Cattle_feed.JPG",
    "grades/korvanto-bento-paper-deink/deink-100.jpg": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "grades/korvanto-bento-specialty/cera.jpg": f"{W}/4/46/Making_pottery_in_Bagh.jpg",
    "grades/korvanto-cham/korvanto-cham-lf42.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "grades/korvanto-cham/korvanto-cham-lf46.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "grades/korvanto-cham/korvanto-cham-lf54.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "grades/korvanto-cham/korvanto-cham-lf60.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "grades/korvanto-cham/korvanto-cham-lf70.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "products/korvanto-bento-feed.jpg": f"{W}/6/6f/Cattle_feed.JPG",
    "products/korvanto-kao-levigated-noodles.jpg": f"{W}/4/46/Making_pottery_in_Bagh.jpg",
    "products/korvanto-kao-hydrous.jpg": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "products/korvanto-kao-metakaolin.jpg": f"{W}/2/2f/Concreting_at_Brabazon_Avenue_-_geograph.org.uk_-_514548.jpg",
    "products/korvanto-clay.jpg": f"{W}/3/37/Frozen_spoil%2C_Newbridge_ball_clay_quarry_-_geograph.org.uk_-_1654551.jpg",
    "products/korvanto-cham.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "products/korvanto-baux.jpg": f"{W}/e/e0/Bauxite_with_core_of_unweathered_rock.jpg",
    "families/korvanto-kao.jpg": f"{W}/4/46/Making_pottery_in_Bagh.jpg",
    "families/korvanto-clay.jpg": f"{W}/3/37/Frozen_spoil%2C_Newbridge_ball_clay_quarry_-_geograph.org.uk_-_1654551.jpg",
    "families/korvanto-cham.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "families/korvanto-baux.jpg": f"{W}/e/e0/Bauxite_with_core_of_unweathered_rock.jpg",
}

PRODUCT_SLUGS = {
    "products/korvanto-bento-feed.jpg": "korvanto-bento-feed",
    "products/korvanto-kao-levigated-noodles.jpg": "korvanto-kao-levigated-noodles",
    "products/korvanto-kao-hydrous.jpg": "korvanto-kao-hydrous",
    "products/korvanto-kao-metakaolin.jpg": "korvanto-kao-metakaolin",
    "products/korvanto-clay.jpg": "korvanto-clay",
    "products/korvanto-cham.jpg": "korvanto-cham",
    "products/korvanto-baux.jpg": "korvanto-baux",
}

FAMILY_SLUGS = {
    "families/korvanto-kao.jpg": "korvanto-kao",
    "families/korvanto-clay.jpg": "korvanto-clay",
    "families/korvanto-cham.jpg": "korvanto-cham",
    "families/korvanto-baux.jpg": "korvanto-baux",
}


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "KorvantoImageSync/2.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
                data = resp.read()
            if len(data) < 4000:
                return False
            dest.write_bytes(data)
            print(f"  patched {dest.relative_to(ROOT)}", flush=True)
            return True
        except Exception as exc:
            if attempt < 2:
                time.sleep(10)
            else:
                print(f"  failed {dest.name}: {exc}", flush=True)
    return False


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    for rel, url in PATCHES.items():
        dest = ROOT / "assets/images" / rel
        if download(url, dest):
            slug = PRODUCT_SLUGS.get(rel)
            if slug:
                for product in data.get("products", []):
                    if product.get("slug") == slug:
                        product["image"] = f"assets/images/{rel}"
            fam = FAMILY_SLUGS.get(rel)
            if fam:
                for family in data.get("catalog", {}).get("families", []):
                    if family.get("slug") == fam:
                        family["image"] = f"assets/images/{rel}"
        time.sleep(1)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
