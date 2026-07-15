#!/usr/bin/env python3
"""Scan and strip encoding junk + unnecessary trademark symbols sitewide."""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".js", ".json", ".css", ".md", ".txt"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# Mojibake / broken sequences -> correct or remove
MOJIBAKE = [
    ("â„¢", ""),  # broken TM -> remove
    ("â€”", "-"),
    ("â€“", "-"),
    ("â€™", "'"),
    ("â€˜", "'"),
    ("â€œ", '"'),
    ("â€", '"'),
    ("â€¦", "..."),
    ("â‰¥", ">="),
    ("â‰¤", "<="),
    ("Â·", "·"),
    ("Â°", "°"),
    ("Â±", "±"),
    ("Â²", "2"),
    ("Â³", "3"),
    ("â‚‚", "2"),
    ("â‚ƒ", "3"),
    ("Â ", " "),
    ("â†’", "->"),
    ("â†", "<-"),
    ("â˜…", "*"),
    ("ï¿½", ""),
    ("�", ""),
]

# Proper trademark / trade entities -> remove (user: unnecessary)
TM_PATTERNS = [
    (re.compile(r"™"), ""),
    (re.compile(r"&#8482;", re.I), ""),
    (re.compile(r"&trade;", re.I), ""),
]


def should_skip(path: Path) -> bool:
    if any(p in SKIP_DIRS for p in path.parts):
        return True
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return True
    if len(rel.parts) >= 2 and rel.parts[0] == "korvanto" and rel.parts[1] == "korvanto":
        return True
    # Don't rewrite the fixer/scanner scripts themselves
    if path.name in {"scan-and-strip-symbols.py", "fix-mojibake.py", "fix-all-pages.js", "fix-index-encoding.js"}:
        return True
    return False


def fix_text(text: str) -> tuple[str, int]:
    n = 0
    for bad, good in MOJIBAKE:
        c = text.count(bad)
        if c:
            text = text.replace(bad, good)
            n += c
    for rx, repl in TM_PATTERNS:
        text2, c = rx.subn(repl, text)
        if c:
            text = text2
            n += c
    # Collapse accidental double spaces left by TM removal in titles
    text2 = re.sub(r" {2,}", " ", text)
    if text2 != text:
        text = text2
    return text, n


def main() -> None:
    total_files = 0
    total_fixes = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in EXTS or should_skip(path):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fixed, n = fix_text(text)
            if n and fixed != text:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                total_files += 1
                total_fixes += n
                print(f"{n:4d}  {path.relative_to(ROOT)}")
    print(f"\nDone: {total_fixes} replacements in {total_files} files")


if __name__ == "__main__":
    main()
