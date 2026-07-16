#!/usr/bin/env python3
"""Capitalize KORVANTO in overview product names and append ™ once per brand mention."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Brand product names that already use all-caps product codes after Korvanto
BRAND_RE = re.compile(
    r"\bKorvanto\s+"
    r"("
    r"BENTO(?:\s+(?:DRILL|FOUNDRY|IOP|CIVIL|FEED|FERT|LITTER|PAPER\s*&\s*DEINK|PAPER\s*&amp;\s*DEINK|PHARMA|COSMETIC|DESICCANT|SEAL|FOOD|PENCIL|SPECIALTY))?"
    r"|KAO(?:\s+(?:CRUDE|LEVIGATED\s+NOODLES|LEVIGATED\s+LUMPS|HYDROUS|SPRAY|CALCINED|METAKAOLIN|CAL|HYDRO|NOODLES))?"
    r"|CHAM"
    r"|BAUX"
    r"|CARBO"
    r"|CLAY(?:\s+BALL)?"
    r"|LATER"
    r"|LAT"
    r")"
    r"(?!™)"
)

# Title-case product names in overview (e.g. Korvanto Laterite)
TITLE_RE = re.compile(
    r"\bKorvanto\s+"
    r"("
    r"Laterite|Bentonite|Ball Clay|Carbon|Chamotte|Bauxite|"
    r"Crude Kaolin|Levigated Kaolin Noodles|Levigated Kaolin Lumps|"
    r"Hydrous Kaolin|Spray Dried Kaolin|Calcined Kaolin|Meta Kaolin"
    r")"
    r"(?!™)"
)


def transform_overview(block: str) -> str:
    def brand_sub(m: re.Match[str]) -> str:
        name = m.group(1)
        # normalize amp entity spacing already in source
        return f"KORVANTO {name}™"

    def title_sub(m: re.Match[str]) -> str:
        return f"KORVANTO {m.group(1).upper()}™"

    block = BRAND_RE.sub(brand_sub, block)
    block = TITLE_RE.sub(title_sub, block)
    return block


def main() -> None:
    changed = 0
    for path in sorted(ROOT.glob("korvanto-*.html")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r'(<section[^>]*id="pdOverview"[^>]*>)([\s\S]*?)(</section>)', text)
        if not match:
            continue
        old = match.group(2)
        new = transform_overview(old)
        if new == old:
            continue
        text = text[: match.start(2)] + new + text[match.end(2) :]
        path.write_text(text, encoding="utf-8", newline="\n")
        changed += 1
        print(path.name)
    print(f"Updated {changed} product detail pages")


if __name__ == "__main__":
    main()
