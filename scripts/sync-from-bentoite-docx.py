#!/usr/bin/env python3
"""Sync non-bento product details from bentoite products-1.docx content into products-data.json."""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "js" / "products-data.json"

DOC_NOTE = (
    "Representative values for reference only. Detailed specifications are available on request — "
    "contact our export team for Technical Data Sheet (TDS) and Certificate of Analysis (COA)."
)

DOC_BLOCKS = [
    {"parameter": "Technical Data Sheet (TDS)", "value": "Available"},
    {"parameter": "Certificate of Analysis (COA)", "value": "Available"},
    {"parameter": "Sample Support", "value": "Available"},
    {"parameter": "Custom Grades / Specifications", "value": "Available upon request"},
]

PACKAGING_STD = [
    {"parameter": "25 kg Bags", "value": "Available"},
    {"parameter": "50 kg Bags", "value": "Available"},
    {"parameter": "1 Jumbo Bags (FIBC)", "value": "Available"},
    {"parameter": "Palletized Loads", "value": "Available"},
    {"parameter": "Container Loads", "value": "Available"},
    {"parameter": "Bulk Shipments", "value": "Available"},
]


def spec_table(title, rows):
    return {"title": title, "specs": [{"parameter": p, "value": v} for p, v in rows]}


def kao_specs(name, desc, form, rows, apps):
    blocks = [
        spec_table(
            "Product Identification Specifications",
            [
                ("Product Name", name),
                ("Product Description", desc),
                ("Supply Form", form),
            ],
        ),
        spec_table("Typical Specifications", rows),
        spec_table("Packaging Specifications", [(p, v) for p, v in [
            ("25 kg Bags", "Available"),
            ("50 kg Bags", "Available"),
            ("1 Jumbo Bags (FIBC)", "Available"),
            ("Palletized Loads", "Available"),
            ("Container Loads", "Available"),
            ("Bulk Shipments", "Available"),
        ]]),
        spec_table("Documentation Specifications", [(b["parameter"], b["value"]) for b in DOC_BLOCKS]),
    ]
    app_text = ", ".join(apps)
    return {
        "subtitle": desc,
        "overview": [
            f"{name}™ is {desc.lower()} supplied for {app_text.lower()} applications.",
        ],
        "applications": apps,
        "typical_specs": blocks,
        "typical_specs_note": DOC_NOTE,
        "custom_grade_note": DOC_NOTE,
    }


