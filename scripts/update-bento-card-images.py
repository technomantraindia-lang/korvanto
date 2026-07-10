#!/usr/bin/env python3
"""Sync application-matched images for Korvanto Bento product cards and detail pages."""
from __future__ import annotations

import json
import shutil
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"
PRODUCTS_DIR = ROOT / "assets/images/products"

# Prefer curated grade images; fall back to Wikimedia for strong application visuals.
BENTO_IMAGE_SOURCES: dict[str, str] = {
    "korvanto-bento-drill": "url:https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Mud_tank_and_shakers_during_groundwater_well_drilling.jpg/1280px-Mud_tank_and_shakers_during_groundwater_well_drilling.jpg",
    "korvanto-bento-drill-api": "assets/images/grades/korvanto-bento-drill-api/api.jpg",
    "korvanto-bento-drill-ocma": "assets/images/grades/korvanto-bento-drill-ocma/ocma.jpg",
    "korvanto-bento-foundry": "url:https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg/1280px-In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg",
    "korvanto-bento-iop": "url:https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Iron_ore_pellets_from_Kiruna.jpg/1280px-Iron_ore_pellets_from_Kiruna.jpg",
    "korvanto-bento-civil": "url:https://upload.wikimedia.org/wikipedia/commons/d/d1/Universal_hdd.jpg",
    "korvanto-bento-feed": "assets/images/grades/korvanto-bento-feed/feed.jpg",
    "korvanto-bento-fert": "assets/images/grades/korvanto-bento-fert/ag-300.jpg",
    "korvanto-bento-litter": "assets/images/grades/korvanto-bento-litter/l-25.jpg",
    "korvanto-bento-paper-deink": "assets/images/grades/korvanto-bento-paper-deink/deink-100.jpg",
    "korvanto-bento-pharma": "assets/images/grades/korvanto-bento-pharma/pharma-ip.jpg",
    "korvanto-bento-cosmetic": "assets/images/grades/korvanto-bento-cosmetic/cosmetic-90.jpg",
    "korvanto-bento-desiccant": "assets/images/grades/korvanto-bento-desiccant/desiccant-24.jpg",
    "korvanto-bento-seal": "assets/images/grades/korvanto-bento-seal/seal-p.jpg",
    "korvanto-bento-food": "assets/images/grades/korvanto-bento-specialty/wine.jpg",
    "korvanto-bento-pencil": "assets/images/products/bento pencil/korvanto-bento-pencil-02.png",
    "korvanto-bento-specialty": "assets/images/grades/korvanto-bento-specialty/custom.jpg",
}


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "KorvantoImageSync/1.0"}
    ctx = ssl.create_default_context()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
                data = resp.read()
            if len(data) < 5000:
                print(f"  skip small: {dest.name}")
                return False
            dest.write_bytes(data)
            print(f"  saved {dest.relative_to(ROOT)}")
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


def copy_local(source_rel: str, dest: Path) -> bool:
    source = ROOT / source_rel
    if not source.is_file():
        print(f"  missing source: {source_rel}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"  copied {source_rel} -> {dest.relative_to(ROOT)}")
    return True


def sync_image(slug: str, source: str, dest: Path) -> bool:
    if source.startswith("url:"):
        return download(source[4:], dest)
    return copy_local(source, dest)


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    ok = 0

    for slug, source in BENTO_IMAGE_SOURCES.items():
        rel = f"assets/images/products/{slug}.jpg"
        dest = ROOT / rel
        if sync_image(slug, source, dest):
            ok += 1
            for product in data.get("products", []):
                if product.get("slug") == slug:
                    product["image"] = rel
                    break
        time.sleep(1)

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {ok}/{len(BENTO_IMAGE_SOURCES)} BENTO product images in products-data.json")


if __name__ == "__main__":
    main()
