#!/usr/bin/env python3
"""Remove unwanted punctuation from user-facing website text.

This intentionally avoids removing commas from code syntax. It cleans:
- HTML text nodes and selected human-readable attributes
- JSON string values
- JavaScript string literals in assets
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
TEXT_ATTRS = {
    "alt",
    "aria-label",
    "content",
    "placeholder",
    "title",
    "value",
}


def clean_text(value: str, remove_question: bool = True, remove_comma: bool = True) -> str:
    replacements = {
        "\u2122": "",
        "&trade;": "",
        "&#8482;": "",
        "â„¢": "",
        "ï¿½": "",
        "\ufffd": "",
    }
    if remove_comma:
        replacements[","] = ""
    if remove_question:
        replacements["?"] = ""
    for bad, good in replacements.items():
        value = value.replace(bad, good)
    value = value.replace("â€”", "-").replace("â€“", "-")
    value = value.replace("â€™", "'").replace("â€˜", "'")
    value = value.replace("â€œ", '"').replace("â€\u009d", '"')
    value = re.sub(r" +", " ", value)
    value = re.sub(r" +([.;:!])", r"\1", value)
    return value


def looks_like_selector(value: str) -> bool:
    return bool(
        re.search(r"[.#\[]", value)
        or re.fullmatch(
            r"(?:input|textarea|select|button|form|a|div|span|label)(?:\s*,\s*(?:input|textarea|select|button|form|a|div|span|label))+",
            value,
        )
    )


def clean_attrs(tag: str) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        quote = match.group(2)
        value = match.group(3)
        if name.lower() not in TEXT_ATTRS:
            return match.group(0)
        return f"{name}={quote}{clean_text(value)}{quote}"

    return re.sub(r"([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(['\"])(.*?)\2", repl, tag)


def clean_html(text: str) -> str:
    out: list[str] = []
    i = 0
    in_raw: str | None = None
    while i < len(text):
        if text.startswith("<!--", i):
            j = text.find("-->", i + 4)
            if j == -1:
                out.append(text[i:])
                break
            out.append(text[i : j + 3])
            i = j + 3
            continue

        if text[i] == "<":
            j = text.find(">", i + 1)
            if j == -1:
                out.append(text[i:])
                break
            tag = text[i : j + 1]
            low = tag.lower()
            out.append(clean_attrs(tag))
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
        out.append(chunk if in_raw else clean_text(chunk))
        i = j
    return "".join(out)


def clean_json_value(value):
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        return [clean_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_json_value(item) for key, item in value.items()}
    return value


def clean_json_file(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    fixed = clean_json_value(data)
    if fixed == data:
        return False
    path.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return True


def clean_js_strings(text: str) -> str:
    out: list[str] = []
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
                functional_query = value.startswith("?") or re.search(r"\.[A-Za-z0-9]+[?]", value)
                out.append(
                    clean_text(
                        value,
                        remove_question=not functional_query,
                        remove_comma=not looks_like_selector(value),
                    )
                )
                out.append(ch)
                quote = None
                buf = []
            else:
                buf.append(ch)
            i += 1
            continue

        if ch in {"'", '"', "`"}:
            quote = ch
            out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1

    if quote:
        value = "".join(buf)
        functional_query = value.startswith("?") or re.search(r"\.[A-Za-z0-9]+[?]", value)
        out.append(
            clean_text(
                value,
                remove_question=not functional_query,
                remove_comma=not looks_like_selector(value),
            )
        )
    return "".join(out)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> None:
    changed: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if should_skip(path):
                continue
            if "scripts" in path.relative_to(ROOT).parts:
                continue

            suffix = path.suffix.lower()
            if suffix == ".html":
                original = path.read_text(encoding="utf-8")
                fixed = clean_html(original)
            elif suffix == ".json":
                if clean_json_file(path):
                    changed.append(path)
                continue
            elif suffix == ".js" and "assets" in path.relative_to(ROOT).parts:
                original = path.read_text(encoding="utf-8")
                fixed = clean_js_strings(original)
            else:
                continue

            if fixed != original:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                changed.append(path)

    for path in changed:
        print(path.relative_to(ROOT))
    print(f"Done: {len(changed)} files updated")


if __name__ == "__main__":
    main()
