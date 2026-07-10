#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "docs" / "product-content.txt"
OUTPUT_PATH = ROOT / "assets" / "js" / "products-data.json"


PRODUCTS: List[Tuple[str, str]] = [
    ("korvanto-bento-foundry", "KORVANTO BENTO FOUNDRY"),
    ("korvanto-bento-drill-api", "KORVANTO BENTO DRILL API"),
    ("korvanto-bento-drill-ocma", "KORVANTO BENTO DRILL OCMA"),
    ("korvanto-bento-iop", "KORVANTO BENTO IOP"),
    ("korvanto-bento-civil", "KORVANTO BENTO CIVIL"),
    ("korvanto-bento-feed", "KORVANTO BENTO FEED"),
    ("korvanto-bento-fert", "KORVANTO BENTO FERT"),
    ("korvanto-bento-litter", "KORVANTO BENTO LITTER"),
    ("korvanto-bento-paper-deink", "KORVANTO BENTO PAPER & DEINK"),
    ("korvanto-bento-pharma", "KORVANTO BENTO PHARMA"),
    ("korvanto-bento-cosmetic", "KORVANTO BENTO COSMETIC"),
    ("korvanto-bento-desiccant", "KORVANTO BENTO DESICCANT"),
    ("korvanto-bento-seal", "KORVANTO BENTO SEAL"),
    ("korvanto-bento-food", "KORVANTO BENTO FOOD"),
    ("korvanto-bento-pencil", "KORVANTO BENTO PENCIL"),
    ("korvanto-kao-crude", "KORVANTO KAO CRUDE"),
    ("korvanto-kao-levigated-noodles", "KORVANTO KAO LEVIGATED NOODLES"),
    ("korvanto-kao-levigated-lumps", "KORVANTO KAO LEVIGATED LUMPS"),
    ("korvanto-kao-hydrous", "KORVANTO KAO HYDROUS"),
    ("korvanto-kao-calcined", "KORVANTO KAO CALCINED"),
    ("korvanto-kao-metakaolin", "KORVANTO KAO METAKAOLIN"),
    ("korvanto-clay", "Korvanto Ball Clay"),
    ("korvanto-lat", "Korvanto Laterite"),
    ("korvanto-cham", "KORVANTO CHAM"),
    ("korvanto-baux", "KORVANTO BAUX"),
    ("korvanto-carbo", "KORVANTO CARBO"),
]

INTERNAL_PRODUCT_SLUGS = {"korvanto-bento-drill-api", "korvanto-bento-drill-ocma"}

