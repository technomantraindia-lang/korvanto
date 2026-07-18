#!/usr/bin/env python3
"""Map family and product images to correct files; fix portfolio copy."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

FAMILY_IMAGES = {
    "korvanto-bento": "assets/images/Product-Images/Bentonite.jpg",
    "korvanto-kao": "assets/images/Product-Images/Kaolin-China-Clay.jpg",
    "korvanto-clay": "assets/images/Product-Images/Ball-Clay.jpg",
    "korvanto-lat": "assets/images/products/korvanto-lat.png",
    "korvanto-cham": "assets/images/Product-Images/Chamotte-Calcined-Clay-Refractory-Clay.jpg",
    "korvanto-baux": "assets/images/Product-Images/Calcined-Bauxite.jpg",
    "korvanto-carbo": "assets/images/Product-Images/Coal-Additive-Lustrous-Coal.jpg",
}

FAMILY_SHORT = {
    "korvanto-clay": "Premium ball clay for ceramic, sanitaryware, tile, porcelain and refractory manufacturing.",
    "korvanto-carbo": "Korvanto Carbon lustrous carbon additive for green sand foundry — grades CA, LCA, HLCA and CS.",
}

PORTFOLIO_META = {
    "korvanto-bento": "Drilling · Foundry · Civil · Feed & More",
    "korvanto-kao": "Crude · Levigated · Hydrous · Calcined",
    "korvanto-clay": "Ball Clay",
    "korvanto-lat": "Laterite",
    "korvanto-cham": "LF42 · LF46 · LF54 · LF60 · LF70",
    "korvanto-baux": "CB80 · CB82 · CB86",
    "korvanto-carbo": "ELITE · PREMIUM · ADVANCE · STANDARD",
}


def resolve_product_image(slug: str) -> str | None:
    for ext in (".jpg", ".png"):
        path = ROOT / "assets/images/products" / f"{slug}{ext}"
        if path.is_file():
            return f"assets/images/products/{slug}{ext}"
    return None


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for family in data.get("catalog", {}).get("families", []):
        slug = family.get("slug", "")
        if slug in FAMILY_IMAGES:
            family["image"] = FAMILY_IMAGES[slug]
        if slug in FAMILY_SHORT:
            family["short"] = FAMILY_SHORT[slug]
        if slug in PORTFOLIO_META:
            family["portfolio_meta"] = PORTFOLIO_META[slug]

    portfolio = data.setdefault("catalog", {}).setdefault("portfolio_page", {})
    portfolio["hero_image"] = FAMILY_IMAGES["korvanto-bento"]

    linked = 0
    for product in data.get("products", []):
        slug = product.get("slug", "")
        img = resolve_product_image(slug)
        if img:
            product["image"] = img
            linked += 1
        elif product.get("family") in FAMILY_IMAGES:
            product["image"] = FAMILY_IMAGES[product["family"]]

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced family images, portfolio hero, and {linked} product images.")


if __name__ == "__main__":
    main()