UPDATES = {
    "korvanto-kao-crude": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO CRUDE"),
                    (
                        "Product Description",
                        "Crude Kaolin (China Clay) for Ceramic, Paint, Paper, Plastic & Industrial Applications",
                    ),
                    ("Mineral Type", "Naturally occurring kaolin clay (China Clay)"),
                    ("Primary Composition", "Hydrated aluminum silicate"),
                    ("Processing State", "Raw, unprocessed — selectively mined"),
                    ("Supply Form", "Dried lump form"),
                    (
                        "Further Processing Suitability",
                        "Grinding, levigation, calcination, or direct industrial use",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "60 – 75"),
                    ("Moisture (%)", "8 – 15"),
                    ("Al₂O₃ (%)", "28 – 36"),
                    ("Fe₂O₃ (%)", "0.5 – 2.5"),
                    ("SiO₂ (%)", "45 – 55"),
                    ("Particle Size", "Natural Ore"),
                    ("pH", "5.0 – 7.0"),
                ],
            ),
        ],
        "available_forms": ["Crude Kaolin Lumps", "Crude Kaolin Powder"],
        "available_forms_lead": (
            "KORVANTO KAO CRUDE™ raw kaolin ore supplied in lump and powder forms."
        ),
        "packaging": [
            "Available in:",
            "Dried Lump Form",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
    },
    # crude forms from catalogue family section
    "korvanto-kao-hydrous": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO HYDROUS"),
                    (
                        "Product Description",
                        "Hydrous Kaolin Powder for Paint, Paper, Plastic, Rubber, Ink & Industrial Applications",
                    ),
                    ("Mineral Type", "Naturally hydrated kaolinite"),
                    ("Crystal Structure", "Retains original crystalline structure"),
                    ("Supply Form", "Powder"),
                    ("Processing", "Premium water-washed from carefully selected deposits"),
                    ("Quality Control", "Manufactured under strict quality controls"),
                    (
                        "Functional Role",
                        "Functional filler, extender, and performance additive",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "78 – 88"),
                    ("Moisture (%)", "≤ 1.5"),
                    ("Al₂O₃ (%)", "34 – 38"),
                    ("Fe₂O₃ (%)", "0.3 – 1.2"),
                    ("SiO₂ (%)", "45 – 50"),
                    ("Residue on 325 Mesh (%)", "≤ 1.0"),
                    ("pH", "5.0 – 7.5"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-kao-levigated-noodles": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO LEVIGATED NOODLES"),
                    (
                        "Product Description",
                        "High-Purity Levigated Kaolin Noodles for Ceramic, Sanitaryware & Tile Applications",
                    ),
                    ("Processing", "Controlled levigation — water-washed and refined"),
                    ("Supply Form", "Noodle form with controlled moisture content"),
                    (
                        "Impurity Removal",
                        "Grit, iron-bearing impurities, and unwanted minerals removed",
                    ),
                    (
                        "Intended Use",
                        "Ceramic bodies, sanitaryware, vitrified tiles, porcelain, tableware, refractory",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "82 – 90"),
                    ("Moisture (%)", "10 – 18"),
                    ("Al₂O₃ (%)", "34 – 38"),
                    ("Fe₂O₃ (%)", "0.3 – 1.0"),
                    ("SiO₂ (%)", "45 – 50"),
                    ("Plasticity", "High"),
                    ("pH", "5.0 – 7.5"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-kao-levigated-lumps": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO LEVIGATED LUMPS"),
                    (
                        "Product Description",
                        "Water-Washed Levigated Kaolin Lumps for Ceramic & Industrial Processing",
                    ),
                    ("Processing", "Advanced levigation — water-refined"),
                    (
                        "Supply Form",
                        "Lump form for grinding, milling, or industrial processing",
                    ),
                    (
                        "Impurity Removal",
                        "Coarse particles, iron impurities, and unwanted minerals removed",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "82 – 90"),
                    ("Moisture (%)", "8 – 15"),
                    ("Al₂O₃ (%)", "34 – 38"),
                    ("Fe₂O₃ (%)", "0.3 – 1.0"),
                    ("SiO₂ (%)", "45 – 50"),
                    ("Plasticity", "High"),
                    ("pH", "5.0 – 7.5"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-kao-spray": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO SPRAY"),
                    (
                        "Product Description",
                        "Spray Dried Kaolin for Ceramic Bodies, Pressed Tiles & Sanitaryware Applications",
                    ),
                    ("Processing", "Spray dried from refined kaolin slurry"),
                    ("Supply Form", "Spray dried powder"),
                    (
                        "Key Characteristics",
                        "Controlled particle structure, uniform moisture, excellent flow",
                    ),
                    (
                        "Intended Use",
                        "Ceramic bodies, pressed tiles, sanitaryware, and technical ceramic pressing applications",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "84 – 92"),
                    ("Moisture (%)", "5 – 8"),
                    ("Al₂O₃ (%)", "34 – 38"),
                    ("Fe₂O₃ (%)", "0.2 – 1.0"),
                    ("SiO₂ (%)", "45 – 50"),
                    ("Flowability", "Excellent"),
                    ("Bulk Density (g/cc)", "0.8 – 1.2"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-kao-calcined": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO CALCINED"),
                    (
                        "Product Description",
                        "Calcined Kaolin for Paints, Plastics, Rubber, Paper, Wire & Cable Insulation Applications",
                    ),
                    ("Mineral Type", "Anhydrous aluminum silicate"),
                    ("Processing", "Controlled calcination of high-purity kaolin"),
                    ("Supply Form", "Powder"),
                    (
                        "Calcination Effect",
                        "Removes chemically bound water; modifies kaolin crystal structure",
                    ),
                    (
                        "Functional Role",
                        "High-performance extender, filler, reinforcing agent, and pigment substitute",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "88 – 95"),
                    ("Moisture (%)", "≤ 0.5"),
                    ("Al₂O₃ (%)", "42 – 46"),
                    ("Fe₂O₃ (%)", "0.2 – 1.0"),
                    ("SiO₂ (%)", "50 – 55"),
                    ("LOI (%)", "≤ 1.5"),
                    ("pH", "6.0 – 8.0"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-kao-metakaolin": {
        "typical_specs": [
            spec_table(
                "Product Identification Specifications",
                [
                    ("Product Name", "KORVANTO KAO METAKAOLIN"),
                    (
                        "Product Description",
                        "High-Reactivity Metakaolin for Concrete, Cement, Construction Chemicals & Industrial Applications",
                    ),
                    ("Material Type", "Highly reactive pozzolanic metakaolin"),
                    ("Source Material", "Controlled calcination of high-purity kaolin clay"),
                    ("Structure", "Amorphous aluminosilicate with exceptional reactivity"),
                    ("Supply Form", "Powder"),
                    (
                        "Supplementary Cementitious Material",
                        "Reacts with calcium hydroxide during cement hydration",
                    ),
                ],
            ),
            spec_table(
                "Typical Specifications",
                [
                    ("Brightness (%)", "80 – 90"),
                    ("Moisture (%)", "≤ 1.0"),
                    ("Al₂O₃ (%)", "40 – 45"),
                    ("Fe₂O₃ (%)", "0.5 – 1.5"),
                    ("SiO₂ (%)", "50 – 55"),
                    ("LOI (%)", "≤ 2.0"),
                    ("Pozzolanic Activity", "High"),
                ],
            ),
        ],
        "packaging": [
            "Available in:",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags (FIBC)",
            "Palletized Loads",
            "Container Loads",
            "Bulk Shipments",
        ],
    },
    "korvanto-clay": {
        "typical_specs": [
            spec_table(
                "Chemical Specifications (Ceramic Industry Grade)",
                [
                    ("Fe₂O₃", "1.5% max."),
                    ("TiO₂", "1.5% max."),
                    ("Fe₂O₃ + TiO₂ (by weight)", "2.75% max."),
                    ("Al₂O₃", "25% min."),
                    ("L.O.I.", "10.5% min."),
                ],
            ),
            spec_table(
                "Physical Specifications (Ceramic Industry Grade)",
                [
                    ("Fired Color", "Light gray or light cream"),
                    ("Purity", "Free from any foreign matter"),
                    ("Plasticity", "Lightly plastic when wet"),
                ],
            ),
        ],
        "typical_specs_note": DOC_NOTE,
        "available_forms": [
            "Powder Form",
            "Noodle Form",
            "Filter Cake",
            "Custom Processing Available",
        ],
        "available_forms_lead": "Processed and supplied in multiple industrial forms to match ceramic, sanitaryware, and refractory manufacturing requirements.",
    },
    "korvanto-lat": {
        "typical_specs": [
            spec_table(
                "Typical Chemical Composition",
                [
                    ("Al₂O₃ (Alumina)", "32% – 34%"),
                    ("Fe₂O₃ (Iron Oxide)", "30% – 33%"),
                    ("SiO₂ (Silica)", "6% – 8%"),
                    ("TiO₂ (Titanium Dioxide)", "4% – 5%"),
                    ("Moisture", "10% Max"),
                    ("Size", "0 – 150 mm"),
                ],
            ),
            spec_table(
                "Physical & General Properties",
                [
                    ("Form", "Lump"),
                    ("Material", "Laterite of High alumina"),
                    ("Packaging Size", "Loose"),
                    ("Grade", "30% to 35%"),
                    ("Color", "Red, Pink and Brown"),
                    ("Country of Origin", "Made in India"),
                ],
            ),
            spec_table(
                "Minimum Guaranteed Specifications",
                [
                    ("Fe₂O₃ (Iron Oxide)", "30% to 35% (minimum)"),
                    ("Al₂O₃ (Alumina)", "30% to 35% (minimum)"),
                    ("SiO₂ (Silica)", "Maximum 7%"),
                    ("Size", "0 mm to 150 mm (lump form)"),
                ],
            ),
            spec_table(
                "Documentation",
                [
                    ("Technical Data Sheet (TDS)", "Available"),
                    ("Certificate of Analysis (COA)", "Available"),
                    ("Sample Support", "Available"),
                    ("Custom Specifications", "Available"),
                ],
            ),
        ],
        "typical_specs_note": DOC_NOTE,
    },
    "korvanto-cham": {
        "typical_specs": [
            spec_table(
                "KORVANTO CHAM LF42™",
                [
                    ("Application", "Castables, Ceramics, Foundry"),
                    ("Al₂O₃", "~42%"),
                    ("PCE (SK)", "32"),
                    ("Fe₂O₃", "< 1.25%"),
                    ("Sizes Available", "0–1 mm, 1–3 mm, 3–5 mm, 200 Mesh"),
                ],
            ),
            spec_table(
                "KORVANTO CHAM LF46™",
                [
                    ("Application", "High-Duty Castables, Kiln Furniture"),
                    ("Al₂O₃", "~46%"),
                    ("PCE (SK)", "32"),
                    ("Fe₂O₃", "< 1.5%"),
                    ("Sizes Available", "0–1 mm, 1–3 mm, 3–5 mm, 200 Mesh"),
                ],
            ),
            spec_table(
                "KORVANTO CHAM LF54™",
                [
                    ("Application", "Dense Refractory Bricks, Glass Furnace, Cement Industry"),
                    ("Al₂O₃", "~54%"),
                    ("PCE (SK)", "32"),
                    ("Fe₂O₃", "< 2.0%"),
                    ("Sizes Available", "0–1 mm, 1–3 mm, 3–5 mm, 200 Mesh"),
                ],
            ),
            spec_table(
                "KORVANTO CHAM LF60™",
                [
                    ("Application", "Steel Plants, Premium Castables"),
                    ("Al₂O₃", "~60%"),
                    ("PCE (SK)", "32"),
                    ("Fe₂O₃", "< 2.0%"),
                    ("Sizes Available", "0–1 mm, 1–3 mm, 3–5 mm, 200 Mesh"),
                ],
            ),
            spec_table(
                "KORVANTO CHAM LF70™",
                [
                    ("Application", "Glass Furnaces, Steel Tundish, Export Refractories"),
                    ("Al₂O₃", "~70%"),
                    ("PCE (SK)", "32"),
                    ("Fe₂O₃", "< 3.0%"),
                    ("Sizes Available", "0–1 mm, 1–3 mm, 3–5 mm, 200 Mesh"),
                ],
            ),
        ],
        "typical_specs_note": DOC_NOTE,
        "packaging": [
            "Available in:",
            "Powder Form",
            "Granular Form",
            "Customized Sizing",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
    },
    "korvanto-baux": {
        "typical_specs": [
            spec_table(
                "KORVANTO BAUX CB80™",
                [
                    ("Al₂O₃", "~80%"),
                    ("Type", "Calcined Bauxite"),
                    ("Application", "Refractory Bricks, Monolithics"),
                    ("Features", "High Thermal Shock Resistance"),
                    ("Applications", "Refractory Bricks; Castables; Monolithic Refractories; Kiln Linings"),
                ],
            ),
            spec_table(
                "KORVANTO BAUX CB82™",
                [
                    ("Al₂O₃", "~82%"),
                    ("Type", "Premium Calcined Bauxite"),
                    ("Application", "Kiln Furniture, High-Strength Castables"),
                    ("Features", "Enhanced Alumina Purity"),
                    ("Applications", "Premium Castables; Kiln Furniture; Refractory Shapes; Export Refractory Products"),
                ],
            ),
            spec_table(
                "KORVANTO BAUX CB86™",
                [
                    ("Al₂O₃", "≥ 86%"),
                    ("Type", "Ultra High Alumina Calcined Bauxite"),
                    ("Application", "Steel, Glass & Cement Industries"),
                    ("Features", "Maximum Refractoriness"),
                    ("Applications", "Steel Plants; Tundish Refractories; Glass Furnaces; Cement Kilns; Critical Refractory Applications"),
                ],
            ),
        ],
        "typical_specs_note": DOC_NOTE,
        "packaging": [
            "Available in:",
            "Powder Form",
            "Granular Form",
            "Customized Particle Sizes",
            "25 kg Bags",
            "50 kg Bags",
            "1 Jumbo Bags",
            "Bulk Supply",
        ],
    },
    "korvanto-carbo": {
        "typical_specs": [
            spec_table(
                "KORVANTO CARBO CA™",
                [
                    ("Volatile Matter", "55 – 65%"),
                    ("Ash", "≤ 6.0%"),
                    ("Fixed Carbon", "By Difference"),
                    ("Applications", "Premium Foundry Moulding Sand; Precision Castings; High Surface Finish Requirements"),
                ],
            ),
            spec_table(
                "KORVANTO CARBO LCA™",
                [
                    ("Volatile Matter", "50 – 55%"),
                    ("Ash", "≤ 8.0%"),
                    ("Fixed Carbon", "By Difference"),
                    ("Applications", "Green Sand Foundries; Grey Iron Castings; General Foundry Use"),
                ],
            ),
            spec_table(
                "KORVANTO CARBO HLCA™",
                [
                    ("Volatile Matter", "40 – 50%"),
                    ("Ash", "≤ 7.0%"),
                    ("Fixed Carbon", "By Difference"),
                    ("Applications", "SG Iron Castings; Grey Iron Castings; High Carbon Metal Casting"),
                ],
            ),
            spec_table(
                "KORVANTO CARBO CS™",
                [
                    ("Volatile Matter", "45 – 55%"),
                    ("Ash", "≤ 9.0%"),
                    ("Fixed Carbon", "By Difference"),
                    ("Applications", "Standard Foundry Applications; General Casting Operations; Moulding Sand Additive"),
                ],
            ),
        ],
        "typical_specs_note": DOC_NOTE,
    },
}