CATALOG_FAMILIES = [
    {
        "slug": "korvanto-bento",
        "name": "KORVANTO BENTO™",
        "file": "korvanto-bento.html",
        "image": "assets/images/Product-Images/Bentonite.png",
        "short": "Premium bentonite grades for drilling, foundry, civil, feed, fertilizer, litter, paper, pharma, cosmetic, desiccant, seal, food, pencil and specialty applications.",
        "portfolio_meta": "15+ Grades",
        "child_slugs": [
            "korvanto-bento-drill",
            "korvanto-bento-foundry",
            "korvanto-bento-iop",
            "korvanto-bento-civil",
            "korvanto-bento-feed",
            "korvanto-bento-fert",
            "korvanto-bento-litter",
            "korvanto-bento-paper-deink",
            "korvanto-bento-pharma",
            "korvanto-bento-cosmetic",
            "korvanto-bento-desiccant",
            "korvanto-bento-seal",
            "korvanto-bento-food",
            "korvanto-bento-pencil",
            "korvanto-bento-specialty",
        ],
    },
    {
        "slug": "korvanto-kao",
        "name": "KORVANTO KAO™",
        "file": "korvanto-kao.html",
        "image": "assets/images/Product-Images/Kaolin-China-Clay.png",
        "short": "Kaolin grades including crude, levigated noodles & lumps, hydrous, calcined and metakaolin for ceramics, paints, paper, plastics and construction.",
        "portfolio_meta": "6 Product Lines",
        "child_slugs": [
            "korvanto-kao-crude",
            "korvanto-kao-levigated-noodles",
            "korvanto-kao-levigated-lumps",
            "korvanto-kao-hydrous",
            "korvanto-kao-calcined",
            "korvanto-kao-metakaolin",
        ],
    },
    {
        "slug": "korvanto-clay",
        "name": "KORVANTO CLAY™",
        "file": "korvanto-clay.html",
        "image": "assets/images/Product-Images/Ball-Clay.png",
        "short": "Korvanto Ball Clay — premium ball clay for ceramic, sanitaryware, tile, porcelain and refractory manufacturing.",
        "portfolio_meta": "Ball Clay",
        "single": "korvanto-clay",
    },
    {
        "slug": "korvanto-lat",
        "name": "KORVANTO LAT™",
        "file": "korvanto-lat.html",
        "image": "assets/images/Product-Images/Laterite.png",
        "short": "Iron and alumina-rich lateritic mineral for cement manufacturing, construction materials, road infrastructure and industrial applications.",
        "portfolio_meta": "Laterite",
        "single": "korvanto-lat",
    },
    {
        "slug": "korvanto-cham",
        "name": "KORVANTO CHAM™",
        "file": "korvanto-cham.html",
        "image": "assets/images/Product-Images/Chamotte-Calcined-Clay-Refractory-Clay.png",
        "short": "Calcined refractory chamotte — grades LF42, LF46, LF54, LF60, LF70 for fire bricks, castables and high-temperature applications.",
        "portfolio_meta": "LF42–LF70",
        "single": "korvanto-cham",
    },
    {
        "slug": "korvanto-baux",
        "name": "KORVANTO BAUX™",
        "file": "korvanto-baux.html",
        "image": "assets/images/Product-Images/Calcined-Bauxite.png",
        "short": "Calcined bauxite refractory aggregate — grades CB80, CB82, CB86 for refractory, abrasive and high-temperature industrial applications.",
        "portfolio_meta": "CB80–CB86",
        "single": "korvanto-baux",
    },
    {
        "slug": "korvanto-carbo",
        "name": "KORVANTO CARBO™",
        "file": "korvanto-carbo.html",
        "image": "assets/images/Product-Images/Coal-Additive-Lustrous-Coal.png",
        "short": "Lustrous carbon additive for green sand foundry — grades CA, LCA, HLCA, CS for improved casting surface finish and reduced defects.",
        "portfolio_meta": "CA · LCA · HLCA · CS",
        "single": "korvanto-carbo",
    },
]

PORTFOLIO_PAGE = {
    "title": "Products | Korvanto",
    "description": "Korvanto product portfolio — KORVANTO BENTO™, KAO™, CLAY™, LAT™, CHAM™, BAUX™, CARBO™ industrial mineral families for global B2B export.",
    "hero_label": "Supply Catalogue",
    "hero_title": "Seven Product Families.<br>One Export Partner.",
    "hero_lead": "Explore Korvanto's branded industrial mineral families — each supplied with specification clarity, export packaging, documentation support and B2B dispatch coordination.",
    "section_label": "Industrial Mineral Portfolio",
    "section_title": "KORVANTO™ Product Families",
    "section_lead": "Premium industrial minerals and raw materials for international B2B buyers — specification-focused sourcing, export-ready packaging and coordinated shipment execution.",
    "stats": [
        {"value": "7", "label": "Branded Families"},
        {"value": "35+", "label": "Product Grades"},
        {"value": "B2B", "label": "Export Ready"},
    ],
    "hero_image": "assets/images/Product-Images/Bentonite.png",
    "hero_badge": "Export Portfolio",
}

QUOTE_FORM = {
    "other_group_label": "Other Product Families",
    "extra_options": [
        {"value": "multiple", "label": "Multiple Products"},
    ],
}


SECTION_KEYS = [
    "overview",
    "key_benefits",
    "applications",
    "product_features",
    "product_advantages",
    "key_features",
    "available_grades",
    "packaging",
    "short_website_description",
]


