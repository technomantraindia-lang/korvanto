#!/usr/bin/env python3
"""Apply client full product display names across products-data.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

FAMILY_NAMES = {
    "korvanto-bento": "Korvanto Bentonite",
    "korvanto-kao": "Korvanto Kaolin (China Clay)",
    "korvanto-clay": "Korvanto Ball Clay",
    "korvanto-lat": "Korvanto Laterite",
    "korvanto-cham": "Korvanto Chamotte",
    "korvanto-baux": "Korvanto Bauxite",
    "korvanto-carbo": "Korvanto Carbon",
}

PRODUCT_NAMES = {
    "korvanto-bento-drill": "Korvanto Bento Drilling",
    "korvanto-bento-drill-api": "Korvanto Bento Drilling API",
    "korvanto-bento-drill-ocma": "Korvanto Bento Drilling OCMA",
    "korvanto-bento-foundry": "Korvanto Bento Foundry",
    "korvanto-bento-iop": "Korvanto Bento Iron Ore Palltetization",
    "korvanto-bento-civil": "Korvanto Bento Civil",
    "korvanto-bento-feed": "Korvanto Bento Cattle Feed",
    "korvanto-bento-fert": "Korvanto Bento Fertilizer",
    "korvanto-bento-litter": "Korvanto Bento Cat Litter",
    "korvanto-bento-paper-deink": "Korvanto Bento Paper & Deink",
    "korvanto-bento-pharma": "Korvanto Bento Pharma",
    "korvanto-bento-cosmetic": "Korvanto Bento Cosmetic",
    "korvanto-bento-desiccant": "Korvanto Bento Desiccant",
    "korvanto-bento-seal": "Korvanto Bento Pond Seal",
    "korvanto-bento-food": "Korvanto Bento Food",
    "korvanto-bento-pencil": "Korvanto Bento Pencil",
    "korvanto-bento-specialty": "Korvanto Bento Specialty",
    "korvanto-kao-crude": "Korvanto Crude Kaolin",
    "korvanto-kao-levigated-noodles": "Korvanto Levigated Kaolin Noodles",
    "korvanto-kao-levigated-lumps": "Korvanto Levigated Kaolin Lumps",
    "korvanto-kao-hydrous": "Korvanto Hydrous Kaolin",
    "korvanto-kao-calcined": "Korvanto Calcined Kaolin",
    "korvanto-kao-metakaolin": "Korvanto Meta Kaolin",
    "korvanto-clay": "Korvanto Ball Clay",
    "korvanto-lat": "Korvanto Laterite",
    "korvanto-cham": "Korvanto Chamotte",
    "korvanto-baux": "Korvanto Bauxite",
    "korvanto-carbo": "Korvanto Carbon",
}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for family in data.get("catalog", {}).get("families", []):
        slug = family.get("slug")
        if slug in FAMILY_NAMES:
            family["name"] = FAMILY_NAMES[slug]

    portfolio = data.setdefault("catalog", {}).setdefault("portfolio_page", {})
    portfolio["description"] = (
        "Korvanto product portfolio — Bentonite, Kaolin, Ball Clay, Laterite, "
        "Chamotte, Bauxite and Carbon industrial mineral families for global B2B export."
    )
    portfolio["section_title"] = "Korvanto Product Families"

    updated = 0
    for product in data.get("products", []):
        slug = product.get("slug")
        if slug in PRODUCT_NAMES:
            product["name"] = PRODUCT_NAMES[slug]
            updated += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(FAMILY_NAMES)} family names and {updated} product names.")


if __name__ == "__main__":
    main()
