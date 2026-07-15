#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXTS = {".html", ".js", ".json", ".css"}
SKIP = {".git", "node_modules", "__pycache__", "scripts"}
checks = [
    ("mojibake", re.compile(r"â.|Â[^A-Za-z0-9\n]")),
    ("tm", re.compile(r"™|&trade;|&#8482;", re.I)),
    ("replacement", re.compile(r"ï¿½|�")),
]

out = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in EXTS:
        continue
    if any(s in p.parts for s in SKIP):
        continue
    rel = p.relative_to(ROOT)
    if rel.parts and rel.parts[0] == "korvanto":
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for name, rx in checks:
        for m in rx.finditer(t):
            i = m.start()
            frag = repr(t[max(0, i - 20) : i + 25])
            out.append(f"{rel}\t{name}\t{frag}")

dest = ROOT / "scripts" / "_scan-out.txt"
dest.write_text("\n".join(out) if out else "CLEAN", encoding="utf-8")
print(f"{len(out)} hits -> {dest}")