SECTION_HEADER_MAP: Dict[str, Optional[str]] = {
    "Key Benefits": "key_benefits",
    "Applications": "applications",
    "Product Features": "product_features",
    "Product Advantages": "product_advantages",
    "Key Features": "key_features",
    "Available Grades": "available_grades",
    "Packaging": "packaging",
    "Short Website Description": "short_website_description",
    "Typical Performance Characteristics": "product_features",
    "End Use Applications": "applications",
    "Foundry Industry": "applications",
    "Website Category Description": None,
    # Common variants in the source content.
    "Product Benefits": "key_benefits",
    "Available Forms": "packaging",
}


def clean_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines()]


def find_drill_category_description(lines: List[str]) -> str:
    marker = "Website Category Description (for KORVANTO BENTO DRILL)"
    for idx, line in enumerate(lines):
        if line == marker:
            for next_line in lines[idx + 1 :]:
                if next_line:
                    return next_line
            break
    return ""


def split_product_blocks(lines: List[str]) -> Dict[str, List[str]]:
    header_to_slug = {header: slug for slug, header in PRODUCTS}
    header_positions: List[Tuple[int, str, str]] = []
    for idx, line in enumerate(lines):
        slug = header_to_slug.get(line)
        if slug:
            header_positions.append((idx, slug, line))

    blocks: Dict[str, List[str]] = {}
    for i, (start, slug, _) in enumerate(header_positions):
        end = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(lines)
        blocks[slug] = lines[start:end]
    return blocks


def parse_product_block(slug: str, block_lines: List[str]) -> Dict:
    meaningful_lines = [line for line in block_lines if line and line != "Bottom of Form"]
    name = meaningful_lines[0] if meaningful_lines else ""

    subtitle = ""
    cursor = 1
    if cursor < len(meaningful_lines):
        candidate = meaningful_lines[cursor]
        if candidate not in SECTION_HEADER_MAP:
            subtitle = candidate
            cursor += 1

    sections = {key: [] for key in SECTION_KEYS}
    current_section: Optional[str] = None
    seen_explicit_section = False

    for line in meaningful_lines[cursor:]:
        mapped_section = SECTION_HEADER_MAP.get(line, "__not_a_header__")
        if mapped_section != "__not_a_header__":
            current_section = mapped_section
            seen_explicit_section = True
            continue

        if not seen_explicit_section:
            sections["overview"].append(line)
            continue

        if current_section and current_section in sections:
            sections[current_section].append(line)

    return {
        "slug": slug,
        "name": name,
        "subtitle": subtitle,
        "sections": sections,
        "grades": [],
    }


def parse_drill_grade(product: Dict) -> List[Dict]:
    token = product["slug"].split("-")[-1].upper()
    return [
        {
            "grade": token,
            "name": product["name"],
            "subtitle": product["subtitle"],
            "overview": product["sections"]["overview"],
            "key_benefits": product["sections"]["key_benefits"],
            "applications": product["sections"]["applications"],
            "product_advantages": product["sections"]["product_advantages"],
        }
    ]


def parse_cham_grades(product: Dict) -> List[Dict]:
    lines = product["sections"]["available_grades"]
    grades: List[Dict] = []
    particle_sizes: List[str] = []
    category = ""
    in_particle_sizes = False

    for line in lines:
        if line == "Particle Sizes":
            in_particle_sizes = True
            continue
        if not in_particle_sizes and line == "Refractory Chamotte":
            category = line
            continue
        if in_particle_sizes:
            particle_sizes.append(line)
            continue
        if line.startswith("KORVANTO CHAM "):
            grades.append({"name": line})

    if not grades and not particle_sizes:
        return []
    return [{"category": category, "grades": grades, "particle_sizes": particle_sizes}]


