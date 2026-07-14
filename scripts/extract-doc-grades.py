#!/usr/bin/env python3
"""Extract grades from product detail pages for documentation request forms."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QUOTE_SLUGS = [
    "korvanto-bento-drill",
    "korvanto-bento-foundry",
    "korvanto-bento-iop",
    "korvanto-bento-civil",
    "korvanto-bento-feed",
    "korvanto-bento-fert",
    "korvanto-bento-litter",
    "korvanto-bento-paper-deink",
    "korvanto-bento-pharma",
    "korvanto-bento-cosmetic",
    "korvanto-bento-desiccant",
    "korvanto-bento-seal",
    "korvanto-bento-food",
    "korvanto-bento-pencil",
    "korvanto-bento-specialty",
    "korvanto-kao-crude",
    "korvanto-kao-levigated-noodles",
    "korvanto-kao-levigated-lumps",
    "korvanto-kao-hydrous",
    "korvanto-kao-spray",
    "korvanto-kao-calcined",
    "korvanto-kao-metakaolin",
    "korvanto-clay",
    "korvanto-lat",
    "korvanto-cham",
    "korvanto-baux",
    "korvanto-carbo",
]

with open(os.path.join(ROOT, "assets", "js", "products-data.json"), encoding="utf-8") as f:
    data = json.load(f)

json_map = {}


def walk(o):
    if isinstance(o, dict):
        if "slug" in o and isinstance(o.get("grades"), list):
            grades = []
            for g in o["grades"]:
                if isinstance(g, dict):
                    name = g.get("grade") or g.get("name") or g.get("code")
                    if name:
                        grades.append(str(name).strip())
            if grades:
                json_map[o["slug"]] = grades
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(data)

tag_re = re.compile(r'class="pd-grade-tag">([^<]+)<')
code_re = re.compile(r'class="pd-grade-use-code">([^<]+)<')


def uniq(items):
    out = []
    for x in items:
        x = (x or "").strip()
        if x and x not in out:
            out.append(x)
    return out


def normalize_grade(name):
    """Keep short codes; shorten long 'KORVANTO CHAM LF42'-style card labels."""
    m = re.search(r"\b(LF\d+|CB\d+|CA|LCA|HLCA|CS)\b", name, re.I)
    if m and re.search(r"KORVANTO\s+(CHAM|BAUX|CARBO)", name, re.I):
        return m.group(1).upper()
    return name.strip()


mapping = {}
for slug in QUOTE_SLUGS:
    tags = []
    codes = []
    path = os.path.join(ROOT, slug + ".html")
    if os.path.isfile(path):
        html = open(path, encoding="utf-8").read()
        tags = uniq(tag_re.findall(html))
        codes = uniq(code_re.findall(html))

    if tags:
        # Detail-page grade cards are the source of truth (includes CUSTOM / PRIVATE LABEL)
        grades = uniq(normalize_grade(t) for t in tags)
    elif codes:
        grades = codes
    elif json_map.get(slug):
        grades = uniq(json_map[slug])
    else:
        grades = ["Standard / As Per Specification"]

    mapping[slug] = grades
    print(f"{slug}: {grades}")

mapping["multiple"] = ["Multiple Grades / As Per Enquiry"]

out_json = os.path.join(ROOT, "assets", "js", "doc-product-grades.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)
    f.write("\n")

js_path = os.path.join(ROOT, "assets", "js", "doc-request-modals.js")
with open(js_path, encoding="utf-8") as f:
    js = f.read()

# Replace the embedded productGrades object
start = js.find("  var productGrades = {")
end = js.find("  };", start)
if start == -1 or end == -1:
    raise SystemExit("Could not find productGrades block in doc-request-modals.js")

lines = ["  var productGrades = {"]
for slug, grades in mapping.items():
    lines.append(f"    {json.dumps(slug)}: {json.dumps(grades)},")
lines.append("  };")
new_block = "\n".join(lines)
js = js[:start] + new_block + js[end + 4 :]
with open(js_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

print("Updated", out_json)
print("Updated", js_path)
