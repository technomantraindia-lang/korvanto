#!/usr/bin/env python3
"""Generate Korvanto product family and detail HTML pages from products-data.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "js" / "products-data.json"
GRADES_IMAGE_DIR = ROOT / "assets" / "images" / "grades"
HEADER_PATH = ROOT / "components" / "header.html"
QUOTE_PATH = ROOT / "request-quote.html"
PRODUCTS_PAGE_PATH = ROOT / "products.html"
MEGA_MENU_START = "<!-- catalog:mega-menu:start -->"
MEGA_MENU_END = "<!-- catalog:mega-menu:end -->"
QUOTE_OPTIONS_START = "<!-- catalog:quote-options:start -->"
QUOTE_OPTIONS_END = "<!-- catalog:quote-options:end -->"


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def get_families(data):
    return data.get("catalog", {}).get("families", [])


def get_family(data, family_slug):
    for family in get_families(data):
        if family["slug"] == family_slug:
            return family
    return None


def esc(text):
    return html.escape(str(text or ""))


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
  <script src="assets/js/main.js"></script>
</body>
</html>"""


SKIP_EXACT = {
    "Website Category Description (for KORVANTO BENTO DRILL)",
}


def filter_items(items):
    skip_prefixes = ("Website Category Description", "Bottom of Form")
    out = []
    for item in items or []:
        if item in SKIP_EXACT:
            continue
        if any(item.startswith(p) for p in skip_prefixes):
            continue
        if item.endswith(" is widely used in:"):
            continue
        out.append(item)
    return out


def filter_overview_paragraphs(items):
    return [i for i in (items or []) if i and not i.startswith("Website Category Description")]


def section_header(label, title, centered=True):
    center = " inner-section-head--center pd-section-head" if centered else " pd-section-head"
    return f"""<header class="inner-section-head{center}">
          <p class="section-label">{esc(label)}</p>
          <h2 class="section-title">{esc(title)}</h2>
        </header>"""


def benefits_section(items):
    items = filter_items(items)
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
    items = filter_items(items)
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
        if isinstance(typical, list) and typical and isinstance(typical[0], dict) and typical[0].get("specs"):
            blocks = []
            for group in typical:
                rows = rows_from_spec_list(group.get("specs"))
                if rows:
                    blocks.append({"title": group.get("title") or "Typical Specifications", "specs": rows})
            return blocks
        rows = rows_from_spec_list(typical)
        if rows:
            return [{"title": "Typical Specifications", "specs": rows}]

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


def render_spec_table(title, rows):
    body = "".join(
        f'<tr><th scope="row">{esc(row["parameter"])}</th><td>{esc(row["value"])}</td></tr>'
        for row in rows
    )
    title_html = f'<h3 class="pd-spec-block-title">{esc(title)}</h3>' if title else ""
    return f"""<div class="pd-spec-block reveal">
        {title_html}
        <div class="pd-spec-table-wrap tilt-card">
          <table class="pd-spec-table">
            <thead>
              <tr><th scope="col">Parameter</th><th scope="col">Typical Value</th></tr>
            </thead>
            <tbody>{body}</tbody>
          </table>
        </div>
      </div>"""