def parse_baux_grades(product: Dict) -> List[Dict]:
    lines = product["sections"]["available_grades"]
    grades: List[Dict] = []
    current: Optional[Dict] = None
    mode: Optional[str] = None

    for line in lines:
        if line.startswith("KORVANTO BAUX "):
            if current:
                grades.append(current)
            current = {"grade": line, "alumina": "", "suitable_for": [], "key_benefits": []}
            mode = None
            continue

        if not current:
            continue

        if line.startswith("Al") and "%" in line:
            current["alumina"] = line
            continue
        if line == "Suitable for:":
            mode = "suitable_for"
            continue
        if line == "Key Benefits":
            mode = "key_benefits"
            continue
        if mode in ("suitable_for", "key_benefits"):
            current[mode].append(line)

    if current:
        grades.append(current)
    return grades


def parse_carbo_grades(product: Dict) -> List[Dict]:
    lines = product["sections"]["available_grades"]
    grades: List[Dict] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        if not line.startswith("KORVANTO CARBO "):
            idx += 1
            continue

        grade = {"grade": line, "description": "", "suitable_for": [], "developed_according_to": []}
        idx += 1

        if idx < len(lines) and not lines[idx].startswith("KORVANTO CARBO "):
            marker = lines[idx]
            if marker not in ("Suitable for:", "Developed according to:"):
                grade["description"] = marker
                idx += 1

        mode: Optional[str] = None
        while idx < len(lines) and not lines[idx].startswith("KORVANTO CARBO "):
            marker = lines[idx]
            if marker == "Suitable for:":
                mode = "suitable_for"
            elif marker == "Developed according to:":
                mode = "developed_according_to"
            else:
                if mode in ("suitable_for", "developed_according_to"):
                    grade[mode].append(marker)
            idx += 1

        grades.append(grade)

    return grades


def attach_grades(product: Dict) -> None:
    slug = product["slug"]
    if slug in {"korvanto-bento-drill-api", "korvanto-bento-drill-ocma"}:
        product["grades"] = parse_drill_grade(product)
    elif slug == "korvanto-cham":
        product["grades"] = parse_cham_grades(product)
    elif slug == "korvanto-baux":
        product["grades"] = parse_baux_grades(product)
    elif slug == "korvanto-carbo":
        product["grades"] = parse_carbo_grades(product)


def merge_product_sections(products: List[Dict], key: str) -> List[str]:
    from content_dedupe import applications_are_similar, benefits_are_similar

    merged: List[str] = []
    similar = applications_are_similar if key == "applications" else benefits_are_similar
    for product in products:
        for item in product.get("sections", {}).get(key, []) or []:
            if not item or item.startswith("Website Category Description"):
                continue
            if item.endswith(" is widely used in:"):
                continue
            if any(similar(item, kept) for kept in merged):
                continue
            merged.append(item)
    return merged


def build_drill_parent_product(products_by_slug: Dict[str, Dict], drill_description: str) -> Dict:
    api = products_by_slug.get("korvanto-bento-drill-api")
    ocma = products_by_slug.get("korvanto-bento-drill-ocma")
    sources = [p for p in (api, ocma) if p]
    grades = []
    for product in sources:
        grades.extend(product.get("grades") or [])
    return {
        "slug": "korvanto-bento-drill",
        "name": "KORVANTO BENTO DRILL",
        "family": "korvanto-bento",
        "page_file": "korvanto-bento-drill.html",
        "page_type": "aggregate",
        "subtitle": "API & OCMA Drilling-Grade Bentonite",
        "hero_badge": "Export Ready",
        "sections": {
            "overview": [drill_description] if drill_description else [],
            "key_benefits": merge_product_sections(sources, "key_benefits"),
            "applications": merge_product_sections(sources, "applications"),
            "product_features": merge_product_sections(sources, "product_features"),
            "product_advantages": merge_product_sections(sources, "product_advantages"),
            "key_features": [],
            "available_grades": [],
            "packaging": merge_product_sections(sources, "packaging"),
            "short_website_description": [],
        },
        "grades": grades,
    }


