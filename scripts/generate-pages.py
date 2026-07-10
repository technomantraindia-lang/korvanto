#!/usr/bin/env python3
"""Generate Korvanto product family and detail HTML pages from products-data.json."""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_dedupe import (
    benefits_are_similar,
    benefits_look_like_features,
    dedupe_applications,
    dedupe_benefits,
    filter_items,
    format_company_prose,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "js" / "products-data.json"
FAQ_PATH = ROOT / "assets" / "js" / "product-faqs.json"
GRADES_IMAGE_DIR = ROOT / "assets" / "images" / "grades"
HEADER_PATH = ROOT / "components" / "header.html"
QUOTE_PATH = ROOT / "request-quote.html"
PRODUCTS_PAGE_PATH = ROOT / "products.html"
SEARCH_INDEX_PATH = ROOT / "assets" / "js" / "product-search-index.json"
MEGA_MENU_START = "<!-- catalog:mega-menu:start -->"
MEGA_MENU_END = "<!-- catalog:mega-menu:end -->"
QUOTE_OPTIONS_START = "<!-- catalog:quote-options:start -->"
QUOTE_OPTIONS_END = "<!-- catalog:quote-options:end -->"


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


_product_faqs = None


def load_product_faqs():
    global _product_faqs
    if _product_faqs is None:
        if FAQ_PATH.exists():
            _product_faqs = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
        else:
            _product_faqs = {}
    return _product_faqs


def get_families(data):
    return data.get("catalog", {}).get("families", [])


def get_family(data, family_slug):
    for family in get_families(data):
        if family["slug"] == family_slug:
            return family
    return None


def esc(text):
    return html.escape(str(text or ""))


def esc_prose(text):
    return esc(format_company_prose(text))


def mega_menu_child_label(name):
    """Drop redundant Korvanto prefix — family column header already shows the brand."""
    label = str(name or "").strip()
    if label.lower().startswith("korvanto "):
        label = label[9:].strip()
    return label


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(description)}">
  <title>{esc(title)} | Korvanto</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/shared/base.css">
  <link rel="stylesheet" href="assets/css/shared/header.css">
  <link rel="stylesheet" href="assets/css/shared/footer.css">
  <link rel="stylesheet" href="assets/css/shared/premium-inner.css">
  <link rel="stylesheet" href="assets/css/pages/inner.css">
  <link rel="stylesheet" href="assets/css/pages/product-detail.css">
  <link rel="stylesheet" href="assets/css/pages/products-catalog.css">
  <link rel="stylesheet" href="assets/css/pages/home.css">
  <link rel="stylesheet" href="assets/css/shared/responsive.css">
  <link rel="stylesheet" href="assets/css/shared/mobile.css">
</head>
<body class="inner-premium product-page">"""


def foot():
    return """  <div id="footer-placeholder"></div>
  <script src="assets/js/product-search.js?v=6"></script>
  <script src="assets/js/header-search.js?v=1"></script>
  <script src="assets/js/main.js?v=14"></script>
