#!/usr/bin/env python3
"""Download application-matched images for every Korvanto product and grade."""
from __future__ import annotations

import json
import shutil
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"
GRADES_DIR = ROOT / "assets/images/grades"
PRODUCTS_DIR = ROOT / "assets/images/products"
FAMILIES_DIR = ROOT / "assets/images/families"

W = "https://upload.wikimedia.org/wikipedia/commons"

# Every product card / detail page — image must match the application name
PRODUCT_APPLICATION: dict[str, str] = {
    # Bentonite applications
    "korvanto-bento-drill": f"{W}/thumb/a/a6/Mud_tank_and_shakers_during_groundwater_well_drilling.jpg/1280px-Mud_tank_and_shakers_during_groundwater_well_drilling.jpg",
    "korvanto-bento-drill-api": f"{W}/thumb/a/a6/Mud_tank_and_shakers_during_groundwater_well_drilling.jpg/1280px-Mud_tank_and_shakers_during_groundwater_well_drilling.jpg",
    "korvanto-bento-drill-ocma": f"{W}/thumb/a/a6/Mud_tank_and_shakers_during_groundwater_well_drilling.jpg/1280px-Mud_tank_and_shakers_during_groundwater_well_drilling.jpg",
    "korvanto-bento-foundry": f"{W}/thumb/b/b8/In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg/1280px-In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg",
    "korvanto-bento-iop": f"{W}/thumb/c/cc/Iron_ore_pellets_from_Kiruna.jpg/1280px-Iron_ore_pellets_from_Kiruna.jpg",
    "korvanto-bento-civil": f"{W}/d/d1/Universal_hdd.jpg",
    "korvanto-bento-feed": f"{W}/6/6f/Cattle_feed.JPG",
    "korvanto-bento-fert": f"{W}/5/54/Sulphur_bentonite_pastilles.jpg",
    "korvanto-bento-litter": f"{W}/thumb/8/81/Bentonite_bianca_uso_lettiera_per_gatti.jpg/1280px-Bentonite_bianca_uso_lettiera_per_gatti.jpg",
    "korvanto-bento-paper-deink": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-bento-pharma": f"{W}/5/53/Hydrated_bentonite.jpg",
    "korvanto-bento-cosmetic": f"{W}/thumb/b/ba/Bentonite_clay_to_make_slurry.JPG/1280px-Bentonite_clay_to_make_slurry.JPG",
    "korvanto-bento-desiccant": f"{W}/thumb/8/81/Bentonite_bianca_uso_lettiera_per_gatti.jpg/1280px-Bentonite_bianca_uso_lettiera_per_gatti.jpg",
    "korvanto-bento-seal": f"{W}/thumb/7/7d/A_local_lake_was_bentonite_mine_pit.JPG/1280px-A_local_lake_was_bentonite_mine_pit.JPG",
    "korvanto-bento-food": f"{W}/thumb/4/44/Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg/1280px-Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg",
    "korvanto-bento-pencil": "assets/images/products/bento pencil/korvanto-bento-pencil-02.png",
    "korvanto-bento-specialty": f"{W}/thumb/4/44/Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg/1280px-Creating_a_bentonite_slurry_for_fining_after_wine_pressing.jpg",
    # Kaolin applications
    "korvanto-kao-crude": f"{W}/1/11/Kaolin_%28China_Clay%29_-_geograph.org.uk_-_3178670.jpg",
    "korvanto-kao-levigated-noodles": f"{W}/4/46/Making_pottery_in_Bagh.jpg",
    "korvanto-kao-levigated-lumps": f"{W}/thumb/8/82/China_clay_drying_in_stacks_-_geograph.org.uk_-_403432.jpg/1280px-China_clay_drying_in_stacks_-_geograph.org.uk_-_403432.jpg",
    "korvanto-kao-hydrous": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-kao-calcined": f"{W}/7/72/China_clay_spoil_heaps_in_the_eighties_-_geograph.org.uk_-_1512218.jpg",
    "korvanto-kao-metakaolin": f"{W}/2/2f/Concreting_at_Brabazon_Avenue_-_geograph.org.uk_-_514548.jpg",
    # Other minerals
    "korvanto-clay": f"{W}/3/37/Frozen_spoil%2C_Newbridge_ball_clay_quarry_-_geograph.org.uk_-_1654551.jpg",
    "korvanto-cham": f"{W}/4/4d/Fire_brick.jpg",
    "korvanto-baux": f"{W}/e/e0/Bauxite_with_core_of_unweathered_rock.jpg",
    "korvanto-carbo": f"{W}/thumb/b/b8/In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg/1280px-In-stream_inoculation_addition_while_molten_cast_iron_is_poured_to_a_green_sand_mold_in_a_foundry_in_Bangladesh.jpg",
}

