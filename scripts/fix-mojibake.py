#!/usr/bin/env python3
"""Fix UTF-8 mojibake (â€", â€“, â€™, etc.) across the Korvanto site."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".js", ".json", ".css", ".md", ".txt"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# Literal mojibake sequences as they appear in UTF-8 text files
REPLACEMENTS = [
    ("â€”", "—"),  # em dash
    ("â€“", "–"),  # en dash
    ("â€™", "'"),  # right single quote
    ("â€˜", "'"),  # left single quote
    ("â€œ", '"'),  # left double quote
    ("â€", '"'),  # right double quote
    ("â€¦", "..."),  # ellipsis
    ("Â·", "·"),  # middle dot
    ("Â°", "°"),  # degree
    ("â‚‚", "₂"),  # subscript 2
    ("â‚ƒ", "₃"),  # subscript 3
    ("â„¢", "™"),  # trademark
    ("Â²", "²"),  # superscript 2
    ("Â³", "³"),  # superscript 3
    ("Â±", "±"),  # plus-minus
    ("â‰¥", "≥"),
    ("â‰¤", "≤"),
    ("Â ", " "),  # nbsp mis-decoded
    ("â†’", "→"),
    ("â†", "←"),
    ("â˜…", "★"),
]


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    # nested stale copy
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return True
    if len(rel.parts) >= 2 and rel.parts[0] == "korvanto" and rel.parts[1] == "korvanto":
        return True
    return False


def fix_text(text: str) -> tuple[str, int]:
    count = 0
    for bad, good in REPLACEMENTS:
        n = text.count(bad)
        if n:
            text = text.replace(bad, good)
            count += n
    # Catch residual â€ + punctuation leftovers
    for bad, good in [
        ("â€?", "—"),
        ("â€�", '"'),
        ("â€˜", "'"),
    ]:
        n = text.count(bad)
        if n:
            text = text.replace(bad, good)
            count += n
    return text, count


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
                raw = path.read_bytes()
            except OSError:
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
            fixed, n = fix_text(text)
            if n:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                total_files += 1
                total_fixes += n
                print(f"{n:4d}  {path.relative_to(ROOT)}")
    print(f"\nDone: {total_fixes} replacements in {total_files} files")


if __name__ == "__main__":
    main()
