#!/usr/bin/env python3
"""Add product-level typical_specs where grade tables are not available."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"

TYPICAL_SPECS: dict[str, list] = {
    "korvanto-lat": [
        {"parameter": "Fe₂O₃ Content", "value": "15 – 45% (typical)"},
        {"parameter": "Al₂O₃ Content", "value": "10 – 30% (typical)"},
        {"parameter": "SiO₂ Content", "value": "5 – 25% (typical)"},
        {"parameter": "Moisture", "value": "≤ 8%"},
        {"parameter": "Form", "value": "Lumps / Crushed / Powder"},
        {"parameter": "Particle Size", "value": "Customized sizes available"},
    ],
    "korvanto-clay": [
        {"parameter": "Primary Mineral", "value": "Kaolinite with quartz & mica"},
        {"parameter": "Plasticity", "value": "High"},
        {"parameter": "Particle Size", "value": "Fine-grained"},
        {"parameter": "Moisture", "value": "As per export requirement"},
        {"parameter": "Form", "value": "Lumps / Powder / Processed clay"},
        {"parameter": "Application", "value": "Ceramic, sanitaryware, tile, porcelain, refractory"},
    ],
    "korvanto-cham": [
        {
            "title": "KORVANTO CHAM LF42",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "≥ 42%"},
                {"parameter": "Application", "value": "General refractory & ceramic applications"},
            ],
        },
        {
            "title": "KORVANTO CHAM LF46",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "≥ 46%"},
                {"parameter": "Application", "value": "Medium-duty refractory products"},
            ],
        },
        {
            "title": "KORVANTO CHAM LF54",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "≥ 54%"},
                {"parameter": "Application", "value": "High-temperature refractory applications"},
            ],
        },
        {
            "title": "KORVANTO CHAM LF60",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "≥ 60%"},
                {"parameter": "Application", "value": "High-alumina refractory & kiln applications"},
            ],
        },
        {
            "title": "KORVANTO CHAM LF70",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "≥ 70%"},
                {"parameter": "Application", "value": "Critical high-temperature refractory service"},
            ],
        },
    ],
    "korvanto-baux": [
        {
            "title": "KORVANTO BAUX CB80",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "~80%"},
                {"parameter": "Application", "value": "High-duty fire bricks, castables, general refractory"},
            ],
        },
        {
            "title": "KORVANTO BAUX CB82",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "~82%"},
                {"parameter": "Application", "value": "Premium refractory bricks, kiln furniture, castables"},
            ],
        },
        {
            "title": "KORVANTO BAUX CB86",
            "specs": [
                {"parameter": "Al₂O₃ Content", "value": "~86%"},
                {"parameter": "Application", "value": "Steel plants, cement kilns, glass furnaces"},
            ],
        },
    ],
    "korvanto-kao-crude": [
        {"parameter": "Mineral Type", "value": "Natural kaolin (China clay)"},
        {"parameter": "Form", "value": "Raw lumps / crude clay"},
        {"parameter": "Plasticity", "value": "Good to excellent"},
        {"parameter": "Whiteness", "value": "Natural — varies by deposit"},
        {"parameter": "Moisture", "value": "As mined / as agreed"},
    ],
    "korvanto-kao-levigated-noodles": [
        {"parameter": "Processing", "value": "Water-washed / levigated"},
        {"parameter": "Form", "value": "Noodles"},
        {"parameter": "Purity", "value": "High — grit & iron reduced"},
        {"parameter": "Plasticity", "value": "Excellent"},
        {"parameter": "Moisture", "value": "Controlled"},
    ],
    "korvanto-kao-levigated-lumps": [
        {"parameter": "Processing", "value": "Water-washed / levigated"},
        {"parameter": "Form", "value": "Lumps"},
        {"parameter": "Purity", "value": "High — coarse particles & iron reduced"},
        {"parameter": "Whiteness", "value": "Enhanced vs crude kaolin"},
        {"parameter": "Moisture", "value": "Controlled"},
    ],
    "korvanto-kao-hydrous": [
        {"parameter": "Mineral Type", "value": "Hydrous kaolin (kaolinite)"},
        {"parameter": "Form", "value": "Powder"},
        {"parameter": "Brightness", "value": "High"},
        {"parameter": "Particle Size", "value": "Fine, controlled distribution"},
        {"parameter": "Moisture", "value": "≤ 1.5% (typical for powder)"},
    ],
    "korvanto-kao-calcined": [
        {"parameter": "Mineral Type", "value": "Calcined kaolin (anhydrous aluminum silicate)"},
        {"parameter": "Form", "value": "Powder"},
        {"parameter": "Brightness", "value": "High"},
        {"parameter": "Opacity", "value": "Enhanced vs hydrous kaolin"},
        {"parameter": "Moisture", "value": "Low — thermally processed"},
    ],
    "korvanto-kao-metakaolin": [
        {"parameter": "Material Type", "value": "Metakaolin (pozzolanic)"},
        {"parameter": "Form", "value": "Powder"},
        {"parameter": "Reactivity", "value": "High pozzolanic activity"},
        {"parameter": "Particle Size", "value": "Fine"},
        {"parameter": "Application", "value": "Cement, concrete, construction chemicals"},
    ],
    "korvanto-bento-food": [
        {"parameter": "Grade", "value": "Food-grade bentonite"},
        {"parameter": "Primary Use", "value": "Beverage clarification & filtration"},
        {"parameter": "Mineral", "value": "Montmorillonite-rich clay"},
        {"parameter": "Form", "value": "Powder"},
        {"parameter": "Documentation", "value": "TDS & COA available on request"},
    ],
    "korvanto-bento-specialty": [
        {"parameter": "Supply Type", "value": "Custom / application-specific grades"},
        {"parameter": "Specifications", "value": "Developed to customer requirements"},
        {"parameter": "Documentation", "value": "TDS & COA available on request"},
        {"parameter": "Support", "value": "Specification-focused sourcing & export coordination"},
    ],
}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = 0
    for product in data.get("products", []):
        slug = product.get("slug")
        if slug not in TYPICAL_SPECS:
            continue
        sections = product.setdefault("sections", {})
        if sections.get("typical_specs"):
            continue
        sections["typical_specs"] = TYPICAL_SPECS[slug]
        updated += 1
        print(f"  added typical_specs -> {slug}")

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated} products in products-data.json")


if __name__ == "__main__":
    main()
