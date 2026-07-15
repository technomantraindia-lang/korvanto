#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", "scripts"}
BAD = {",", "?", "\u2122"}
BAD_ENTITIES = ("&trade;", "&#8482;")
TEXT_ATTRS = {"alt", "aria-label", "content", "placeholder", "title", "value"}


def bad_chars(value: str) -> list[str]:
    hits = [ch for ch in BAD if ch in value]
    hits.extend(entity for entity in BAD_ENTITIES if entity.lower() in value.lower())
    return hits


def check_html(path: Path, text: str) -> list[str]:
    hits: list[str] = []
    i = 0
    in_raw: str | None = None
    while i < len(text):
        if text.startswith("<!--", i):
            j = text.find("-->", i + 4)
            i = len(text) if j == -1 else j + 3
            continue
        if text[i] == "<":
            j = text.find(">", i + 1)
            if j == -1:
                break
            tag = text[i : j + 1]
            low = tag.lower()
            for match in re.finditer(r"([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(['\"])(.*?)\2", tag):
                if match.group(1).lower() in TEXT_ATTRS and bad_chars(match.group(3)):
                    hits.append(f"{path}: attr {match.group(1)} -> {match.group(3)[:80]}")
            if low.startswith("<script") and not low.startswith("</script"):
                in_raw = "script"
            elif low.startswith("<style") and not low.startswith("</style"):
                in_raw = "style"
            elif low.startswith("</script") or low.startswith("</style"):
                in_raw = None
            i = j + 1
            continue
        j = text.find("<", i)
        if j == -1:
            j = len(text)
        chunk = text[i:j]
        if not in_raw and bad_chars(chunk):
            snippet = " ".join(chunk.split())[:100]
            if snippet:
                hits.append(f"{path}: text -> {snippet}")
        i = j
    return hits


def walk_json_strings(value, path: Path, hits: list[str]) -> None:
    if isinstance(value, str):
        if bad_chars(value):
            hits.append(f"{path}: json -> {value[:100]}")
    elif isinstance(value, list):
        for item in value:
            walk_json_strings(item, path, hits)
    elif isinstance(value, dict):
        for item in value.values():
            walk_json_strings(item, path, hits)


def check_js_strings(path: Path, text: str) -> list[str]:
    hits: list[str] = []
    i = 0
    quote: str | None = None
    escape = False
    buf: list[str] = []
    while i < len(text):
        ch = text[i]
        if quote:
            if escape:
                buf.append(ch)
                escape = False
            elif ch == "\\":
                buf.append(ch)
                escape = True
            elif ch == quote:
                value = "".join(buf)
                if bad_chars(value):
                    hits.append(f"{path}: js string -> {value[:100]}")
                quote = None
                buf = []
            else:
                buf.append(ch)
            i += 1
            continue
        if ch in {"'", '"', "`"}:
            quote = ch
        i += 1
    return hits


def main() -> None:
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            suffix = path.suffix.lower()
            if suffix not in {".html", ".json", ".js"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            rel = path.relative_to(ROOT)
            if suffix == ".html":
                hits.extend(check_html(rel, text))
            elif suffix == ".json":
                try:
                    data = json.loads(text)
                except Exception:
                    continue
                walk_json_strings(data, rel, hits)
            elif suffix == ".js" and "assets" in rel.parts:
                hits.extend(check_js_strings(rel, text))

    if hits:
        print(f"{len(hits)} visible/string punctuation hits")
        for hit in hits[:80]:
            print(hit)
    else:
        print("CLEAN")


if __name__ == "__main__":
    main()