</body>
</html>"""


SPEC_SECTION_TITLE = "Representative Technical Specifications"
SPEC_TABLE_NOTE = (
    "Representative values shown above. Full Technical Data Sheet (TDS), "
    "Certificate of Analysis (COA), and additional documentation are available upon request."
)

STANDARD_PACKAGING_OPTIONS = [
    "25 kg",
    "50 kg",
    "Jumbo Bag",
    "Palletized Load",
    "Containerized Shipping",
    "Bulk Shipments",
    "Custom Packing Available",
]

STANDARD_PACKAGING_FAQ_ANSWER = (
    "Korvanto LLP supplies products in the following export-ready packing options:\n"
    "25 kg\n"
    "50 kg\n"
    "Jumbo Bag\n"
    "Palletized Load\n"
    "Containerized Shipping\n"
    "Bulk Shipments\n"
    "Custom Packing Available"
)

STANDARD_PACKAGING_DOCS_FAQ_ANSWER = (
    STANDARD_PACKAGING_FAQ_ANSWER
    + "\n\nTechnical Data Sheets (TDS), Certificate of Analysis (COA), Safety Data Sheets (SDS), "
    "and other export documentation are available upon request."
)

BTN_ICON_QUOTE = (
    '<span class="btn-icon" aria-hidden="true">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>'
    '<path d="M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2z"/>'
    '<path d="M9 12h6"/><path d="M9 16h4"/>'
    "</svg></span>"
)

BTN_ICON_DOC = (
    '<span class="btn-icon" aria-hidden="true">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
    '<path d="M14 2v6h6"/><path d="M9 15l2 2 4-4"/>'
    "</svg></span>"
)

SHARED_KEY_BENEFITS = [
    "API / OCMA compliant",
    "High Yield",
    "Excellent Gel Strength",
    "Low Fluid Loss",
    "Borehole Stabilization",
    "Efficient Cuttings Suspension",
    "Easy Mixing",
    "Thermal Stability",
    "Consistent Batch Quality",
]

DRILLING_BENEFIT_SLUGS = {
    "korvanto-bento-drill",
    "korvanto-bento-drill-api",
    "korvanto-bento-drill-ocma",
}

GRADE_NAME_BENEFIT_RE = re.compile(
    r"(?:"
    r"\b(?:High Purity )?[A-Za-z]+ Grade (?:Bentonite|Kaolin)\b"
    r"|\bKORVANTO\b"
    r"|\b(?:API|OCMA)[ /-]?\d*\s*(?:Grade|compliant)\b"
    r"|\bGrade [A-Z]{1,4}(?:-\d+)?\b"
    r"|\b(?:PHARMA-IP|AG-\d+|C-\d+)\b"
    r"|\b(?:KORVANTO )?BENTO (?:FEED|FERT|IOP)\b"
    r"|\b(?:Fine|Premium|Standard|Economy) (?:Powder )?Grade\b"
    r"|\b(?:Mesh Sizes|Particle Sizes) and Grades\b"
    r")",
    re.I,
)

BENEFIT_REPLACEMENTS = {
    "API / OCMA compliant": "Meets API and OCMA performance standards",
    "API 13A compliant quality": "Meets API 13A performance standards",
    "OCMA-compliant quality": "Meets OCMA performance standards",
    "High Purity Cosmetic Grade Bentonite": "High Purity Mineral Composition",
    "High Purity Food Grade Bentonite": "High Purity Mineral Composition",
    "High Purity Bentonite": "High Purity Mineral Composition",
}


def sanitize_benefit_text(text):
    text = (text or "").strip()
    return BENEFIT_REPLACEMENTS.get(text, text)


def is_grade_name_benefit(text):
    if not text:
        return True
    if GRADE_NAME_BENEFIT_RE.search(text):
        lowered = text.lower()
        if "meets " in lowered and "performance" in lowered:
            return False
        return True
    return False


def sanitize_benefits(items, slug=None):
    cleaned = []
    for item in filter_items(items or []):
        item = sanitize_benefit_text(item)
        if not item or is_grade_name_benefit(item):
            continue
        if slug not in DRILLING_BENEFIT_SLUGS and item in SHARED_KEY_BENEFITS:
            continue
        cleaned.append(item)
    return dedupe_benefits(cleaned)


def resolve_product_benefits(product):
    sections = product.get("sections") or {}
    key_benefits = filter_items(sections.get("key_benefits") or [])
    product_advantages = filter_items(sections.get("product_advantages") or [])
    key_features = filter_items(sections.get("key_features") or [])

    if key_benefits and not benefits_look_like_features(key_benefits, key_features):
        items = key_benefits
    elif product_advantages:
        items = product_advantages
    else:
        items = key_benefits
    return sanitize_benefits(items, product.get("slug"))


def merge_compulsory_benefits(items):
    merged = dedupe_benefits(items)
    for shared in SHARED_KEY_BENEFITS:
        if any(benefits_are_similar(shared, kept) for kept in merged):
            continue
        merged.append(shared)
    return merged


def filter_overview_paragraphs(items):
    return [i for i in (items or []) if i and not i.startswith("Website Category Description")]


def section_header(label, title, centered=True):
    center = " inner-section-head--center pd-section-head" if centered else " pd-section-head"
    return f"""<header class="inner-section-head{center}">
          <p class="section-label">{esc(label)}</p>
          <h2 class="section-title">{esc(title)}</h2>
        </header>"""


def benefits_section(product=None, items=None, slug=None):
    if product is not None:
        items = resolve_product_benefits(product)
        slug = product.get("slug")
    else:
        items = sanitize_benefits(items, slug)
    if slug in DRILLING_BENEFIT_SLUGS:
        items = merge_compulsory_benefits(items)
    if not items:
        return ""
    cards = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        cards += f"""<article class="pd-benefit-card tilt-card reveal{delay}">
            <span class="pd-benefit-num">{i:02d}</span>
            <p>{esc(item)}</p>
          </article>"""
    return f"""<section class="section pd-section pd-section--navy" id="pdBenefits">
      <div class="container">
        {section_header("Performance", "Key Benefits")}
        <div class="pd-benefits-grid reveal reveal-delay-1">{cards}</div>
      </div>
    </section>"""


def applications_section(items):
    items = dedupe_applications(items)
    if not items:
        return ""
    chips = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        chips += f"""<article class="pd-app-chip tilt-card reveal{delay}">
            <span class="pd-app-dot" aria-hidden="true"></span>
            <span>{esc(item)}</span>
          </article>"""
    return f"""<section class="section pd-section pd-section--mesh" id="pdApplications">
      <div class="container">
        {section_header("Industry Use", "Applications")}
        <div class="pd-apps-grid reveal reveal-delay-1">{chips}</div>
      </div>
    </section>"""


def features_section(items):
    items = filter_items(items)
    if not items:
        return ""
    cards = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        cards += f"""<article class="pd-feature-card tilt-card reveal{delay}">
            <span class="pd-card-shine" aria-hidden="true"></span>
            <p>{esc(item)}</p>
          </article>"""
    return f"""<section class="section pd-section pd-section--white" id="pdFeatures">
      <div class="container">
        {section_header("Technical Profile", "Product Features")}
        <div class="pd-features-grid reveal reveal-delay-1">{cards}</div>
      </div>
    </section>"""


def normalize_spec_row(item):
    if not isinstance(item, dict):
        return None
    param = item.get("parameter") or item.get("property") or item.get("name")
    value = item.get("value") or item.get("spec") or item.get("typical")
    if param and value is not None:
        return {"parameter": str(param), "value": str(value)}
    return None


def rows_from_spec_list(items):
    return [row for row in (normalize_spec_row(item) for item in (items or [])) if row]


def blocks_from_grade(grade):
    grade_label = grade.get("name") or grade.get("grade") or "Grade"
    subtitle = grade.get("subtitle") or grade.get("description") or ""
    title = grade_label if not subtitle else f"{grade_label} — {subtitle}"

    if grade.get("spec_sections"):
        blocks = []
        for section in grade["spec_sections"]:
            rows = rows_from_spec_list(section.get("specs"))
            if rows:
                blocks.append({"title": section.get("title") or title, "specs": rows})
        return blocks or None

    rows = rows_from_spec_list(grade.get("specifications") or grade.get("specs"))
    if not rows:
        rows = []
        if grade.get("alumina"):
            rows.append({"parameter": "Al₂O₃ Content", "value": grade["alumina"]})
        if grade.get("description"):
            rows.append({"parameter": "Grade Type", "value": grade["description"]})
        suitable = grade.get("suitable_for") or grade.get("developed_for") or []
        if suitable:
            rows.append({"parameter": "Suitable For", "value": "; ".join(suitable)})
    if rows:
        return [{"title": title, "specs": rows}]
    return None


def collect_typical_spec_blocks(product, data):
    sections = product.get("sections") or {}
    typical = sections.get("typical_specs")
    if typical:
        if isinstance(typical, list) and typical and isinstance(typical[0], dict):
            blocks = []
            for group in typical:
                if group.get("type") in ("comparison", "matrix"):
                    blocks.append(group)
                    continue
                rows = rows_from_spec_list(group.get("specs"))
                if rows:
                    title = group["title"] if "title" in group else SPEC_SECTION_TITLE
                    blocks.append({"title": title, "specs": rows})
            if blocks:
                return blocks
        rows = rows_from_spec_list(typical)
        if rows:
            return [{"title": SPEC_SECTION_TITLE, "specs": rows}]

    blocks = []
    for grade in product.get("grades") or []:
        if isinstance(grade, dict):
            grade_blocks = blocks_from_grade(grade)
            if grade_blocks:
                blocks.extend(grade_blocks)
    if blocks:
        return blocks

    drill_map = {
        "korvanto-bento-drill-api": "API",
        "korvanto-bento-drill-ocma": "OCMA",
    }
    tag = drill_map.get(product.get("slug"))
    if tag and data:
        parent = get_product(data, "korvanto-bento-drill")
        if parent:
            for grade in parent.get("grades") or []:
                if isinstance(grade, dict) and grade.get("grade") == tag:
                    grade_blocks = blocks_from_grade(grade)
                    if grade_blocks:
                        return grade_blocks
    return []


def grade_anchor_id(grade_code=None, name=""):
    raw = (grade_code or name or "").strip()
    if not raw:
        return None
    cleaned = re.sub(r"[™\u2122]", "", raw).strip()
    code_match = re.search(
        r"\b(F\d{2}|F-\d+(?:\.\d+)?|I-\d+|C-\d+|AG-\d+|L-\d+|LF\d+|CB\d+|"
        r"PHARMA-IP|PAPER-325|DEINK-100|COSMETIC-90|DESICCANT-\d+|"
        r"SEAL-[PG]|API|OCMA|CA|LCA|HLCA|CS)\b",
        cleaned,
        re.I,
    )
    if code_match:
        slug = re.sub(r"[^a-z0-9]+", "-", code_match.group(1).lower()).strip("-")
        return f"grade-{slug}" if slug else None
    tokens = cleaned.split()
    token = tokens[-1] if tokens else cleaned
    if re.match(r"^[A-Za-z0-9][A-Za-z0-9\-./]*$", token):
        slug = re.sub(r"[^a-z0-9]+", "-", token.lower()).strip("-")
    else:
        slug = re.sub(r"[^a-z0-9]+", "-", cleaned.lower()).strip("-")
    return f"grade-{slug}" if slug else None


def grade_id_attr(grade_code=None, name=""):
    anchor = grade_anchor_id(grade_code, name)
    return f' id="{esc(anchor)}"' if anchor else ""


def is_grade_spec_title(title):
    if not title:
        return False
    upper = title.upper()
    return "KORVANTO" in upper and (
        "™" in title or re.search(r"\b(LF|CB|F-|C-|I-|AG-|L-|CA|LCA|HLCA|CS)\b", upper)
    )


def search_keywords(*parts):
    tokens = set()
    for part in parts:
        if not part:
            continue
        text = str(part).lower()
        tokens.add(text)
        for piece in re.split(r"[^a-z0-9]+", text):
            if len(piece) >= 2:
                tokens.add(piece)
    return sorted(tokens)


def build_product_search_index(data):
    entries = []
    seen = set()

    def add(label, url, kind, family_name="", keywords=None):
        label = (label or "").strip()
        url = (url or "").strip()
        if not label or not url:
            return
        key = (label.lower(), url.lower())
        if key in seen:
            return
        seen.add(key)
        entries.append(
            {
                "label": label,
                "url": url,
                "type": kind,
                "family": family_name,
                "keywords": search_keywords(label, family_name, *(keywords or [])),
            }
        )

    for family in get_families(data):
        add(
            family["name"],
            family["file"],
            "family",
            family["name"],
            [family["slug"], family.get("portfolio_meta", ""), family.get("short", "")],
        )

    for product in data.get("products", []):
        page = product.get("page_file")
        if not page:
            continue
        family = get_family(data, product.get("family", ""))
        family_name = family["name"] if family else ""
        add(
            product["name"],
            page,
            "product",
            family_name,
            [product["slug"], product.get("subtitle", "")],
        )

        for grade in product.get("grades") or []:
            if isinstance(grade, dict) and grade.get("grades"):
                for entry in grade["grades"]:
                    if not isinstance(entry, dict):
                        continue
                    grade_code = entry.get("grade") or entry.get("name", "")
                    grade_name = entry.get("name") or grade_code
                    anchor = grade_anchor_id(grade_code, grade_name)
                    if not anchor:
                        continue
                    add(
                        grade_name,
                        f"{page}#{anchor}",
                        "grade",
                        family_name,
                        [grade_code, grade_name],
                    )
                continue
            if not isinstance(grade, dict):
                continue
            grade_code = grade.get("grade") or ""
            grade_name = grade.get("name") or grade_code or grade.get("title", "")
            if not grade_name and not grade_code:
                continue
            anchor = grade_anchor_id(grade_code, grade_name)
            if not anchor:
                continue
            label = grade_name or grade_code
            add(label, f"{page}#{anchor}", "grade", family_name, [grade_code, grade_name, grade.get("description", ""), grade.get("subtitle", "")])

        for block in (product.get("sections") or {}).get("typical_specs") or []:
            title = block.get("title", "")
            if not is_grade_spec_title(title):
                continue
            anchor = grade_anchor_id(name=title)
            if not anchor:
                continue
            clean_title = re.sub(r"[™\u2122]", "", title).strip()
            add(clean_title, f"{page}#{anchor}", "grade", family_name, [title, clean_title])

    entries.sort(key=lambda item: (item["type"] != "family", item["family"], item["label"]))
    return entries


def write_product_search_index(data):
    index = build_product_search_index(data)
    SEARCH_INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote product search index ({len(index)} entries)")


def render_comparison_spec_block(block, sections=None):
    columns = block.get("columns") or []
    rows_data = block.get("rows") or []
    if not columns or not rows_data:
        return ""
    title = block.get("title", "")
    title_html = f'<h3 class="pd-spec-block-title">{esc(title)}</h3>' if title else ""
    header_html = "".join(
        f'<th scope="col">{esc(col["header"])}</th>' for col in columns
    )
    body = ""
    for row in rows_data:
        cells = ""
        for i, col in enumerate(columns):
            value = esc(row.get(col["key"], ""))
            if i == 0 or col.get("scope") == "row":
                cells += f'<th scope="row">{value}</th>'
            else:
                cells += f"<td>{value}</td>"
        body += f"<tr>{cells}</tr>"
    sections = sections or {}
    note = block.get("table_note")
    if note is None:
        note = sections.get("specs_table_note")
    if note is None:
        note = SPEC_TABLE_NOTE
    note_html = f'<p class="pd-spec-table-note">{esc(note)}</p>' if note else ""
    return f"""<div class="pd-spec-block reveal">
        {title_html}
        <div class="pd-spec-table-wrap pd-spec-table-wrap--wide tilt-card">
          <table class="pd-spec-table pd-spec-comparison-table">
            <thead>
              <tr>{header_html}</tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
        {note_html}
      </div>"""


def render_matrix_spec_block(block):
    header_row = block.get("header_row") or {}
    value_row = block.get("value_row") or {}
    header_cells = header_row.get("cells") or []
    value_cells = value_row.get("cells") or []
    if not header_cells or not value_cells:
        return ""
    title = block.get("title", "")
    title_html = f'<h3 class="pd-spec-block-title">{esc(title)}</h3>' if title else ""
    header_label = header_row.get("label", "")
    value_label = value_row.get("label", "")
    header_html = "".join(f"<th scope=\"col\">{esc(cell)}</th>" for cell in header_cells)
    value_html = "".join(f"<td>{esc(cell)}</td>" for cell in value_cells)
    return f"""<div class="pd-spec-block reveal">
        {title_html}
        <div class="pd-spec-table-wrap pd-spec-table-wrap--wide tilt-card">
          <table class="pd-spec-table pd-spec-matrix-table">
            <thead>
              <tr>
                <th scope="col">{esc(header_label)}</th>
                {header_html}
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">{esc(value_label)}</th>
                {value_html}
              </tr>
            </tbody>
          </table>
        </div>
      </div>"""


def render_spec_block(block, sections=None):
    block_type = block.get("type", "standard")
    if block_type == "comparison":
        return render_comparison_spec_block(block, sections)
    if block_type == "matrix":
        return render_matrix_spec_block(block)
    return render_spec_table(
        block.get("title"),
        block.get("specs") or [],
        value_column=(sections or {}).get("specs_value_column"),
        table_note=(sections or {}).get("specs_table_note"),
    )


def render_spec_table(title, rows, value_column=None, table_note=None):
    value_col = value_column or "Representative Value"
    body = "".join(
        f'<tr><th scope="row">{esc(row["parameter"])}</th><td>{esc(row["value"])}</td></tr>'
        for row in rows
    )
    title_html = f'<h3 class="pd-spec-block-title">{esc(title)}</h3>' if title else ""
    note = SPEC_TABLE_NOTE if table_note is None else table_note
    note_html = f'<p class="pd-spec-table-note">{esc(note)}</p>' if note else ""
    return f"""<div class="pd-spec-block reveal">
        {title_html}
        <div class="pd-spec-table-wrap tilt-card">
          <table class="pd-spec-table">
            <thead>
              <tr><th scope="col">Parameter</th><th scope="col">{esc(value_col)}</th></tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
        {note_html}
      </div>"""


def grades_quick_reference_section(product):
    ref = product.get("grades_quick_reference") or {}
    rows_data = ref.get("rows") or []
    if not rows_data:
        return ""

    section_label = ref.get("section_label", "Quick Reference")
    section_title = ref.get("section_title", "All Grades at a Glance")
    columns = ref.get("columns") or [
        {"header": "Grade", "key": "grade", "scope": "row"},
        {"header": "Al₂O₃ (%)", "key": "alumina"},
        {"header": "PCE (SK)", "key": "pce"},
        {"header": "Fe₂O₃", "key": "iron"},
        {"header": "Typical Application", "key": "typical_application"},
        {"header": "Recommended For", "key": "recommended_for"},
        {"header": "Sizes Available", "key": "sizes"},
    ]

    header_html = "".join(
        f'<th scope="col">{esc(col["header"])}</th>' for col in columns
    )
    body = ""
    for row in rows_data:
        cells = ""
        for col in columns:
            value = esc(row.get(col["key"], ""))
            if col.get("scope") == "row":
                cells += f'<th scope="row">{value}</th>'
            else:
                cells += f"<td>{value}</td>"
        body += f"<tr>{cells}</tr>"

    ctas = ref.get("cta") or []
    cta_html = ""
    if ctas:
        buttons = ""
        for item in ctas:
            style = item.get("style", "gold")
            btn_class = "btn btn-gold" if style == "gold" else "btn btn-outline btn-outline--light"
            buttons += (
                f'<a href="{esc(item.get("href", "request-quote.html"))}" class="{btn_class}">'
                f'{esc(item.get("text", "Request Quote"))} <span class="arrow">&rarr;</span></a>'
            )
        cta_html = f'<div class="pd-quick-ref-actions reveal reveal-delay-2">{buttons}</div>'

    return f"""<section class="section pd-section pd-section--navy pd-quick-ref-section" id="pdQuickRef">
      <div class="container">
        <header class="inner-section-head inner-section-head--center pd-section-head pd-quick-ref-head reveal">
          <p class="section-label">{esc(section_label)}</p>
          <h2 class="section-title">{esc(section_title)}</h2>
        </header>
        <div class="pd-quick-ref-table-wrap reveal reveal-delay-1">
          <table class="pd-quick-ref-table">
            <thead>
              <tr>{header_html}</tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
        {cta_html}
      </div>
    </section>"""


def typical_specs_section(product, data):
    sections = product.get("sections") or {}
    blocks = collect_typical_spec_blocks(product, data)
    if not blocks:
        blocks = [
            {
                "title": SPEC_SECTION_TITLE,
                "specs": [
                    {
                        "parameter": "Detailed Specifications",
                        "value": "Available on request — contact our export team for TDS",
                    }
                ],
            }
        ]
    tables = "".join(render_spec_block(block, sections) for block in blocks)
    custom_note = sections.get("custom_grade_note")
    custom_note_html = (
        f'<p class="pd-spec-note pd-spec-custom-note reveal">{esc(custom_note)}</p>'
        if custom_note else ""
    )
    section_label = sections.get("specs_section_label", "Technical Data")
    section_title = sections.get("specs_section_title", SPEC_SECTION_TITLE)
    return f"""<section class="section pd-section pd-section--white pd-specs-section" id="pdSpecs">
      <div class="container">
        {section_header(section_label, section_title)}
        <div class="pd-spec-blocks reveal reveal-delay-1">{tables}</div>
        {custom_note_html}
      </div>
    </section>"""


def product_comparison_section(product):
    cmp = product.get("product_comparison") or {}
    rows_data = cmp.get("rows") or []
    columns = cmp.get("columns") or []
    if not rows_data or not columns:
        return ""

    section_label = cmp.get("section_label", "Compare Options")
    section_title = cmp.get(
        "section_title",
        "Not sure whether Chamotte or Calcined Bauxite is right for your application?",
    )

    header_html = "".join(
        f'<th scope="col">{esc(col["header"])}</th>' for col in columns
    )
    body = ""
    for row in rows_data:
        # Skip packing rows if present in source data
        prop = str(row.get("property") or row.get(columns[0]["key"]) or "").strip().lower()
        if prop == "packing":
            continue
        cells = ""
        for i, col in enumerate(columns):
            value = esc(row.get(col["key"], ""))
            if i == 0 or col.get("scope") == "row":
                cells += f'<th scope="row">{value}</th>'
            else:
                cells += f"<td>{value}</td>"
        body += f"<tr>{cells}</tr>"

    ctas = cmp.get("cta") or []
    cta_html = ""
    if ctas:
        buttons = ""
        for item in ctas:
            style = item.get("style", "gold")
            btn_class = "btn btn-gold" if style == "gold" else "btn btn-outline btn-outline--light"
            buttons += (
                f'<a href="{esc(item.get("href", "request-quote.html"))}" class="{btn_class}">'
                f'{esc(item.get("text", "Request Quote"))} <span class="arrow">&rarr;</span></a>'
            )
        cta_html = f'<div class="pd-quick-ref-actions reveal reveal-delay-2">{buttons}</div>'

    return f"""<section class="section pd-section pd-section--navy pd-compare-section" id="pdCompare">
      <div class="container">
        <header class="inner-section-head inner-section-head--center pd-section-head pd-quick-ref-head reveal">
          <p class="section-label">{esc(section_label)}</p>
          <h2 class="section-title pd-compare-title">{esc(section_title)}</h2>
        </header>
        <div class="pd-quick-ref-table-wrap reveal reveal-delay-1">
          <table class="pd-quick-ref-table pd-compare-table">
            <thead>
              <tr>{header_html}</tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
        {cta_html}
      </div>
    </section>"""


def list_cards(items, css_class="pd-feature-grid"):
    items = filter_items(items)
    if not items:
        return ""
    cards = "".join(
        f'<article class="pd-feature-card tilt-card reveal"><span class="pd-card-shine" aria-hidden="true"></span><p>{esc(i)}</p></article>'
        for i in items
    )
    return f'<div class="{css_class}">{cards}</div>'


def section_block(title, items, grid_class="pd-feature-grid"):
    """Fallback generic section."""
    items = filter_items(items)
    if not items:
        return ""
    return f"""<section class="section pd-section pd-section--white">
      <div class="container reveal">
        {section_header("Product Detail", title)}
        {list_cards(items, "pd-features-grid")}
      </div>
    </section>"""


def product_image(product, fallback="assets/images/process/stage1.png"):
    return product.get("image") or fallback


def grade_code(grade_obj):
    if not isinstance(grade_obj, dict):
        return ""
    for field in ("grade", "name", "title"):
        val = (grade_obj.get(field) or "").strip().lower()
        if not val:
            continue
        if match := re.search(
            r"\b(hlca|lca|cb\d{2}|lf\d{2}|f-\d+|i-\d+|c-\d+|l-\d+|"
            r"api|ocma\+?|pharma-ip|cosmetic-90|desiccant-\d+|seal-[pg]|"
            r"paper-325|deink-100|feed|pencil|ag-\d+|bleach|detox|agro|cera|wine|custom|ca|cs)\b",
            val,
        ):
            return match.group(1)
    return ""


def grade_tokens(grade_obj):
    tokens = set()
    if not isinstance(grade_obj, dict):
        return tokens
    for field in ("grade", "name", "title"):
        val = (grade_obj.get(field) or "").strip()
        if not val:
            continue
        lowered = val.lower()
        tokens.add(lowered)
        for part in re.findall(r"[a-z0-9]+(?:-[0-9]+)?", lowered):
            tokens.add(part)
        for part in re.findall(
            r"(?:lf|cb|ag|api|ocma|pharma|cosmetic|desiccant|seal|paper|deink|feed|pencil|custom|wine|bleach|agro|detox|cera)\d*",
            lowered,
        ):
            tokens.add(part)
        for pattern in (r"f-\d+", r"i-\d+", r"c-\d+", r"l-\d+"):
            if match := re.search(pattern, lowered):
                tokens.add(match.group())
    return tokens


def resolve_grade_image(product_slug, grade_obj):
    if isinstance(grade_obj, dict):
        explicit = grade_obj.get("image")
        if explicit:
            return str(explicit).replace("\\", "/")
    grade_dir = GRADES_IMAGE_DIR / product_slug
    if not grade_dir.is_dir():
        return None

    code = grade_code(grade_obj)
    if code:
        code_pattern = re.compile(rf"(?:^|-){re.escape(code)}(?:$|[-.])")
        for path in sorted(grade_dir.iterdir()):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            if code_pattern.search(path.stem.lower()):
                return f"assets/images/grades/{product_slug}/{path.name}".replace("\\", "/")

    tokens = grade_tokens(grade_obj)
    best = None
    best_score = 0
    for path in grade_dir.iterdir():
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        stem = path.stem.lower()
        score = sum(len(token) for token in tokens if token in stem)
        if score > best_score:
            best_score = score
            best = path
    if best and best_score > 0:
        return f"assets/images/grades/{product_slug}/{best.name}".replace("\\", "/")
    return None


def grade_media_html(image_rel, alt):
    if not image_rel:
        return ""
    return (
        f'<div class="pd-grade-media"><img src="{esc(image_rel)}" alt="{esc(alt)}" loading="lazy"></div>'
    )


def family_context(product, data):
    family = get_family(data, product.get("family", ""))
    if not family:
        return None, None, None, product_image(product)
    return family["slug"], family["file"], family["name"], product_image(product, family["image"])


def grade_cards_cham(product):
    grades = product.get("grades") or []
    if not grades:
        items = filter_items(product["sections"].get("available_grades", []))
        return list_cards(items, "pd-grade-grid") if items else ""
    slug = product["slug"]
    html_parts = []
    for g in grades:
        if isinstance(g, dict) and g.get("entries"):
            for entry in g["entries"]:
                name = entry.get("name", "")
                size = entry.get("particle_size", "")
                media = grade_media_html(resolve_grade_image(slug, entry), name)
                html_parts.append(
                    f'<article class="pd-grade-card tilt-card reveal"{grade_id_attr(name=name)}>{media}'
                    f'<span class="pd-grade-tag">{esc(name)}</span>'
                    f'<p class="pd-grade-size">{esc(size)}</p></article>'
                )
        elif isinstance(g, dict) and g.get("grades"):
            for entry in g["grades"]:
                if not isinstance(entry, dict):
                    continue
                name = entry.get("name", "")
                media = grade_media_html(resolve_grade_image(slug, entry), name)
                html_parts.append(
                    f'<article class="pd-grade-card tilt-card reveal"{grade_id_attr(name=name)}>{media}'
                    f'<span class="pd-grade-tag">{esc(name)}</span></article>'
                )
    return f'<div class="pd-grade-grid">{"".join(html_parts)}</div>' if html_parts else ""


def grade_cards_baux(product):
    slug = product["slug"]
    blocks = []
    for g in product.get("grades") or []:
        if not isinstance(g, dict):
            continue
        name = g.get("grade") or g.get("name", "")
        alumina = g.get("alumina", "")
        suitable = g.get("suitable_for") or []
        benefits = g.get("key_benefits") or []
        suit_html = "".join(f"<li>{esc(s)}</li>" for s in suitable)
        ben_html = "".join(f"<li>{esc(b)}</li>" for b in benefits)
        media = grade_media_html(resolve_grade_image(slug, g), name)
        blocks.append(
            f"""<article class="pd-grade-card pd-grade-card--wide tilt-card reveal"{grade_id_attr(grade_code=name, name=name)}>
              {media}
              <span class="pd-grade-tag">{esc(name)}</span>
              {f'<p class="pd-grade-size">{esc(alumina)}</p>' if alumina else ''}
              {f'<h4>Suitable for</h4><ul>{suit_html}</ul>' if suitable else ''}
              {f'<h4>Key Benefits</h4><ul>{ben_html}</ul>' if benefits else ''}
            </article>"""
        )
    return f'<div class="pd-grade-grid pd-grade-grid--wide">{"".join(blocks)}</div>' if blocks else ""


def grade_cards_carbo(product):
    slug = product["slug"]
    blocks = []
    for g in product.get("grades") or []:
        if not isinstance(g, dict):
            continue
        name = g.get("grade") or ""
        title = g.get("name") or g.get("title", "")
        suitable = g.get("suitable_for") or g.get("developed_for") or []
        desc = g.get("description", "")
        suit_html = "".join(f"<li>{esc(s)}</li>" for s in suitable)
        media = grade_media_html(resolve_grade_image(slug, g), title or name)
        blocks.append(
            f"""<article class="pd-grade-card tilt-card reveal"{grade_id_attr(grade_code=name, name=name)}>
              {media}
              <span class="pd-grade-tag">{esc(name)}</span>
              <h3>{esc(title)}</h3>
              {f'<p>{esc(desc)}</p>' if desc else ''}
              {f'<ul>{suit_html}</ul>' if suitable else ''}
            </article>"""
        )
    return f'<div class="pd-grade-grid">{"".join(blocks)}</div>' if blocks else ""


def grade_cards_drill(product):
    slug = product["slug"]
    blocks = []
    for g in product.get("grades") or []:
        if not isinstance(g, dict):
            continue
        tag = g.get("grade") or ""
        name = g.get("name") or tag
        subtitle = g.get("subtitle", "")
        overview = g.get("overview") or []
        ov_html = "".join(f"<p>{esc_prose(p)}</p>" for p in overview)
        media = grade_media_html(resolve_grade_image(slug, g), name)
        blocks.append(
            f"""<article class="pd-grade-card pd-grade-card--wide tilt-card reveal"{grade_id_attr(grade_code=tag, name=name)}>
              {media}
              <span class="pd-grade-tag">{esc(tag)}</span>
              <h3>{esc(name)}</h3>
              {f'<p class="pd-drill-sub">{esc(subtitle)}</p>' if subtitle else ''}
              {ov_html}
            </article>"""
        )
    return f'<div class="pd-grade-grid pd-grade-grid--triple">{"".join(blocks)}</div>' if blocks else ""


def grade_cards_grades_array(product):
    slug = product["slug"]
    blocks = []
    for g in product.get("grades") or []:
        if isinstance(g, dict) and g.get("grades"):
            for entry in g["grades"]:
                if isinstance(entry, dict):
                    tag = entry.get("name") or entry.get("grade") or "Grade"
                    media = grade_media_html(resolve_grade_image(slug, entry), tag)
                    blocks.append(
                        f'<article class="pd-grade-card tilt-card reveal"{grade_id_attr(grade_code=tag, name=tag)}>{media}'
                        f'<span class="pd-grade-tag">{esc(tag)}</span></article>'
                    )
            continue
        if not isinstance(g, dict) or g.get("entries"):
            continue
        tag = g.get("grade") or g.get("name") or "Grade"
        subtitle = g.get("subtitle") or g.get("alumina") or g.get("description") or ""
        media = grade_media_html(resolve_grade_image(slug, g), tag)
        subtitle_html = f'<p class="pd-grade-size">{esc(subtitle)}</p>' if subtitle else ""
        grade_name = g.get("name") or tag
        blocks.append(
            f'<article class="pd-grade-card tilt-card reveal"{grade_id_attr(grade_code=tag, name=grade_name)}>{media}'
            f'<span class="pd-grade-tag">{esc(tag)}</span>'
            f"{subtitle_html}</article>"
        )
    blocks.extend(render_supplementary_grade_cards(product))
    return f'<div class="pd-grade-grid">{"".join(blocks)}</div>' if blocks else ""


def short_grade_label(name):
    if not name:
        return "Grade"
    cleaned = re.sub(r"[™\u2122]", "", str(name)).strip()
    patterns = [
        r"\bOCMA\+",
        r"\bF\d{2}\b",
        r"\b(?:F|I|C|L|AG)-\d+\b",
        r"\bLF\d+\b",
        r"\bCB\d+\b",
        r"\bPHARMA-IP\b",
        r"\bPAPER-325\b",
        r"\bDEINK-100\b",
        r"\bCOSMETIC-90\b",
        r"\bDESICCANT-\d+\b",
        r"\bSEAL-[PG]\b",
        r"\bAPI\b",
        r"\bOCMA\b",
        r"\b(?:CA|LCA|HLCA|CS)\b",
        r"\bPENCIL\b",
        r"\bFEED\b",
        r"\bBLEACH\b",
        r"\bDETOX\b",
        r"\bAGRO\b",
        r"\bCERA\b",
        r"\bWINE\b",
        r"\bCUSTOM\b",
        r"\bPRIVATE LABEL\b",
    ]
    for pattern in patterns:
        if match := re.search(pattern, cleaned, re.I):
            label = match.group(0).upper()
            return label.replace("OCMA+", "OCMA+")
    tokens = cleaned.split()
    return tokens[-1] if tokens else cleaned


def typical_spec_application_map(product):
    mapping = {}
    for block in product.get("sections", {}).get("typical_specs") or []:
        title = block.get("title", "")
        code = short_grade_label(title)
        for spec in block.get("specs") or []:
            if (spec.get("parameter") or "").strip().lower() == "application":
                mapping[code.upper()] = spec["value"]
    return mapping


def grade_recommended_use(grade_obj, entry=None, product=None):
    g = entry or grade_obj
    if g.get("recommended_use"):
        return g["recommended_use"]

    if product:
        app_map = typical_spec_application_map(product)
        code = short_grade_label(g.get("grade") or g.get("name", ""))
        if app_map.get(code.upper()):
            return app_map[code.upper()]

    apps = g.get("applications") or []
    if apps:
        return "; ".join(apps[:3])

    if g.get("subtitle"):
        return g["subtitle"]
    if g.get("description"):
        return g["description"]

    suitable = g.get("suitable_for") or g.get("developed_for") or []
    if suitable:
        return "; ".join(suitable[:2]) if len(suitable) > 1 else suitable[0]
    if g.get("particle_size"):
        return g["particle_size"]
    if g.get("alumina"):
        return f"{g['alumina']} alumina content"
    return "Contact our export team for grade guidance"


def collect_primary_grade_table_rows(product):
    rows = []
    app_map = typical_spec_application_map(product)

    for g in product.get("grades") or []:
        if isinstance(g, dict) and g.get("entries"):
            for entry in g["entries"]:
                name = entry.get("name", "")
                code = short_grade_label(name)
                use = app_map.get(code.upper()) or grade_recommended_use(g, entry, product)
                rows.append({"grade": code, "use": use})
            continue

        if isinstance(g, dict) and g.get("grades"):
            for entry in g["grades"]:
                if not isinstance(entry, dict):
                    continue
                name = entry.get("name") or entry.get("grade") or "Grade"
                code = short_grade_label(name)
                use = app_map.get(code.upper()) or grade_recommended_use(g, entry, product)
                rows.append({"grade": code, "use": use})
            continue

        if not isinstance(g, dict):
            continue

        code = short_grade_label(g.get("grade") or g.get("name") or "Grade")
        use = app_map.get(code.upper()) or grade_recommended_use(g, product=product)
        rows.append({"grade": code, "use": use})

    if not rows:
        for item in filter_items(product.get("sections", {}).get("available_grades", [])):
            code = short_grade_label(item)
            if code.lower() in {"particle", "sizes", "custom", "refractory", "chamotte"}:
                continue
            if re.match(r"^\d", code):
                continue
            rows.append({
                "grade": code,
                "use": app_map.get(code.upper()) or "Contact our export team for grade guidance",
            })

    return rows


def supplementary_grade_defs(product):
    slug = product.get("slug")
    sections = product.get("sections") or {}
    custom_use = sections.get("custom_grade_note") or (
        "Tailored specifications based on application and processing requirements"
    )

    if slug == "korvanto-bento-foundry":
        return [
            {
                "grade": "CUSTOM",
                "subtitle": "Custom Grade",
                "recommended_use": (
                    "Economy, Standard and Premium grades tailored to casting type, "
                    "sand system requirements, and foundry operating conditions."
                ),
            }
        ]

    primary_rows = collect_primary_grade_table_rows(product)
    if len(primary_rows) != 1:
        return []
    defs = [
        {
            "grade": "CUSTOM",
            "subtitle": (
                "Custom Pharmaceutical Grade"
                if product.get("slug") == "korvanto-bento-pharma"
                else "Custom Grade"
            ),
            "recommended_use": custom_use,
        }
    ]
    if product.get("slug") == "korvanto-bento-litter":
        defs.append({
            "grade": "PRIVATE LABEL",
            "subtitle": "Private Label Grade",
            "recommended_use": (
                "Private label cat litter manufacturing and branded pet care products"
            ),
        })
    return defs


def resolve_primary_grade_image(product):
    slug = product.get("slug", "")
    for g in product.get("grades") or []:
        if isinstance(g, dict) and g.get("entries"):
            for entry in g["entries"]:
                image = resolve_grade_image(slug, entry)
                if image:
                    return image
            continue
        if isinstance(g, dict) and g.get("grades"):
            for entry in g["grades"]:
                if isinstance(entry, dict):
                    image = resolve_grade_image(slug, entry)
                    if image:
                        return image
            continue
        if isinstance(g, dict):
            image = resolve_grade_image(slug, g)
            if image:
                return image
    return None


def render_supplementary_grade_cards(product):
    cards = []
    fallback_image = resolve_primary_grade_image(product)
    for entry in supplementary_grade_defs(product):
        tag = entry["grade"]
        subtitle = entry.get("subtitle", "")
        media = grade_media_html(fallback_image, tag) if fallback_image else ""
        subtitle_html = f'<p class="pd-grade-size">{esc(subtitle)}</p>' if subtitle else ""
        cards.append(
            f'<article class="pd-grade-card tilt-card reveal"{grade_id_attr(grade_code=tag, name=tag)}>'
            f"{media}"
            f'<span class="pd-grade-tag">{esc(tag)}</span>'
            f"{subtitle_html}</article>"
        )
    return cards


def collect_grade_table_rows(product):
    rows = collect_primary_grade_table_rows(product)
    for entry in supplementary_grade_defs(product):
        rows.append({
            "grade": entry["grade"],
            "use": entry.get("recommended_use", ""),
        })
    return rows


def render_grade_use_table(rows):
    if not rows:
        return ""
    body = "".join(
        f'<tr><td class="pd-grade-use-code">{esc(row["grade"])}</td>'
        f'<td>{esc(row["use"])}</td></tr>'
        for row in rows
    )
    return f"""<aside class="pd-grade-use-table-wrap reveal reveal-delay-2" aria-label="Grade recommended uses">
        <table class="pd-grade-use-table">
          <thead>
            <tr><th scope="col">Grade</th><th scope="col">Recommended Use</th></tr>
          </thead>
          <tbody>{body}</tbody>
        </table>
      </aside>"""


def grade_section(product):
    slug = product["slug"]
    if slug == "korvanto-bento-drill":
        grid = grade_cards_drill(product)
    elif slug == "korvanto-cham":
        grid = grade_cards_cham(product)
    elif slug == "korvanto-baux":
        grid = grade_cards_baux(product)
    elif slug == "korvanto-carbo":
        grid = grade_cards_carbo(product)
    elif product.get("grades"):
        grid = grade_cards_grades_array(product)
    else:
        grid = list_cards(product["sections"].get("available_grades", []), "pd-grade-grid")
    if not grid:
        return ""
    use_table = render_grade_use_table(collect_grade_table_rows(product))
    return f"""<section class="section pd-section pd-section--mesh" id="pdGrades">
      <div class="container">
        {section_header("Grades", "Available Grades")}
        <div class="pd-grades-layout reveal reveal-delay-1">
          <div class="pd-grades-cards">{grid}</div>
          {use_table}
        </div>
      </div>
    </section>"""


def forms_section(items, lead=None, section_label=None, section_title=None):
    items = filter_items(items)
    if not items:
        return ""
    label = section_label or "Supply Formats"
    title = section_title or "Available Forms"
    cards = ""
    form_icons = {
        "powder": '<path d="M6 3h12v4H6z"/><path d="M8 7v14h8V7"/><path d="M10 11h4"/>',
        "noodle": '<path d="M4 8c4-2 8-2 12 0s8 2 12 0"/><path d="M4 12c4 2 8 2 12 0s8-2 12 0"/><path d="M4 16c4 2 8 2 12 0s8-2 12 0"/>',
        "filter": '<path d="M4 5h16l-6 7v6l-4 2v-8z"/>',
        "lump": '<path d="M8 4l8 4-8 4-8-4z"/><path d="M4 12l8 4 8-4"/><path d="M4 16l8 4 8-4"/>',
        "granular": '<circle cx="7" cy="8" r="2"/><circle cx="17" cy="8" r="2"/><circle cx="12" cy="16" r="2"/>',
        "custom": '<path d="M12 3v18"/><path d="M5 8h14"/><path d="M7 16h10"/>',
    }

    def icon_paths(label):
        lowered = label.lower()
        if "noodle" in lowered:
            return form_icons["noodle"]
        if "filter" in lowered or "cake" in lowered:
            return form_icons["filter"]
        if "lump" in lowered or "crushed" in lowered:
            return form_icons["lump"]
        if "granular" in lowered or "particle" in lowered or "sizing" in lowered:
            return form_icons["granular"]
        if "powder" in lowered:
            return form_icons["powder"]
        return form_icons["custom"]

    lead_text = lead or (
        "Supplied in multiple industrial forms to match your processing and application requirements."
    )

    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        cards += f"""<article class="pd-form-card tilt-card reveal{delay}">
            <span class="pd-form-index">{i:02d}</span>
            <span class="pd-form-card-shine" aria-hidden="true"></span>
            <span class="pd-form-glow" aria-hidden="true"></span>
            <div class="pd-form-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                {icon_paths(item)}
              </svg>
            </div>
            <span class="pd-form-label">{esc(item)}</span>
          </article>"""
    return f"""<section class="section pd-section pd-forms-section" id="pdForms">
      <div class="pd-forms-deco" aria-hidden="true">
        <span class="pd-forms-orb pd-forms-orb--1"></span>
        <span class="pd-forms-orb pd-forms-orb--2"></span>
        <span class="pd-forms-mesh" aria-hidden="true"></span>
      </div>
      <div class="container">
        {section_header(label, title)}
        <p class="pd-forms-lead reveal">{esc(lead_text)}</p>
        <div class="pd-forms-grid reveal reveal-delay-1">{cards}</div>
      </div>
    </section>"""


def faq_items_html(items, start_open=False):
    blocks = []
    for i, item in enumerate(items):
        open_attr = " open" if i == 0 and start_open else ""
        blocks.append(
            f"""<details class="pd-faq-item"{open_attr}>
            <summary class="pd-faq-question">{esc(item["question"])}</summary>
            <div class="pd-faq-answer">{esc_prose(item["answer"])}</div>
          </details>"""
        )
    return "".join(blocks)


def faq_section(slug):
    if not slug:
        return ""
    data = load_product_faqs().get(slug)
    if not data:
        return ""

    if data.get("groups"):
        body = ""
        for group in data["groups"]:
            body += f"""<div class="pd-faq-group">
            <h3 class="pd-faq-group-title">{esc(group["title"])}</h3>
            <div class="pd-faq-list">{faq_items_html(group.get("items", []))}</div>
          </div>"""
    else:
        body = f'<div class="pd-faq-list">{faq_items_html(data.get("items", []), start_open=True)}</div>'

    return f"""<section class="section pd-section pd-section--mesh pd-faq-section" id="pdFaq">
      <div class="container">
        {section_header("Product Support", "Frequently Asked Questions", centered=True)}
        <div class="pd-faq-wrap reveal reveal-delay-1">{body}</div>
      </div>
    </section>"""


DEFAULT_CUSTOM_MANUFACTURING_ITEMS = [
    "Particle Size Distribution",
    "Custom Specifications & Grades",
    "Application-Specific Formulations",
    "Quality & Purity Requirements",
    "Custom Packaging",
    "Export Documentation Support",
]


def resolve_custom_manufacturing(product):
    sections = product.get("sections") or {}
    cm = sections.get("custom_manufacturing")
    if isinstance(cm, dict) and cm.get("items"):
        return {
            "section_label": cm.get("section_label", "Custom Grade"),
            "title": cm.get("title", "Custom Manufacturing Options"),
            "lead": cm.get("lead", ""),
            "items": filter_items(cm["items"]),
        }

    name = product.get("name", "products")
    if name.lower().startswith("korvanto "):
        name = name[9:]
    return {
        "section_label": "Custom Grade",
        "title": "Custom Manufacturing Options",
        "lead": f"KORVANTO supplies {name.lower()} according to customer requirements, including:",
        "items": DEFAULT_CUSTOM_MANUFACTURING_ITEMS,
    }


def custom_manufacturing_section(product):
    cm = resolve_custom_manufacturing(product)
    items = cm.get("items") or []
    if not items:
        return ""

    tiles = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        tiles += f"""<article class="pd-custom-tile tilt-card reveal{delay}">
            <span class="pd-custom-tile-shine" aria-hidden="true"></span>
            <span class="pd-custom-tile-index">{i:02d}</span>
            <div class="pd-custom-tile-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                {custom_tile_icon_paths(item, i)}
              </svg>
            </div>
            <p class="pd-custom-tile-label">{esc(item)}</p>
          </article>"""

    return f"""<section class="section pd-section pd-custom-section" id="pdCustom">
      <div class="pd-custom-deco" aria-hidden="true">
        <span class="pd-custom-mesh"></span>
        <span class="pd-custom-orb pd-custom-orb--1"></span>
        <span class="pd-custom-orb pd-custom-orb--2"></span>
      </div>
      <div class="container">
        <div class="pd-custom-showcase tilt-card reveal">
          <div class="pd-custom-showcase-left">
            <span class="pd-custom-badge">Bespoke Supply</span>
            <p class="section-label section-label--light">{esc(cm.get("section_label", "Custom Grade"))}</p>
            <h2 class="pd-custom-title">{esc(cm.get("title", "Custom Manufacturing Options"))}</h2>
            <p class="pd-custom-lead">{esc_prose(cm.get("lead", ""))}</p>
            <a href="request-quote.html" class="btn btn-gold btn-sm pd-custom-cta">Discuss Custom Specs <span class="arrow">&rarr;</span></a>
          </div>
          <div class="pd-custom-showcase-right">
            <div class="pd-custom-grid">{tiles}</div>
          </div>
        </div>
      </div>
    </section>"""


def custom_tile_icon_paths(label, index):
    lowered = (label or "").lower()
    if any(k in lowered for k in ("packag", "label", "export", "document")):
        return '<path d="M4 8h16v12H4z"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M12 12v4"/>'
    if any(k in lowered for k in ("particle", "granule", "size", "moisture", "dust")):
        return '<circle cx="7" cy="8" r="2"/><circle cx="17" cy="8" r="2"/><circle cx="12" cy="16" r="2"/>'
    if any(k in lowered for k in ("quality", "purity", "strength", "absorption", "clump", "fragrance", "color")):
        return '<path d="M12 3l2.2 6.8H21l-5.6 4.1 2.1 6.6L12 16.2 6.5 20.5l2.1-6.6L3 9.8h6.8z"/>'
    if any(k in lowered for k in ("application", "formulation", "specification", "grade")):
        return '<path d="M4 6h16v12H4z"/><path d="M8 10h8"/><path d="M8 14h5"/>'
    icons = [
        '<path d="M12 3v18"/><path d="M5 8h14"/><path d="M8 16h8"/>',
        '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
        '<path d="M4 7h16"/><path d="M6 7V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/><path d="M9 11h6"/><path d="M9 15h4"/>',
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    ]
    return icons[(index - 1) % len(icons)]


def quality_assurance_section(product):
    qa = (product.get("sections") or {}).get("quality_assurance")
    if not qa:
        return ""

    if isinstance(qa, list):
        items = filter_items(qa)
        section_label = "Compliance"
        title = "Quality Assurance"
    else:
        items = filter_items(qa.get("items") or [])
        section_label = qa.get("section_label", "Compliance")
        title = qa.get("title", "Quality Assurance")

    if not items:
        return ""
    cards = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 3, 2)}" if i % 3 else ""
        cards += f"""<article class="pd-qa-card tilt-card reveal{delay}">
            <span class="pd-qa-card-shine" aria-hidden="true"></span>
            <div class="pd-qa-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
            </div>
            <p class="pd-qa-label">{esc(item)}</p>
          </article>"""

    return f"""<section class="section pd-section pd-qa-section" id="pdQuality">
      <div class="container">
        {section_header(section_label, title, centered=True)}
        <div class="pd-qa-grid reveal reveal-delay-1">{cards}</div>
      </div>
    </section>"""


def packaging_section(items=None, show=True):
    if not show:
        return ""
    items = STANDARD_PACKAGING_OPTIONS
    cards = ""
    for i, item in enumerate(items, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        cards += f"""<article class="pd-pack-card tilt-card reveal{delay}">
            <span class="pd-pack-card-shine" aria-hidden="true"></span>
            <span class="pd-pack-glow" aria-hidden="true"></span>
            <div class="pd-pack-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                <path d="M4 8h16v12H4z"/>
                <path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                <path d="M12 12v4"/>
              </svg>
            </div>
            <span class="pd-pack-label">{esc(item)}</span>
          </article>"""
    return f"""<section class="section pd-section pd-pack-section" id="pdPackaging">
      <div class="pd-pack-deco" aria-hidden="true">
        <span class="pd-pack-orb pd-pack-orb--1"></span>
        <span class="pd-pack-orb pd-pack-orb--2"></span>
      </div>
      <div class="container">
        {section_header("Export Supply", "Packaging Options")}
        <div class="pd-pack-grid reveal reveal-delay-1">{cards}</div>
      </div>
    </section>"""


def hero(breadcrumb_tail, label, h1, lead, image, family_file=None, badge_text="Export Ready"):
    if family_file:
        bc = f'<a href="index.html">Home</a> / <a href="products.html">Products</a> / <a href="{family_file}">{esc(label)}</a> / {esc(breadcrumb_tail)}'
    elif breadcrumb_tail == h1 and label == "Product Family":
        bc = f'<a href="index.html">Home</a> / <a href="products.html">Products</a> / {esc(h1)}'
    else:
        bc = f'<a href="index.html">Home</a> / <a href="products.html">Products</a> / {esc(breadcrumb_tail)}'
    return f"""<section class="product-hero-detail">
      <div class="pd-hero-deco" aria-hidden="true">
        <span class="pd-hero-orb pd-hero-orb--1"></span>
        <span class="pd-hero-orb pd-hero-orb--2"></span>
      </div>
      <div class="container pd-hero-grid">
        <div class="product-hero-copy reveal">
          <nav class="breadcrumb" aria-label="Breadcrumb">{bc}</nav>
          <p class="section-label">{esc(label)}</p>
          <h1>{esc(h1)}</h1>
          <p class="lead">{esc(lead)}</p>
          <div class="product-hero-actions">
            <a href="request-quote.html" class="btn btn-gold">{BTN_ICON_QUOTE}<span>Request a Quote</span> <span class="arrow">&rarr;</span></a>
            <a href="quality-assurance.html" class="btn btn-outline">{BTN_ICON_DOC}<span>Quality &amp; Documentation</span></a>
          </div>
        </div>
        <div class="product-hero-visual reveal reveal-delay-1">
          <div class="product-hero-frame tilt-card">
            <img src="{esc(image)}" alt="{esc(h1)}">
            <span class="pd-hero-badge-float">{esc(badge_text)}</span>
          </div>
        </div>
      </div>
    </section>"""


def overview_section(paragraphs, image, panel=None):
    paras = filter_overview_paragraphs(paragraphs)
    if not paras:
        return ""
    panel = panel or {}
    label = panel.get("section_label", "Overview")
    title = panel.get("section_title", "Product Overview")
    cta_text = panel.get("cta_text")
    cta_href = panel.get("cta_href", "request-quote.html")
    body = "".join(f"<p>{esc_prose(p)}</p>" for p in paras)
    cta_html = (
        f'<a href="{esc(cta_href)}" class="btn btn-gold pd-overview-cta">{esc(cta_text)} <span class="arrow">&rarr;</span></a>'
        if cta_text
        else ""
    )
    return f"""<section class="section section--mesh pd-overview" id="pdOverview">
      <div class="container">
        <div class="pd-overview-grid reveal">
          <div class="pd-overview-visual premium-scene-3d">
            <div class="premium-scene-glow" aria-hidden="true"></div>
            <div class="premium-scene-layer premium-media-frame tilt-card">
              <img src="{esc(image)}" alt="Product overview">
            </div>
          </div>
          <div class="pd-overview-panel tilt-card reveal reveal-delay-1">
            <span class="pd-panel-shine" aria-hidden="true"></span>
            <p class="section-label">{esc(label)}</p>
            <h2 class="section-title">{esc(title)}</h2>
            {body}
            {cta_html}
          </div>
        </div>
      </div>
    </section>"""


def request_section(name, slug=""):
    return f"""<section class="section pd-request-section" id="pdRequest">
      <div class="container">
        <div class="pd-request-panel reveal tilt-card">
          {section_header("Get Started", "Request TDS / Request Quote")}
          <p class="pd-request-lead">Share your grade requirements, destination country and documentation needs. Our export team will provide a Technical Data Sheet, certificate support and a tailored quotation for {esc(name)}.</p>
          <div class="pd-request-actions">
            <a href="request-quote.html" class="btn btn-outline">Request TDS</a>
            <a href="request-quote.html" class="btn btn-gold">Request Quote <span class="arrow">&rarr;</span></a>
          </div>
        </div>
      </div>
    </section>"""


def cta_block(name):
    return f"""<section class="cta-banner about-cta">
      <div class="cta-bg"><img src="assets/images/cta/1.png" alt="Export logistics"></div>
      <div class="container cta-content reveal">
        <h2>Looking for a reliable mineral export partner ?</h2>
        <p class="cta-tagline">Share your specifications, application requirements and destination country.<br>Our team will recommend suitable grades, packaging options and export solutions for {esc(name)}.</p>
        <a href="request-quote.html" class="btn btn-gold">Request a Quote <span class="arrow">&rarr;</span></a>
      </div>
    </section>"""


def related_products(items):
    if not items:
        return ""
    links = "".join(
        f'<a href="{esc(href)}" class="pd-related-card tilt-card reveal"><span>{esc(title)}</span><small>{esc(sub)}</small></a>'
        for href, title, sub in items[:4]
    )
    return f"""<section class="section pd-related">
      <div class="container reveal">
        <header class="pd-section-head"><p class="section-label">Explore More</p><h2 class="section-title">Related Products</h2></header>
        <div class="pd-related-grid">{links}</div>
      </div>
    </section>"""


def get_product(data, slug):
    for p in data["products"]:
        if p["slug"] == slug:
            return p
    return None


def render_detail_page(product, data, outfile):
    _, fam_file, fam_label, image = family_context(product, data)
    hero_image = product.get("hero_image") or image
    overview_image = product.get("overview_image") or image
    s = product["sections"]
    lead = product.get("subtitle") or ""
    if not lead and s.get("overview"):
        lead = s["overview"][0]
    badge = product.get("hero_badge", "Export Ready")

    parts = [
        head(product["name"], lead or product["name"]),
        '  <div id="header-placeholder"></div>\n  <main>',
        hero(product["name"], fam_label, product["name"], lead, hero_image, fam_file, badge),
        overview_section(s.get("overview", []), overview_image, product.get("overview_panel")),
        benefits_section(product=product),
        grades_quick_reference_section(product),
        typical_specs_section(product, data),
        product_comparison_section(product),
        applications_section(s.get("applications")),
        grade_section(product),
        custom_manufacturing_section(product),
        forms_section(
            s.get("available_forms", []),
            s.get("available_forms_lead"),
            s.get("forms_section_label") or product.get("forms_section_label"),
            s.get("forms_section_title") or product.get("forms_section_title"),
        ),
        packaging_section(s.get("packaging", []), show=product.get("show_packaging", True)),
        quality_assurance_section(product),
        faq_section(product.get("slug", "")),
        request_section(product["name"], product.get("slug", "")),
    ]
    parts.append("  </main>\n")
    parts.append(foot())
    (ROOT / outfile).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {outfile}")


def generate_detail_page(data, slug, outfile):
    product = get_product(data, slug)
    if not product:
        print(f"SKIP missing product: {slug}")
        return
    render_detail_page(product, data, outfile)


def family_product_guide_section(family, data):
    rows_data = family.get("product_guide") or []
    if not rows_data:
        return ""

    section_label = family.get("product_guide_label", "Product Guide")
    section_title = family.get("product_guide_title", "Grades at a Glance")

    if family.get("product_guide_columns"):
        columns = family["product_guide_columns"]
    else:
        columns = [
            {"header": "Product", "key": "product", "scope": "row"},
            {"header": "Form", "key": "form"},
            {"header": "Processing", "key": "processing"},
            {"header": "Main Applications", "key": "applications"},
        ]

    header_html = "".join(
        f'<th scope="col">{esc(col["header"])}</th>' for col in columns
    )
    header_html += '<th scope="col">Specifications</th>'

    body = ""
    for row in rows_data:
        cells = ""
        for col in columns:
            value = esc(row.get(col["key"], ""))
            if col.get("scope") == "row":
                cells += f'<th scope="row">{value}</th>'
            else:
                cells += f"<td>{value}</td>"
        slug = row.get("slug", "")
        product = get_product(data, slug) if slug else None
        page = (product.get("page_file") if product else None) or (f"{slug}.html" if slug else "#")
        href = f"{page}#pdSpecs"
        body += f"""<tr>
            {cells}
            <td class="pf-guide-spec-cell">
              <a href="{esc(href)}" class="pf-guide-spec-link">View Specifications <span class="arrow">&rarr;</span></a>
            </td>
          </tr>"""

    return f"""<section class="section pf-guide-section" id="pfProductGuide">
      <div class="container">
        {section_header(section_label, section_title)}
        <div class="pf-guide-table-wrap reveal reveal-delay-1">
          <table class="pf-guide-table">
            <thead>
              <tr>{header_html}</tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
      </div>
    </section>"""


def generate_family_page(family, data):
    if family.get("single"):
        product = get_product(data, family["single"])
        if product and product.get("page_file"):
            render_detail_page(product, data, family["file"])
        return

    cards = ""
    for i, child_slug in enumerate(family.get("child_slugs", []), 1):
        product = get_product(data, child_slug)
        if not product:
            continue
        href = product.get("page_file") or f"{child_slug}.html"
        title = product.get("name", child_slug)
        sub = product.get("card_summary") or product.get("subtitle") or ""
        img = product.get("image") or family.get("image", "")
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        cards += f"""<article class="pf-card tilt-card reveal{delay}">
          <span class="pf-card-index">{i:02d}</span>
          <span class="pf-card-shine" aria-hidden="true"></span>
          <div class="pf-card-media"><img src="{esc(img)}" alt="{esc(title)}" loading="lazy"></div>
          <h3>{esc(title)}</h3>
          <p>{esc(sub)}</p>
          <a href="{esc(href)}" class="btn btn-gold btn-sm">Explore Product <span class="arrow">&rarr;</span></a>
        </article>"""

    guide = family_product_guide_section(family, data)
    overview_html = overview_section(
        family.get("overview", []),
        family.get("overview_image") or family.get("image", ""),
        family.get("overview_panel"),
    )
    faq_html = faq_section(family["slug"])

    content = f"""{head(family['name'], family['short'])}
  <div id="header-placeholder"></div>
  <main>
    {hero(family['name'], 'Product Family', family['name'], family['short'], family['image'], badge_text='Product Family')}
    {overview_html}
    <section class="section pf-grid-section">
      <div class="container">
        {section_header("Product Range", f"Explore {family['name']} Grades")}
        <div class="pf-grid">{cards}</div>
      </div>
    </section>
    {guide}
    {faq_html}
    {cta_block(family['name'])}
  </main>
{foot()}"""
    (ROOT / family["file"]).write_text(content, encoding="utf-8")
    print(f"Wrote {family['file']}")


def portfolio_hero_slider_html(families):
    """Main products-page banner only — uses family card images; does not affect product detail pages."""
    slides = []
    metas = []
    captions = []
    dots = []
    total = len(families)
    for i, family in enumerate(families):
        active = " is-active" if i == 0 else ""
        aria = "true" if i == 0 else "false"
        slides.append(
            f'<div class="products-hero-slide{active}">'
            f'<div class="products-hero-stage">'
            f'<img src="{esc(family["image"])}" alt="{esc(family["name"])}">'
            f"</div></div>"
        )
        metas.append(
            f'<span class="products-hero-meta{active}">{esc(family.get("portfolio_meta", ""))}</span>'
        )
        captions.append(
            f'<p class="products-hero-caption{active}">{esc(family["name"])}</p>'
        )
        dots.append(
            f'<button type="button" class="products-hero-dot{active}" role="tab" '
            f'aria-selected="{aria}" aria-label="{esc(family["name"])}"></button>'
        )
    return f"""<div class="products-hero-showcase">
            <div class="products-hero-media">
              <div class="products-hero-slider" aria-label="Korvanto product families">
                {"".join(slides)}
              </div>
            </div>
            <div class="products-hero-footer">
              <div class="products-hero-meta-track" aria-live="polite">
                {"".join(metas)}
              </div>
              <div class="products-hero-caption-track" aria-live="polite">
                {"".join(captions)}
              </div>
              <div class="products-hero-controls">
                <div class="products-hero-dots" role="tablist" aria-label="Product family slides">
                  {"".join(dots)}
                </div>
                <span class="products-hero-counter" aria-hidden="true"><span class="is-current">01</span><span class="products-hero-counter-sep">/</span>{total:02d}</span>
              </div>
            </div>
          </div>"""


def generate_portfolio_page(data):
    page = data.get("catalog", {}).get("portfolio_page", {})
    families = get_families(data)
    hero_slider = portfolio_hero_slider_html(families)
    cards = ""
    for i, family in enumerate(families, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        btn = "Explore grades"
        cards += f"""<article class="products-family-card tilt-card reveal{delay}">
            <a href="{esc(family['file'])}" class="media"><img src="{esc(family['image'])}" alt="{esc(family['name'])}"></a>
            <div class="body">
              <span class="products-family-meta">{esc(family.get('portfolio_meta', ''))}</span>
              <h2>{esc(family['name'])}</h2>
              <p>{esc(family['short'])}</p>
              <a href="{esc(family['file'])}" class="btn btn-gold btn-sm">{btn} <span class="arrow">&rarr;</span></a>
            </div>
          </article>"""

    stats = page.get("stats", [])
    stats_html = "".join(
        f"""<div class="products-portfolio-stat">
              <strong>{esc(item.get('value', ''))}</strong>
              <span>{esc(item.get('label', ''))}</span>
            </div>"""
        for item in stats
    )

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(page.get('description', ''))}">
  <title>{esc(page.get('title', 'Products | Korvanto'))}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/shared/base.css">
  <link rel="stylesheet" href="assets/css/shared/header.css">
  <link rel="stylesheet" href="assets/css/shared/footer.css">
  <link rel="stylesheet" href="assets/css/shared/premium-inner.css">
  <link rel="stylesheet" href="assets/css/pages/inner.css">
  <link rel="stylesheet" href="assets/css/pages/product-detail.css">
  <link rel="stylesheet" href="assets/css/pages/products-catalog.css">
  <link rel="stylesheet" href="assets/css/pages/home.css">
  <link rel="stylesheet" href="assets/css/shared/responsive.css">
  <link rel="stylesheet" href="assets/css/shared/mobile.css">
</head>
<body class="inner-premium product-page">
  <div id="header-placeholder"></div>
  <main>
    <section class="products-portfolio-hero">
      <div class="pd-hero-deco" aria-hidden="true">
        <span class="pd-hero-orb pd-hero-orb--1"></span>
        <span class="pd-hero-orb pd-hero-orb--2"></span>
      </div>
      <div class="container pd-hero-grid">
        <div class="reveal">
          <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / Products</nav>
          <p class="section-label">{esc(page.get('hero_label', ''))}</p>
          <h1>{page.get('hero_title', '')}</h1>
          <p class="page-hero-lead">{esc_prose(page.get('hero_lead', ''))}</p>
          <div class="products-portfolio-stats">{stats_html}</div>
        </div>
        <div class="products-portfolio-visual reveal reveal-delay-1">
          <div class="products-portfolio-frame tilt-card">
            {hero_slider}
          </div>
        </div>
      </div>
    </section>

    <section class="products-search-bar" aria-label="Product search">
      <div class="container">
        <div class="products-search product-search" id="productSearch">
          <label class="products-search-label" for="productSearchInput">Search products &amp; grades</label>
          <div class="products-search-field product-search-field">
            <input type="search" id="productSearchInput" class="products-search-input product-search-input" placeholder="Search by product, family, or grade code (e.g. LF42, Hydrous Kaolin, F-100)..." autocomplete="off" aria-controls="productSearchResults" aria-expanded="false" aria-autocomplete="list">
            <div class="product-search-results" id="productSearchResults" role="listbox" hidden></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--mesh">
      <div class="container">
        <header class="inner-section-head inner-section-head--center reveal">
          <p class="section-label">{esc(page.get('section_label', ''))}</p>
          <h2 class="section-title">{esc(page.get('section_title', ''))}</h2>
          <p class="section-lead">{esc_prose(page.get('section_lead', ''))}</p>
        </header>
        <div class="products-family-grid">{cards}</div>
      </div>
    </section>

    <section class="cta-banner">
      <div class="cta-bg"><img src="assets/images/cta/1.png" alt="Export logistics"></div>
      <div class="container cta-content reveal">
        <h2>Looking for a reliable mineral export partner ?</h2>
        <p class="cta-tagline">Share your specifications, application requirements and destination country.<br>Our team will recommend suitable grades, packaging options and export solutions.</p>
        <a href="request-quote.html" class="btn btn-gold">Request a Quote <span class="arrow">&rarr;</span></a>
      </div>
    </section>
  </main>
  <div id="footer-placeholder"></div>
  <script src="assets/js/main.js"></script>
</body>
</html>"""
    PRODUCTS_PAGE_PATH.write_text(content, encoding="utf-8")
    print("Wrote products.html")