def merge_typical_specs(sections, patch_tables):
    existing = {
        t["title"]: t
        for t in sections.get("typical_specs", [])
        if isinstance(t, dict) and t.get("title")
    }
    order = [
        t["title"]
        for t in sections.get("typical_specs", [])
        if isinstance(t, dict) and t.get("title")
    ]
    for table in patch_tables:
        title = table.get("title")
        if not title:
            continue
        existing[title] = deepcopy(table)
        if title not in order:
            order.append(title)
    sections["typical_specs"] = [existing[title] for title in order if title in existing]


def apply_update(product, patch):
    if "subtitle" in patch:
        product["subtitle"] = patch["subtitle"]
    sections = product.setdefault("sections", {})
    for key in (
        "overview",
        "applications",
        "typical_specs_note",
        "custom_grade_note",
        "available_forms",
        "available_forms_lead",
        "packaging",
    ):
        if key in patch:
            sections[key] = deepcopy(patch[key])
    if "typical_specs" in patch:
        merge_typical_specs(sections, patch["typical_specs"])
    if "grades" in patch:
        product["grades"] = deepcopy(patch["grades"])


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = []
    for product in data.get("products", []):
        slug = product.get("slug")
        if slug in UPDATES and not slug.startswith("korvanto-bento"):
            apply_update(product, UPDATES[slug])
            updated.append(slug)

    # Update family short descriptions
    for family in data.get("catalog", {}).get("families", []):
        if family.get("slug") == "korvanto-clay":
            family["short"] = "Premium ball clay for ceramic, sanitaryware, tile, porcelain and refractory manufacturing."
        elif family.get("slug") == "korvanto-lat":
            family["short"] = "KORVANTO LAT™ laterite for cement, steel, metallurgical, construction, and refractory applications."
        elif family.get("slug") == "korvanto-cham":
            family["short"] = "Calcined refractory chamotte — grades LF42, LF46, LF54, LF60, LF70 for fire bricks, castables and high-temperature applications."
        elif family.get("slug") == "korvanto-baux":
            family["short"] = "Premium calcined bauxite for refractory, abrasive and high-temperature applications — grades CB80, CB82, CB86."
        elif family.get("slug") == "korvanto-carbo":
            family["short"] = "Premium lustrous carbon additive for green sand foundry applications — grades CA, LCA, HLCA, and CS."

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated products:", ", ".join(updated))


if __name__ == "__main__":
    main()