FAMILY_APPLICATION: dict[str, str] = {
    "korvanto-bento": PRODUCT_APPLICATION["korvanto-bento-drill"],
    "korvanto-kao": PRODUCT_APPLICATION["korvanto-kao-levigated-noodles"],
    "korvanto-clay": PRODUCT_APPLICATION["korvanto-clay"],
    "korvanto-cham": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-baux": PRODUCT_APPLICATION["korvanto-baux"],
    "korvanto-carbo": f"{W}/1/10/Anthracite_coal.jpg",
}

# Grade card images — path relative to assets/images/grades/
GRADE_APPLICATION: dict[str, str] = {
    "korvanto-bento-drill/api.jpg": PRODUCT_APPLICATION["korvanto-bento-drill"],
    "korvanto-bento-drill/ocma.jpg": PRODUCT_APPLICATION["korvanto-bento-drill"],
    "korvanto-bento-drill/ocma-plus.jpg": PRODUCT_APPLICATION["korvanto-bento-drill"],
    "korvanto-bento-drill-api/api.jpg": PRODUCT_APPLICATION["korvanto-bento-drill-api"],
    "korvanto-bento-drill-ocma/ocma.jpg": PRODUCT_APPLICATION["korvanto-bento-drill-ocma"],
    "korvanto-bento-foundry/f-100.jpg": PRODUCT_APPLICATION["korvanto-bento-foundry"],
    "korvanto-bento-foundry/f-200.jpg": PRODUCT_APPLICATION["korvanto-bento-foundry"],
    "korvanto-bento-iop/i-100.jpg": PRODUCT_APPLICATION["korvanto-bento-iop"],
    "korvanto-bento-iop/i-200.jpg": PRODUCT_APPLICATION["korvanto-bento-iop"],
    "korvanto-bento-iop/i-300.jpg": PRODUCT_APPLICATION["korvanto-bento-iop"],
    "korvanto-bento-civil/c-33.jpg": PRODUCT_APPLICATION["korvanto-bento-civil"],
    "korvanto-bento-civil/c-45.jpg": PRODUCT_APPLICATION["korvanto-bento-civil"],
    "korvanto-bento-feed/feed.jpg": PRODUCT_APPLICATION["korvanto-bento-feed"],
    "korvanto-bento-fert/ag-100.jpg": PRODUCT_APPLICATION["korvanto-bento-fert"],
    "korvanto-bento-fert/ag-200.jpg": PRODUCT_APPLICATION["korvanto-bento-fert"],
    "korvanto-bento-fert/ag-300.jpg": PRODUCT_APPLICATION["korvanto-bento-fert"],
    "korvanto-bento-litter/l-25.jpg": PRODUCT_APPLICATION["korvanto-bento-litter"],
    "korvanto-bento-paper-deink/paper-325.jpg": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-bento-paper-deink/deink-100.jpg": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-bento-pharma/pharma-ip.jpg": PRODUCT_APPLICATION["korvanto-bento-pharma"],
    "korvanto-bento-cosmetic/cosmetic-90.jpg": PRODUCT_APPLICATION["korvanto-bento-cosmetic"],
    "korvanto-bento-desiccant/desiccant-05.jpg": PRODUCT_APPLICATION["korvanto-bento-desiccant"],
    "korvanto-bento-desiccant/desiccant-12.jpg": PRODUCT_APPLICATION["korvanto-bento-desiccant"],
    "korvanto-bento-desiccant/desiccant-24.jpg": PRODUCT_APPLICATION["korvanto-bento-desiccant"],
    "korvanto-bento-seal/seal-p.jpg": PRODUCT_APPLICATION["korvanto-bento-seal"],
    "korvanto-bento-seal/seal-g.jpg": PRODUCT_APPLICATION["korvanto-bento-seal"],
    "korvanto-bento-pencil/pencil.jpg": "assets/images/products/bento pencil/korvanto-bento-pencil-02.png",
    "korvanto-bento-specialty/wine.jpg": PRODUCT_APPLICATION["korvanto-bento-food"],
    "korvanto-bento-specialty/bleach.jpg": f"{W}/thumb/6/6d/AV_Nackawic_pulp_and_paper_mill.jpg/1280px-AV_Nackawic_pulp_and_paper_mill.jpg",
    "korvanto-bento-specialty/agro.jpg": PRODUCT_APPLICATION["korvanto-bento-fert"],
    "korvanto-bento-specialty/detox.jpg": PRODUCT_APPLICATION["korvanto-bento-cosmetic"],
    "korvanto-bento-specialty/cera.jpg": PRODUCT_APPLICATION["korvanto-kao-levigated-noodles"],
    "korvanto-bento-specialty/custom.jpg": f"{W}/thumb/b/ba/Bentonite_clay_to_make_slurry.JPG/1280px-Bentonite_clay_to_make_slurry.JPG",
    "korvanto-cham/korvanto-cham-lf42.jpg": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-cham/korvanto-cham-lf46.jpg": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-cham/korvanto-cham-lf54.jpg": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-cham/korvanto-cham-lf60.jpg": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-cham/korvanto-cham-lf70.jpg": PRODUCT_APPLICATION["korvanto-cham"],
    "korvanto-baux/korvanto-baux-cb80.jpg": PRODUCT_APPLICATION["korvanto-baux"],
    "korvanto-baux/korvanto-baux-cb82.jpg": f"{W}/thumb/7/72/China_clay_spoil_heaps_in_the_eighties_-_geograph.org.uk_-_1512218.jpg/1280px-China_clay_spoil_heaps_in_the_eighties_-_geograph.org.uk_-_1512218.jpg",
    "korvanto-baux/korvanto-baux-cb86.jpg": f"{W}/4/4d/Fire_brick.jpg",
    "korvanto-carbo/korvanto-carbo-ca.jpg": PRODUCT_APPLICATION["korvanto-carbo"],
    "korvanto-carbo/korvanto-carbo-lca.jpg": PRODUCT_APPLICATION["korvanto-carbo"],
    "korvanto-carbo/korvanto-carbo-hlca.jpg": PRODUCT_APPLICATION["korvanto-carbo"],
    "korvanto-carbo/korvanto-carbo-cs.jpg": PRODUCT_APPLICATION["korvanto-carbo"],
}