def render_mega_menu(data):
    families = get_families(data)
    family_links = "".join(
        f'                <a href="{esc(family["file"])}">{esc(family["name"])}</a>\n'
        for family in families
    )
    wide_cols = []
    for family in families:
        slugs = family.get("child_slugs") or []
        if not slugs:
            continue
        links = "".join(
            f'                  <a href="{esc(get_product(data, slug).get("page_file") or f"{slug}.html")}">{esc(mega_menu_child_label(get_product(data, slug)["name"]))}</a>\n'
            for slug in slugs
            if get_product(data, slug)
        )
        wide_cols.append(
            f"""              <div class="mega-col{' mega-col--wide' if family['slug'] == 'korvanto-bento' else ''}">
                <p class="mega-label">{esc(family['name'])}</p>
                {'<div class="mega-links-grid">' + links + '</div>' if family['slug'] == 'korvanto-bento' else links}
              </div>"""
        )
    return f"""            <div class="mega-menu-inner">
              <div class="mega-col">
                <p class="mega-label">Product Families</p>
{family_links}                <a href="products.html" class="mega-all">Explore All Products →</a>
              </div>
{''.join(wide_cols)}
            </div>"""


def patch_file_section(path, start_marker, end_marker, new_content):
    text = path.read_text(encoding="utf-8", errors="replace")
    if start_marker not in text or end_marker not in text:
        raise ValueError(f"Markers not found in {path}")
    before, rest = text.split(start_marker, 1)
    _, after = rest.split(end_marker, 1)
    path.write_text(before + start_marker + "\n" + new_content + "\n" + end_marker + after, encoding="utf-8")


