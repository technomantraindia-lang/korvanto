#!/usr/bin/env python3
"""Sync Available Forms from client catalogue into products-data.json."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "js" / "products-data.json"

# Source: final description-1.docx — Available Forms & physical supply formats
FORM_UPDATES = {
    "korvanto-lat": {
        "available_forms": [
            "Lumps",
            "Crushed Material",
            "Powder",
            "Customized Sizes Available",
        ],
        "packaging": [],
        "available_forms_lead": (
            "Naturally occurring laterite supplied in multiple particle sizes for "
            "cement manufacturing, construction materials, and road infrastructure."
        ),
    },
    "korvanto-cham": {
        "available_forms": [
            "Powder Form",
            "Granular Form",
            "Customized Sizing",
        ],
        "packaging": [
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
        "available_forms_lead": (
            "Calcined refractory chamotte supplied in powder and granular formats with "
            "customized sizing for fire bricks, castables, and high-temperature applications."
        ),
    },
    "korvanto-baux": {
        "available_forms": [
            "Powder Form",
            "Granular Form",
            "Customized Particle Sizes",
        ],
        "packaging": [
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
        "available_forms_lead": (
            "Calcined bauxite refractory aggregate available in powder and granular forms "
            "with customized particle sizes for demanding industrial applications."
        ),
    },
    "korvanto-kao-crude": {
        "available_forms": ["Dried Lump Form"],
        "packaging": [
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
        "available_forms_lead": (
            "Crude kaolin (China clay) supplied in dried lump form for ceramic, paint, "
            "paper, plastic, and general industrial processing."
        ),
    },
    "korvanto-bento-pencil": {
        "available_forms": ["Fine Powder Grade"],
        "packaging": [
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
            "Jumbo Bags (FIBC)",
            "Customized Packaging Available",
        ],
        "available_forms_lead": (
            "Premium bentonite for pencil lead manufacturing, supplied as a finely "
            "processed powder grade for binding and extrusion applications."
        ),
    },
    "korvanto-clay": {
        "available_forms": [
            "Powder Form",
            "Noodle Form",
            "Filter Cake",
            "Custom Processing Available",
        ],
        "packaging": [],
        "available_forms_lead": (
            "Processed and supplied in multiple industrial forms to match ceramic, "
            "sanitaryware, and refractory manufacturing requirements."
        ),
    },
}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = 0
    for product in data.get("products", []):
        slug = product.get("slug", "")
        if slug not in FORM_UPDATES:
            continue
        patch = FORM_UPDATES[slug]
        sections = product.setdefault("sections", {})
        sections["available_forms"] = patch["available_forms"]
        sections["packaging"] = patch["packaging"]
        sections["available_forms_lead"] = patch["available_forms_lead"]
        updated += 1
        print(f"Updated {slug}")

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Done — {updated} products updated.")


if __name__ == "__main__":
    main()
