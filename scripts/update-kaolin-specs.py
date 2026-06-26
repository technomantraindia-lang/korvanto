#!/usr/bin/env python3
"""Populate full kaolin product specifications from client catalogue content."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "js" / "products-data.json"

SPEC_NOTE = (
    "Representative values for reference only. Detailed specifications are available on request — "
    "contact our export team for Technical Data Sheet (TDS) and Certificate of Analysis (COA)."
)

CUSTOM_NOTE = (
    "Custom kaolin grades and tailored specifications can be supplied according to application "
    "requirements, processing needs, and customer specifications."
)

STANDARD_PACKAGING = [
    "25 kg Bags",
    "50 kg Bags",
    "1 Jumbo Bags (FIBC)",
    "Palletized Loads",
    "Container Loads",
    "Bulk Shipments",
]

DOCUMENTATION_SPECS = [
    {"parameter": "Technical Data Sheet (TDS)", "value": "Available"},
    {"parameter": "Certificate of Analysis (COA)", "value": "Available"},
    {"parameter": "Sample Support", "value": "Available"},
    {"parameter": "Quality Verification Support", "value": "Available"},
    {"parameter": "Third-Party Testing", "value": "Available upon request"},
]

QUALITY_SPECS = [
    {"parameter": "Specification-Focused Sourcing", "value": "Confirmed"},
    {"parameter": "Quality Verification Support", "value": "Confirmed"},
    {"parameter": "Batch Consistency Monitoring", "value": "Confirmed"},
]

IDENTIFICATION = {
    "korvanto-kao-crude": [
        {"parameter": "Product Name", "value": "KORVANTO KAO CRUDE"},
        {
            "parameter": "Product Description",
            "value": "Crude Kaolin (China Clay) for Ceramic, Paint, Paper, Plastic & Industrial Applications",
        },
        {"parameter": "Mineral Type", "value": "Naturally occurring kaolin clay (China Clay)"},
        {"parameter": "Primary Composition", "value": "Hydrated aluminum silicate"},
        {"parameter": "Processing State", "value": "Raw, unprocessed — selectively mined"},
        {"parameter": "Supply Form", "value": "Dried lump form"},
        {
            "parameter": "Further Processing Suitability",
            "value": "Grinding, levigation, calcination, or direct industrial use",
        },
    ],
    "korvanto-kao-levigated-noodles": [
        {"parameter": "Product Name", "value": "KORVANTO KAO LEVIGATED NOODLES"},
        {
            "parameter": "Product Description",
            "value": "High-Purity Levigated Kaolin Noodles for Ceramic, Sanitaryware & Tile Applications",
        },
        {"parameter": "Processing", "value": "Controlled levigation — water-washed and refined"},
        {"parameter": "Supply Form", "value": "Noodle form with controlled moisture content"},
        {
            "parameter": "Impurity Removal",
            "value": "Grit, iron-bearing impurities, and unwanted minerals removed",
        },
        {
            "parameter": "Intended Use",
            "value": "Ceramic bodies, sanitaryware, vitrified tiles, porcelain, tableware, refractory",
        },
    ],
    "korvanto-kao-levigated-lumps": [
        {"parameter": "Product Name", "value": "KORVANTO KAO LEVIGATED LUMPS"},
        {
            "parameter": "Product Description",
            "value": "Water-Washed Levigated Kaolin Lumps for Ceramic & Industrial Processing",
        },
        {"parameter": "Processing", "value": "Advanced levigation — water-refined"},
        {"parameter": "Supply Form", "value": "Lump form for grinding, milling, or industrial processing"},
        {
            "parameter": "Impurity Removal",
            "value": "Coarse particles, iron impurities, and unwanted minerals removed",
        },
    ],
    "korvanto-kao-hydrous": [
        {"parameter": "Product Name", "value": "KORVANTO KAO HYDROUS"},
        {
            "parameter": "Product Description",
            "value": "Hydrous Kaolin Powder for Paint, Paper, Plastic, Rubber, Ink & Industrial Applications",
        },
        {"parameter": "Mineral Type", "value": "Naturally hydrated kaolinite"},
        {"parameter": "Crystal Structure", "value": "Retains original crystalline structure"},
        {"parameter": "Supply Form", "value": "Powder"},
        {"parameter": "Processing", "value": "Premium water-washed from carefully selected deposits"},
        {"parameter": "Quality Control", "value": "Manufactured under strict quality controls"},
        {"parameter": "Functional Role", "value": "Functional filler, extender, and performance additive"},
    ],
    "korvanto-kao-calcined": [
        {"parameter": "Product Name", "value": "KORVANTO KAO CALCINED"},
        {
            "parameter": "Product Description",
            "value": "Calcined Kaolin for Paints, Plastics, Rubber, Paper, Wire & Cable Insulation Applications",
        },
        {"parameter": "Mineral Type", "value": "Anhydrous aluminum silicate"},
        {"parameter": "Processing", "value": "Controlled calcination of high-purity kaolin"},
        {"parameter": "Supply Form", "value": "Powder"},
        {
            "parameter": "Calcination Effect",
            "value": "Removes chemically bound water; modifies kaolin crystal structure",
        },
        {
            "parameter": "Functional Role",
            "value": "High-performance extender, filler, reinforcing agent, and pigment substitute",
        },
    ],
    "korvanto-kao-metakaolin": [
        {"parameter": "Product Name", "value": "KORVANTO KAO METAKAOLIN"},
        {
            "parameter": "Product Description",
            "value": "High-Reactivity Metakaolin for Concrete, Cement, Construction Chemicals & Industrial Applications",
        },
        {"parameter": "Material Type", "value": "Highly reactive pozzolanic metakaolin"},
        {"parameter": "Source Material", "value": "Controlled calcination of high-purity kaolin clay"},
        {"parameter": "Structure", "value": "Amorphous aluminosilicate with exceptional reactivity"},
        {"parameter": "Supply Form", "value": "Powder"},
        {
            "parameter": "Supplementary Cementitious Material",
            "value": "Reacts with calcium hydroxide during cement hydration",
        },
    ],
}

METAKAOLIN_PERFORMANCE = [
    (
        "Construction Performance Specifications",
        [
            "Increases Compressive and Flexural Strength",
            "Reduces Concrete Porosity and Permeability",
            "Enhances Durability and Service Life",
            "Improves Resistance to Sulfate and Chemical Attack",
            "Reduces Efflorescence",
            "Improves Workability and Surface Finish",
            "Enhances Bond Strength in Cementitious Systems",
            "Improves Long-Term Structural Performance",
        ],
    ),
    (
        "Sustainability Specifications",
        [
            "Reduces Portland Cement Consumption",
            "Helps Lower Carbon Footprint of Concrete",
            "Supports Sustainable Construction Practices",
            "Contributes to Green Building Solutions",
        ],
    ),
    (
        "Industrial Performance Specifications",
        [
            "Improves Whiteness and Opacity in Pigments and Coatings",
            "Enhances Reinforcement in Rubber and Polymer Systems",
            "Provides Excellent Thermal and Electrical Performance in Specialty Applications",
        ],
    ),
]

SKIP_ADVANTAGES = {
    "Construction Performance",
    "Sustainability Benefits",
    "Industrial Benefits",
}


def rows_from_list(items, prefix="Product specification"):
    return [
        {"parameter": item, "value": f"{prefix} — confirmed"}
        for item in items
        if item and item not in SKIP_ADVANTAGES
    ]


def packaging_specs(items):
    cleaned = [i for i in items if i and i not in {"Available in:", "Available in"}]
    if not cleaned:
        cleaned = STANDARD_PACKAGING
    return [{"parameter": item, "value": "Available"} for item in cleaned]


def build_spec_blocks(product, performance_groups=None):
    sections = product.get("sections") or {}
    slug = product.get("slug", "")
    blocks = [
        {
            "title": "Product Identification Specifications",
            "specs": IDENTIFICATION.get(slug, []),
        },
        {
            "title": "Physical & Mineral Specifications",
            "specs": rows_from_list(sections.get("key_features") or [], "Physical specification"),
        },
    ]

    if performance_groups:
        for title, items in performance_groups:
            blocks.append(
                {
                    "title": title,
                    "specs": rows_from_list(items, "Performance specification"),
                }
            )
    else:
        blocks.append(
            {
                "title": "Performance Specifications",
                "specs": rows_from_list(
                    sections.get("product_advantages") or [], "Performance specification"
                ),
            }
        )

    blocks.extend(
        [
            {
                "title": "Packaging Specifications",
                "specs": packaging_specs(sections.get("packaging") or []),
            },
            {"title": "Documentation Specifications", "specs": DOCUMENTATION_SPECS},
            {"title": "Quality Assurance Specifications", "specs": QUALITY_SPECS},
        ]
    )
    return blocks


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = 0
    for product in data.get("products", []):
        slug = product.get("slug")
        if slug not in IDENTIFICATION:
            continue
        sections = product.setdefault("sections", {})
        performance = METAKAOLIN_PERFORMANCE if slug == "korvanto-kao-metakaolin" else None
        sections["typical_specs"] = build_spec_blocks(product, performance_groups=performance)
        sections["typical_specs_note"] = SPEC_NOTE
        sections["custom_grade_note"] = f"{SPEC_NOTE} {CUSTOM_NOTE}"
        if not sections.get("packaging"):
            sections["packaging"] = ["Available in:", *STANDARD_PACKAGING]
        updated += 1
        print(f"Updated specifications for {slug}")

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Done — {updated} kaolin products updated in {DATA_PATH.name}")


if __name__ == "__main__":
    main()