def generate_quote_options(data):
    quote = data.get("catalog", {}).get("quote_form", {})
    groups = []
    for family in get_families(data):
        if family.get("single"):
            product = get_product(data, family["single"])
            if not product:
                continue
            groups.append(
                {
                    "label": quote.get("other_group_label", "Other Product Families"),
                    "options": [{"value": product["slug"], "label": product["name"]}],
                }
            )
            continue
        options = []
        for slug in family.get("child_slugs", []):
            product = get_product(data, slug)
            if product:
                options.append({"value": product["slug"], "label": product["name"]})
        if options:
            groups.append({"label": family["name"], "options": options})

    other = [g for g in groups if g["label"] == quote.get("other_group_label", "Other Product Families")]
    main_groups = [g for g in groups if g not in other]
    html_parts = ['              <option value="">Select product</option>']
    for group in main_groups:
        html_parts.append(f'              <optgroup label="{esc(group["label"])}">')
        for option in group["options"]:
            html_parts.append(f'                <option value="{esc(option["value"])}">{esc(option["label"])}</option>')
        html_parts.append("              </optgroup>")
    if other:
        merged = []
        for group in other:
            merged.extend(group["options"])
        html_parts.append(f'              <optgroup label="{esc(quote.get("other_group_label", "Other Product Families"))}">')
        for option in merged:
            html_parts.append(f'                <option value="{esc(option["value"])}">{esc(option["label"])}</option>')
        html_parts.append("              </optgroup>")
    for option in quote.get("extra_options", []):
        html_parts.append(f'              <option value="{esc(option["value"])}">{esc(option["label"])}</option>')
    return "\n".join(html_parts)


def main():
    data = load_data()
    if "catalog" not in data:
        raise SystemExit("products-data.json is missing catalog metadata. Run: python scripts/parse-products.py")

    for product in data["products"]:
        page_file = product.get("page_file")
        if page_file:
            render_detail_page(product, data, page_file)

    for family in get_families(data):
        generate_family_page(family, data)

    generate_portfolio_page(data)
    write_product_search_index(data)
    patch_file_section(HEADER_PATH, MEGA_MENU_START, MEGA_MENU_END, render_mega_menu(data))
    print("Updated components/header.html mega menu")
    patch_file_section(QUOTE_PATH, QUOTE_OPTIONS_START, QUOTE_OPTIONS_END, generate_quote_options(data))
    print("Updated request-quote.html product options")
    print("Done generating product pages.")


if __name__ == "__main__":
    main()
