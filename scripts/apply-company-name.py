#!/usr/bin/env python3
"""Apply Korvanto LLP company naming in prose across JSON and static HTML files."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_dedupe import format_company_prose

ROOT = Path(__file__).resolve().parents[1]

JSON_FILES = [
    ROOT / "assets/js/product-faqs.json",
    ROOT / "assets/js/bentonite-faqs.json",
    ROOT / "assets/js/products-data.json",
]

HTML_FILES = [
    ROOT / "index.html",
    ROOT / "about.html",
    ROOT / "contact.html",
    ROOT / "certifications.html",
    ROOT / "quality-assurance.html",
    ROOT / "export-packaging.html",
    ROOT / "global-supply.html",
    ROOT / "products.html",
    ROOT / "disclaimer.html",
    ROOT / "terms.html",
    ROOT / "privacy-policy.html",
    ROOT / "shipping-policy.html",
    ROOT / "components/footer.html",
    ROOT / "request-quote.html",
]

PROSE_JSON_KEYS = {
    "overview",
    "answer",
    "lead",
    "hero_lead",
    "section_lead",
    "short",
    "short_website_description",
    "custom_note",
    "forms_section_lead",
    "available_forms_lead",
    "subtitle",
}

SKIP_JSON_KEYS = {
    "slug",
    "file",
    "page_file",
    "family",
    "single",
    "href",
    "url",
    "image",
    "hero_image",
    "overview_image",
    "value",
    "name",
    "title",
    "grade",
    "product",
    "code",
    "id",
    "header",
    "key",
    "label",
    "alt",
}

PROSE_TAG_RE = re.compile(
    r"(<(?:p|div)(?:\s[^>]*)?>)(.*?)(</(?:p|div)>)",
    re.I | re.S,
)


def process_json_value(value, key=None):
    if isinstance(value, str):
        if key in SKIP_JSON_KEYS:
            return value
        if key in PROSE_JSON_KEYS or key is None and len(value) > 40:
            return format_company_prose(value)
        if re.search(r"\bKorvanto\b(?! LLP)\s+(?:supplies|offers|can|supports|operates|maintains|primarily|was|has|also|delivers|ensures)", value, re.I):
            return format_company_prose(value)
        return value
    if isinstance(value, list):
        parent_key = key
        return [process_json_value(item, parent_key) for item in value]
    if isinstance(value, dict):
        return {item_key: process_json_value(item, item_key) for item_key, item in value.items()}
    return value


def should_process_html_tag(open_tag: str) -> bool:
    classes = (
        "section-lead",
        "page-hero-lead",
        "footer-desc",
        "pd-faq-answer",
        "about-manifesto-text",
        "about-exists-text",
        "cta-tagline",
        "pd-custom-lead",
        "pd-forms-lead",
        "pd-request-lead",
    )
    return any(cls in open_tag for cls in classes) or open_tag.lower().startswith("<p")


def process_html(text: str) -> str:
    def repl(match):
        open_tag, body, close_tag = match.groups()
        if not should_process_html_tag(open_tag):
            return match.group(0)
        if "korvanto" not in body.lower():
            return match.group(0)
        return f"{open_tag}{format_company_prose(body)}{close_tag}"

    return PROSE_TAG_RE.sub(repl, text)


def main():
    for path in JSON_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        updated = process_json_value(data)
        path.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")

    for path in HTML_FILES:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = process_html(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"Updated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