LEGACY_FAMILY_FILES = {
    "korvanto-bento": "assets/images/Product-Images/Bentonite.jpg",
    "korvanto-kao": "assets/images/Product-Images/Kaolin-China-Clay.jpg",
    "korvanto-clay": "assets/images/Product-Images/Ball-Clay.jpg",
    "korvanto-cham": "assets/images/Product-Images/Chamotte-Calcined-Clay-Refractory-Clay.jpg",
    "korvanto-baux": "assets/images/Product-Images/Calcined-Bauxite.jpg",
    "korvanto-carbo": "assets/images/Product-Images/Coal-Additive-Lustrous-Coal.jpg",
}


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "KorvantoImageSync/2.0"}
    ctx = ssl.create_default_context()
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
                data = resp.read()
            if len(data) < 4000:
                print(f"  skip small: {dest.name}", flush=True)
                return False
            dest.write_bytes(data)
            print(f"  saved {dest.relative_to(ROOT)}", flush=True)
            return True
        except Exception as exc:
            if attempt < 4:
                wait = 15 * (attempt + 1)
                print(f"  retry {dest.name} in {wait}s ({exc})", flush=True)
                time.sleep(wait)
            else:
                print(f"  failed {dest.name}: {exc}", flush=True)
                return False
    return False


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    grades_ok = 0
    products_ok = 0
    families_ok = 0

    print("=== Grade application images ===", flush=True)
    for rel, url in GRADE_APPLICATION.items():
        dest = GRADES_DIR / Path(rel)
        if download(url, dest):
            grades_ok += 1
        time.sleep(2)

    print("=== Product application images ===", flush=True)
    for slug, url in PRODUCT_APPLICATION.items():
        dest = PRODUCTS_DIR / f"{slug}.jpg"
        if download(url, dest):
            products_ok += 1
            for product in data.get("products", []):
                if product.get("slug") == slug:
                    product["image"] = f"assets/images/products/{slug}.jpg"
        time.sleep(2)

    # Laterite — user photo
    lat_png = PRODUCTS_DIR / "korvanto-lat.png"
    if lat_png.is_file():
        rel = "assets/images/products/korvanto-lat.png"
        for product in data.get("products", []):
            if product.get("slug") == "korvanto-lat":
                product["image"] = rel
        for family in data.get("catalog", {}).get("families", []):
            if family.get("slug") == "korvanto-lat":
                family["image"] = rel
        print("  kept laterite user image", flush=True)

    print("=== Family portfolio images ===", flush=True)
    for slug, url in FAMILY_APPLICATION.items():
        dest = FAMILIES_DIR / f"{slug}.jpg"
        if download(url, dest):
            families_ok += 1
            rel = f"assets/images/families/{slug}.jpg"
            for family in data.get("catalog", {}).get("families", []):
                if family.get("slug") == slug:
                    family["image"] = rel
            legacy = LEGACY_FAMILY_FILES.get(slug)
            if legacy:
                (ROOT / legacy).write_bytes(dest.read_bytes())
        time.sleep(2)

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Done: {grades_ok} grades, {products_ok} products, {families_ok} families.",
        flush=True,
    )


if __name__ == "__main__":
    main()