def build_specialty_product() -> Dict:
    return {
        "slug": "korvanto-bento-specialty",
        "name": "KORVANTO BENTO SPECIALTY",
        "family": "korvanto-bento",
        "page_file": "korvanto-bento-specialty.html",
        "page_type": "enquiry",
        "subtitle": "Specialty bentonite solutions developed for custom industrial applications. Contact our export team to discuss your specification requirements.",
        "hero_badge": "Custom Grades",
        "overview_panel": {
            "section_label": "Specialty Supply",
            "section_title": "Custom Bentonite Solutions",
            "cta_text": "Discuss Your Requirements",
            "cta_href": "request-quote.html",
        },
        "sections": {
            "overview": [
                "For specialty bentonite grades and application-specific requirements, contact Korvanto LLP. Our team supports specification-focused sourcing, quality verification, and export-ready supply coordination."
            ],
            "key_benefits": [],
            "applications": [],
            "product_features": [],
            "product_advantages": [],
            "key_features": [],
            "available_grades": [],
            "packaging": [],
            "short_website_description": [],
        },
        "grades": [],
    }


def infer_family_slug(product_slug: str) -> Optional[str]:
    for family in CATALOG_FAMILIES:
        if family.get("single") == product_slug:
            return family["slug"]
        if product_slug in family.get("child_slugs", []):
            return family["slug"]
    if product_slug.startswith("korvanto-bento"):
        return "korvanto-bento"
    if product_slug.startswith("korvanto-kao"):
        return "korvanto-kao"
    for family in CATALOG_FAMILIES:
        if product_slug == family["slug"] or product_slug.startswith(family["slug"] + "-"):
            return family["slug"]
    return None


def page_file_for_slug(product_slug: str) -> Optional[str]:
    if product_slug in INTERNAL_PRODUCT_SLUGS:
        return None
    for family in CATALOG_FAMILIES:
        if family.get("single") == product_slug:
            return family["file"]
        if product_slug in family.get("child_slugs", []):
            return f"{product_slug}.html"
    return f"{product_slug}.html"


def apply_catalog_metadata(products: List[Dict]) -> None:
    for product in products:
        slug = product["slug"]
        product["family"] = infer_family_slug(slug)
        product["page_file"] = page_file_for_slug(slug)
        if slug in INTERNAL_PRODUCT_SLUGS:
            product["page_type"] = "internal_grade"


def build_catalog() -> Dict:
    return {
        "families": CATALOG_FAMILIES,
        "portfolio_page": PORTFOLIO_PAGE,
        "quote_form": QUOTE_FORM,
    }


def build_output(source_text: str) -> Tuple[Dict, List[str]]:
    lines = clean_lines(source_text)
    blocks = split_product_blocks(lines)

    products = []
    issues: List[str] = []
    for slug, header in PRODUCTS:
        block = blocks.get(slug)
        if not block:
            issues.append(f"Missing product header in source: {header}")
            products.append(
                {
                    "slug": slug,
                    "name": header,
                    "subtitle": "",
                    "sections": {key: [] for key in SECTION_KEYS},
                    "grades": [],
                }
            )
            continue

        product = parse_product_block(slug, block)
        attach_grades(product)
        products.append(product)

    products_by_slug = {product["slug"]: product for product in products}
    drill_category_description = find_drill_category_description(lines)
    if not drill_category_description:
        issues.append("Missing drill category description marker or value.")

    drill_parent = build_drill_parent_product(products_by_slug, drill_category_description)
    specialty = build_specialty_product()
    products = [p for p in products if p["slug"] not in {drill_parent["slug"], specialty["slug"]}]
    products.extend([drill_parent, specialty])
    apply_catalog_metadata(products)

    output = {
        "catalog": build_catalog(),
        "drill_category_description": drill_category_description,
        "products": products,
        "product_count": len(products),
    }
    return output, issues


def main() -> int:
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    output_data, issues = build_output(source_text)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Parsed products: {output_data['product_count']}")
    print(f"Output JSON: {OUTPUT_PATH}")
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Issues: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
