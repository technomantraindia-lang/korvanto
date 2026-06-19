#!/usr/bin/env python3
"""Restore original Product-Images paths; remove per-product/grade image overrides."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets/js/products-data.json"


def load_original_data() -> dict:
    raw = subprocess.check_output(
        ["git", "show", "HEAD:assets/js/products-data.json"],
        cwd=ROOT,
    )
    return json.loads(raw.decode("utf-8"))


def strip_grade_images(grades) -> None:
    for grade in grades or []:
        if not isinstance(grade, dict):
            continue
        grade.pop("image", None)
        if grade.get("entries"):
            for entry in grade["entries"]:
                if isinstance(entry, dict):
                    entry.pop("image", None)
        if grade.get("grades"):
            strip_grade_images(grade["grades"])


def main() -> None:
    original = load_original_data()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    orig_families = {f["slug"]: f for f in original.get("catalog", {}).get("families", [])}
    for family in data.get("catalog", {}).get("families", []):
        slug = family.get("slug")
        if slug in orig_families:
            family["image"] = orig_families[slug]["image"]

    portfolio = data.setdefault("catalog", {}).setdefault("portfolio_page", {})
    orig_portfolio = original.get("catalog", {}).get("portfolio_page", {})
    if orig_portfolio.get("hero_image"):
        portfolio["hero_image"] = orig_portfolio["hero_image"]

    for product in data.get("products", []):
        product.pop("image", None)
        product.pop("overview_image", None)
        strip_grade_images(product.get("grades"))

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Restored original family/portfolio image paths and removed product/grade images.")


if __name__ == "__main__":
    main()