def typical_specs_section(product, data):
    sections = product.get("sections") or {}
    blocks = collect_typical_spec_blocks(product, data)
    if not blocks:
        blocks = [
            {
                "title": "Typical Specifications",
                "specs": [
                    {
                        "parameter": "Detailed Specifications",
                        "value": "Available on request — contact our export team for TDS",
                    }
                ],
            }
        ]
    tables = "".join(render_spec_table(block.get("title"), block["specs"]) for block in blocks)
    note = sections.get("custom_grade_note") or sections.get("typical_specs_note")
    note_html = f'<p class="pd-spec-note reveal">{esc(note)}</p>' if note else ""
    return f"""<section class="section pd-section pd-section--white pd-specs-section" id="pdSpecs">
      <div class="container">
        {section_header("Technical Data", "Typical Specs")}
        <div class="pd-spec-blocks reveal reveal-delay-1">{tables}</div>
        {note_html}
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
    grade_dir = GRADES_IMAGE_DIR / product_slug
    if not grade_dir.is_dir():
        return None
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
                    f'<article class="pd-grade-card tilt-card reveal">{media}'
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
                    f'<article class="pd-grade-card tilt-card reveal">{media}'
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
            f"""<article class="pd-grade-card pd-grade-card--wide tilt-card reveal">
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
            f"""<article class="pd-grade-card tilt-card reveal">
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
        ov_html = "".join(f"<p>{esc(p)}</p>" for p in overview)
        media = grade_media_html(resolve_grade_image(slug, g), name)
        blocks.append(
            f"""<article class="pd-grade-card pd-grade-card--wide tilt-card reveal">
              {media}
              <span class="pd-grade-tag">{esc(tag)}</span>
              <h3>{esc(name)}</h3>
              {f'<p class="pd-drill-sub">{esc(subtitle)}</p>' if subtitle else ''}
              {ov_html}
            </article>"""
        )
    return f'<div class="pd-grade-grid pd-grade-grid--pair">{"".join(blocks)}</div>' if blocks else ""


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
                        f'<article class="pd-grade-card tilt-card reveal">{media}'
                        f'<span class="pd-grade-tag">{esc(tag)}</span></article>'
                    )
            continue
        if not isinstance(g, dict) or g.get("entries"):
            continue
        tag = g.get("grade") or g.get("name") or "Grade"
        subtitle = g.get("subtitle") or g.get("alumina") or g.get("description") or ""
        media = grade_media_html(resolve_grade_image(slug, g), tag)
        subtitle_html = f'<p class="pd-grade-size">{esc(subtitle)}</p>' if subtitle else ""
        blocks.append(
            f'<article class="pd-grade-card tilt-card reveal">{media}'
            f'<span class="pd-grade-tag">{esc(tag)}</span>'
            f"{subtitle_html}</article>"
        )
    return f'<div class="pd-grade-grid">{"".join(blocks)}</div>' if blocks else ""


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
    return f"""<section class="section pd-section pd-section--mesh" id="pdGrades">
      <div class="container">
        {section_header("Grades", "Available Grades")}
        <div class="reveal reveal-delay-1">{grid}</div>
      </div>
    </section>"""


def packaging_section(items):
    items = filter_items(items)
    if not items:
        return ""
    lead = ""
    if items and items[0].rstrip(":").strip().lower() == "available in":
        lead = items[0] if items[0].endswith(":") else f"{items[0]}:"
        items = items[1:]
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
    lead_html = f'<p class="pd-pack-lead reveal">{esc(lead)}</p>' if lead else ""
    return f"""<section class="section pd-section pd-pack-section" id="pdPackaging">
      <div class="pd-pack-deco" aria-hidden="true">
        <span class="pd-pack-orb pd-pack-orb--1"></span>
        <span class="pd-pack-orb pd-pack-orb--2"></span>
      </div>
      <div class="container">
        {section_header("Export Supply", "Packing Options")}
        {lead_html}
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
            <a href="request-quote.html" class="btn btn-gold">Request a Quote <span class="arrow">&rarr;</span></a>
            <a href="quality-assurance.html" class="btn btn-outline">Quality &amp; Documentation</a>
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
    body = "".join(f"<p>{esc(p)}</p>" for p in paras)
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
        <h2>Looking for a Reliable Industrial Mineral Supply Partner?</h2>
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
    s = product["sections"]
    lead = product.get("subtitle") or ""
    if not lead and s.get("overview"):
        lead = s["overview"][0]
    badge = product.get("hero_badge", "Export Ready")

    parts = [
        head(product["name"], lead or product["name"]),
        '  <div id="header-placeholder"></div>\n  <main>',
        hero(product["name"], fam_label, product["name"], lead, image, fam_file, badge),
        overview_section(s.get("overview", []), image, product.get("overview_panel")),
        benefits_section(s.get("key_benefits") or s.get("key_features")),
        typical_specs_section(product, data),
        applications_section(s.get("applications")),
        grade_section(product),
        packaging_section(s.get("packaging", [])),
    ]
    parts.append(request_section(product["name"], product.get("slug", "")))
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

    content = f"""{head(family['name'], family['short'])}
  <div id="header-placeholder"></div>
  <main>
    {hero(family['name'], 'Product Family', family['name'], family['short'], family['image'], badge_text='Product Family')}
    <section class="section pf-grid-section">
      <div class="container">
        {section_header("Product Range", f"Explore {family['name']} Grades")}
        <div class="pf-grid">{cards}</div>
      </div>
    </section>
    {cta_block(family['name'])}
  </main>
{foot()}"""
    (ROOT / family["file"]).write_text(content, encoding="utf-8")
    print(f"Wrote {family['file']}")


def generate_portfolio_page(data):
    page = data.get("catalog", {}).get("portfolio_page", {})
    families = get_families(data)
    cards = ""
    for i, family in enumerate(families, 1):
        delay = f" reveal-delay-{min(i % 4, 3)}" if i % 4 else ""
        btn = "View Grades" if family.get("single") and family["slug"] in {"korvanto-cham", "korvanto-baux", "korvanto-carbo"} else (
            "View Product" if family.get("single") else "Explore Products"
        )
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
          <p class="page-hero-lead">{esc(page.get('hero_lead', ''))}</p>
          <div class="products-portfolio-stats">{stats_html}</div>
        </div>
        <div class="products-portfolio-visual reveal reveal-delay-1">
          <div class="products-portfolio-frame tilt-card">
            <img src="{esc(page.get('hero_image', ''))}" alt="Korvanto industrial minerals portfolio">
            <span class="pd-hero-badge-float">{esc(page.get('hero_badge', 'Export Portfolio'))}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--mesh">
      <div class="container">
        <header class="inner-section-head inner-section-head--center reveal">
          <p class="section-label">{esc(page.get('section_label', ''))}</p>
          <h2 class="section-title">{esc(page.get('section_title', ''))}</h2>
          <p class="section-lead">{esc(page.get('section_lead', ''))}</p>
        </header>
        <div class="products-family-grid">{cards}</div>
      </div>
    </section>

    <section class="cta-banner">
      <div class="cta-bg"><img src="assets/images/cta/1.png" alt="Export logistics"></div>
      <div class="container cta-content reveal">
        <h2>Looking for a Reliable Industrial Mineral Supply Partner?</h2>
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
            f'                  <a href="{esc(get_product(data, slug).get("page_file") or f"{slug}.html")}">{esc(get_product(data, slug)["name"])}</a>\n'
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
{family_links}                <a href="products.html" class="mega-all">View Full Catalogue →</a>
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
    patch_file_section(HEADER_PATH, MEGA_MENU_START, MEGA_MENU_END, render_mega_menu(data))
    print("Updated components/header.html mega menu")
    patch_file_section(QUOTE_PATH, QUOTE_OPTIONS_START, QUOTE_OPTIONS_END, generate_quote_options(data))
    print("Updated request-quote.html product options")
    print("Done generating product pages.")


if __name__ == "__main__":
    main()
