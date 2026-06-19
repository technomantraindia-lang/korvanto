#!/usr/bin/env python3
"""Download title-matched images for KORVANTO BENTO product cards."""
from __future__ import annotations

import json
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

# Wikimedia Commons — each image chosen for the product title / application
BENTO_PRODUCT_IMAGES = {
    "korvanto-bento-drill": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Mud_tank_and_shakers_during_groundwater_well_drilling.jpg/1280px-Mud_tank_and_shakers_during_groundwater_well_drilling.jpg",
    "korvanto-bento-foundry": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg/1280px-In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg",
    "korvanto-bento-iop": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Iron_ore_pellets_from_Kiruna.jpg/1280px-Iron_ore_pellets_from_Kiruna.jpg",
    "korvanto-bento-civil": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Universal_hdd.jpg",
    "korvanto-bento-feed": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Bentonite_clay_to_make_slurry.JPG/1280px-Bentonite_clay_to_make_slurry.JPG",
    "korvanto-bento-fert": "https://upload.wikimedia.org/wikipedia/commons/5/54/Sulphur_bentonite_pastilles.jpg",
    "korvanto-bento-litter": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Bentonite_bianca_uso_lettiera_per_gatti.jpg/1280px-Bentonite_bianca_uso_lettiera_per_gatti.jpg",
    "korvanto-bento-paper-deink": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-bento-pharma": "https://upload.wikimedia.org/wikipedia/commons/5/53/Hydrated_bentonite.jpg",
    "korvanto-bento-cosmetic": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Beloon1.jpg",
    "korvanto-bento-desiccant": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Volcanic_Tuff_of_Green_River_Formation_in_Wyoming.jpg/1280px-Volcanic_Tuff_of_Green_River_Formation_in_Wyoming.jpg",
    "korvanto-bento-seal": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/A_local_lake_was_bentonite_mine_pit.JPG/1280px-A_local_lake_was_bentonite_mine_pit.JPG",
    "korvanto-bento-food": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg/1280px-Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg",
    "korvanto-bento-pencil": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Graphite-233436.jpg",
    "korvanto-bento-specialty": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Bentonite_Hills_%283723677310%29.jpg/1280px-Bentonite_Hills_%283723677310%29.jpg",
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


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    ok = 0
    for slug, url in BENTO_PRODUCT_IMAGES.items():
        rel = f"assets/images/products/{slug}.jpg"
        dest = ROOT / rel
        if download(url, dest):
            ok += 1
            for product in data.get("products", []):
                if product.get("slug") == slug:
                    product["image"] = rel
                    break
        time.sleep(3)

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {ok}/{len(BENTO_PRODUCT_IMAGES)} BENTO product images in products-data.json")


if __name__ == "__main__":
    main()
