#!/usr/bin/env python3
"""Rebuild index.html mineral atlas from products-data.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "assets/js/products-data.json"

# Homepage atlas uses mineral display names (not KORVANTO brand codes).
HOMEPAGE_ATLAS_ORDER = [
    "korvanto-bento",
    "korvanto-kao",
    "korvanto-clay",
    "korvanto-cham",
    "korvanto-baux",
    "korvanto-lat",
    "korvanto-carbo",
]

ATLAS_TITLES = {
    "korvanto-bento": "Bentonite",
    "korvanto-kao": "Kaolin (China Clay)",
    "korvanto-clay": "Ball Clay",
    "korvanto-cham": "Chamotte / Calcined Clay",
    "korvanto-baux": "Calcined Bauxite",
    "korvanto-lat": "Laterite",
    "korvanto-carbo": "Coal Additive / Lustrous Coal",
}

ATLAS_INDEX_NAMES = {
    "korvanto-bento": "Bentonite",
    "korvanto-kao": "Kaolin",
    "korvanto-clay": "Ball Clay",
    "korvanto-cham": "Chamotte",
    "korvanto-baux": "Calcined Bauxite",
    "korvanto-lat": "Laterite",
    "korvanto-carbo": "Coal Additive",
}

ATLAS_ALT = {
    "korvanto-bento": "Bentonite mineral supply",
    "korvanto-kao": "Kaolin china clay",
    "korvanto-clay": "Ball clay",
    "korvanto-cham": "Chamotte calcined clay",
    "korvanto-baux": "Calcined bauxite",
    "korvanto-lat": "Laterite mineral",
    "korvanto-carbo": "Coal additive lustrous coal",
}


def esc(text):
    return html.escape(str(text or ""))


def ordered_families(data):
    by_slug = {f["slug"]: f for f in data.get("catalog", {}).get("families", [])}
    families = [by_slug[slug] for slug in HOMEPAGE_ATLAS_ORDER if slug in by_slug]
    if not families:
        raise SystemExit("No families in products-data.json")
    return families


def panel_article(i, family, active=False):
    idx = f"{i + 1:02d}"
    cls = "atlas-panel is-active" if active else "atlas-panel"
    slug = family.get("slug", "")
    img = family.get("image") or "assets/images/Product-Images/Bentonite.png"
    title = ATLAS_TITLES.get(slug, family.get("name", ""))
    alt = ATLAS_ALT.get(slug, title)
    short = family.get("short", "")
    return f"""              <article class="{cls}" data-index="{i}">
                <a href="{esc(family.get('file', '#'))}" class="atlas-panel-link">
                  <div class="atlas-panel-media">
                    <img src="{esc(img)}" alt="{esc(alt)}">
                  </div>
                  <div class="atlas-panel-content">
                    <span class="atlas-panel-index">{idx}</span>
                    <h3 class="atlas-panel-title">{esc(title)}</h3>
                    <p class="atlas-panel-desc">{esc(short)}</p>
                    <span class="atlas-panel-cta">View specification &amp; Applications  <span class="arrow">&rarr;</span></span>
                  </div>
                </a>
              </article>"""


def index_button(i, family, active=False):
    idx = f"{i + 1:02d}"
    cls = "atlas-index-item is-active" if active else "atlas-index-item"
    slug = family.get("slug", "")
    label = ATLAS_INDEX_NAMES.get(slug, family.get("name", ""))
    return f"""          <button type="button" class="{cls}" data-index="{i}"><span class="atlas-index-num">{idx}</span><span class="atlas-index-name">{esc(label)}</span></button>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    families = ordered_families(data)

    text = INDEX.read_text(encoding="utf-8")
    panels = "\n".join(panel_article(i, f, i == 0) for i, f in enumerate(families))
    buttons = "\n".join(index_button(i, f, i == 0) for i, f in enumerate(families))

    text = re.sub(
        r'(<div class="atlas-stage" id="atlasStage">)\s*.*?\s*(</div>\s*<div class="atlas-progress")',
        lambda m: f'{m.group(1)}\n{panels}\n            {m.group(2)}',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<nav class="atlas-index reveal" aria-label="Select product">)\s*.*?\s*(</nav>)',
        lambda m: f'{m.group(1)}\n{buttons}\n        {m.group(2)}',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(
        '<span class="atlas-counter-total">07</span>',
        f'<span class="atlas-counter-total">{len(families):02d}</span>',
    )
    INDEX.write_text(text, encoding="utf-8")
    print(f"Rebuilt index.html mineral atlas with {len(families)} family images")


if __name__ == "__main__":
    main()
