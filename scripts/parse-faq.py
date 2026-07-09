#!/usr/bin/env python3
"""Parse product FAQ content from FAQ docx files into assets/js/product-faqs.json."""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "assets" / "js" / "product-faqs.json"
LEGACY_OUT_PATH = ROOT / "assets" / "js" / "bentonite-faqs.json"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

SECTION_RULES = [
    (re.compile(r"^BENTONITE PRODUCTS PAGE$|^Bentonite Family FAQs$", re.I), "korvanto-bento", "Bentonite Family FAQs"),
    (re.compile(r"KORVANTO BENTO DRILL.*FAQs", re.I), "korvanto-bento-drill", "KORVANTO BENTO DRILL FAQs"),
    (re.compile(r"KORVANTO BENTO IOP.*FAQs", re.I), "korvanto-bento-iop", "KORVANTO BENTO IOP FAQs"),
    (re.compile(r"KORVANTO BENTO FEED.*FAQs", re.I), "korvanto-bento-feed", "KORVANTO BENTO FEED FAQs"),
    (re.compile(r"KORVANTO BENTO LITTER.*FAQs", re.I), "korvanto-bento-litter", "KORVANTO BENTO LITTER FAQs"),
    (re.compile(r"KORVANTO BENTO PHARMA.*FAQs", re.I), "korvanto-bento-pharma", "KORVANTO BENTO PHARMA FAQs"),
    (re.compile(r"KORVANTO BENTO DESIC.*FAQs", re.I), "korvanto-bento-desiccant", "KORVANTO BENTO DESIC FAQs"),
    (re.compile(r"KORVANTO BENTO FOOD.*FAQs", re.I), "korvanto-bento-food", "KORVANTO BENTO FOOD FAQs"),
    (re.compile(r"KORVANTO BENTO SPECIAL.*FAQs", re.I), "korvanto-bento-specialty", "KORVANTO BENTO SPECIAL FAQs"),
    (re.compile(r"KORVANTO BENTO FOUNDRY.*FAQs", re.I), "korvanto-bento-foundry", "KORVANTO BENTO FOUNDRY FAQs"),
    (re.compile(r"^Bento civil$", re.I), "korvanto-bento-civil", "KORVANTO BENTO CIVIL FAQs"),
    (re.compile(r"^Fertilizer grade$", re.I), "korvanto-bento-fert", "KORVANTO BENTO FERTILIZER FAQs"),
    (re.compile(r"KORVANTO BENTO PAPER-325", re.I), "korvanto-bento-paper-deink:paper", "KORVANTO BENTO PAPER-325"),
    (re.compile(r"KORVANTO BENTO DEINK-100", re.I), "korvanto-bento-paper-deink:deink", "KORVANTO BENTO DEINK-100"),
    (re.compile(r"^KORVANTO BENTO COSMETIC$", re.I), "korvanto-bento-cosmetic", "KORVANTO BENTO COSMETIC FAQs"),
    (re.compile(r"^KORVANTO BENTO SEAL$", re.I), "korvanto-bento-seal", "KORVANTO BENTO SEAL FAQs"),
    (re.compile(r"^KORVANTO BENTO PENCIL$", re.I), "korvanto-bento-pencil", "KORVANTO BENTO PENCIL FAQs"),
    (re.compile(r"KORVANTO KAO CRUDE", re.I), "korvanto-kao-crude", "KORVANTO KAO CRUDE FAQs"),
    (re.compile(r"^Levigated noodles$", re.I), "korvanto-kao-levigated-noodles", "KORVANTO KAO NOODLES FAQs"),
    (re.compile(r"^Levigated lumps$", re.I), "korvanto-kao-levigated-lumps", "KORVANTO KAO LUMPS FAQs"),
    (re.compile(r"^Hydrous kaolin$", re.I), "korvanto-kao-hydrous", "KORVANTO KAO HYDRO FAQs"),
    (re.compile(r"^Spray dried kaolin$", re.I), "korvanto-kao-spray", "KORVANTO KAO SPRAY FAQs"),
    (re.compile(r"^Calicined kaolin$|^Calcined kaolin$", re.I), "korvanto-kao-calcined", "KORVANTO KAO CAL FAQs"),
    (re.compile(r"^Meta kaolin$", re.I), "korvanto-kao-metakaolin", "KORVANTO META FAQs"),
    (re.compile(r"Kaolin product page faq", re.I), "korvanto-kao", "Kaolin Family FAQs"),
    (re.compile(r"^Ball clay$", re.I), "korvanto-clay", "KORVANTO BALL FAQs"),
    (re.compile(r"^Laterite$", re.I), "korvanto-lat", "KORVANTO LATER FAQs"),
    (re.compile(r"^Chamotte$|^Calcined chamotte$", re.I), "korvanto-cham", "KORVANTO CHAM FAQs"),
    (re.compile(r"^Calcined bauxite$|^Bauxite$", re.I), "korvanto-baux", "KORVANTO BAUX FAQs"),
    (re.compile(r"^Lustrous carbon|^KORVANTO CARBO|Carbon additive", re.I), "korvanto-carbo", "KORVANTO CARBO FAQs"),
]

FAQ_SECTION_START = re.compile(r"^Frequently Asked Questions \(FAQs\)$", re.I)

STOP_LINE = re.compile(
    r"^(Suggested Applications|Suggested Key Benefits|Suggested note|Disclaimer:|"
    r"Paper grade$|Recommended for:|"
    r"Standard Fertilizer Grade$|Granulation Grade$|Premium Granule Binder Grade$|"
    r"Pond Sealant Powder Grade$|Pond Sealant Granular Grade$|Export-Ready Qualiy$|"
    r"Levigated noodles$|Levigated lumps$|Hydrous kaolin$|Spray dried kaolin$|"
    r"Calicined kaolin$|Calcined kaolin$|Meta kaolin$|Kaolin product page faq$|"
    r"Ball clay$|Laterite$|Chamotte$|Calcined chamotte$|Bauxite$|Calcined bauxite$|"
    r"Lustrous carbon|KORVANTO KAO CRUDE)",
    re.I,
)

QUESTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")

CHAMOTTE_FAQ_TRIGGER = re.compile(r"^1\.\s+What is KORVANTO CHAM", re.I)
BAUXITE_FAQ_TRIGGER = re.compile(r"^1\.\s+What is KORVANTO BAUX", re.I)
CARBO_FAQ_TRIGGER = re.compile(r"^1\.\s+What is KORVANTO CARBO", re.I)
HYDROUS_FAQ_TRIGGER = re.compile(r"^1\.\s+What is KORVANTO KAO HYDRO", re.I)


def extract_lines(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    lines = []
    for para in root.iter(f"{W_NS}p"):
        text = "".join((node.text or "") for node in para.iter(f"{W_NS}t")).strip()
        if text:
            lines.append(text.replace("\ufffd", "™"))
    return lines


def match_section(line: str):
    for pattern, slug, title in SECTION_RULES:
        if pattern.search(line):
            return slug, title
    return None


def parse_faqs(lines: list[str]) -> dict:
    sections: dict[str, dict] = {}
    current_slug = None
    current_title = None
    current_group = None
    current_question = None
    answer_lines: list[str] = []
    pending_faq_header = False

    def store_question():
        nonlocal current_question, answer_lines
        if not current_slug or not current_question:
            return
        answer = "\n".join(answer_lines).strip()
        if not answer:
            return
        entry = {"question": current_question, "answer": answer}
        if ":" in current_slug:
            base, group_key = current_slug.split(":", 1)
            sec = sections.setdefault(base, {"title": "Frequently Asked Questions", "groups": {}})
            grp = sec["groups"].setdefault(
                current_group or group_key,
                {"title": current_title or group_key.upper(), "items": []},
            )
            grp["items"].append(entry)
        else:
            sec = sections.setdefault(current_slug, {"title": current_title or "FAQs", "items": []})
            sec["items"].append(entry)
        current_question = None
        answer_lines = []

    def start_section(slug: str, title: str):
        nonlocal current_slug, current_title, current_group, pending_faq_header
        store_question()
        current_slug = slug
        current_title = title
        current_group = title if ":" in slug else None
        pending_faq_header = False

    for line in lines:
        section_match = match_section(line)
        if section_match:
            start_section(*section_match)
            continue

        if FAQ_SECTION_START.match(line):
            pending_faq_header = True
            continue

        if pending_faq_header and QUESTION_RE.match(line):
            pending_faq_header = False
            if CHAMOTTE_FAQ_TRIGGER.match(line):
                start_section("korvanto-cham", "KORVANTO CHAM FAQs")
            elif BAUXITE_FAQ_TRIGGER.match(line):
                start_section("korvanto-baux", "KORVANTO BAUX FAQs")
            elif CARBO_FAQ_TRIGGER.match(line):
                start_section("korvanto-carbo", "KORVANTO CARBO FAQs")
            elif HYDROUS_FAQ_TRIGGER.match(line):
                start_section("korvanto-kao-hydrous", "KORVANTO KAO HYDRO FAQs")
            elif not current_slug:
                continue

        if not current_slug:
            continue

        if STOP_LINE.match(line):
            store_question()
            continue

        q_match = QUESTION_RE.match(line)
        if q_match:
            store_question()
            current_question = q_match.group(2).strip()
            continue

        if line.strip().lower() == "answer":
            continue

        if current_question:
            answer_lines.append(line)

    store_question()
    return sections


def normalize_paper_deink(sections: dict) -> dict:
    paper = sections.pop("korvanto-bento-paper-deink", None)
    if not paper or "groups" not in paper:
        return sections
    groups = list(paper["groups"].values())
    sections["korvanto-bento-paper-deink"] = {
        "title": "Frequently Asked Questions",
        "groups": groups,
    }
    return sections


def merge_sections(target: dict, incoming: dict) -> dict:
    for slug, data in incoming.items():
        if slug not in target:
            target[slug] = data
            continue
        if data.get("items"):
            target[slug] = data
    return target


def resolve_docx_paths() -> list[Path]:
    paths = []
    for candidate in [
        Path.home() / "Downloads" / "FAQ-1.docx",
        Path.home() / "Downloads" / "FAQ.docx",
        ROOT / "FAQ-1.docx",
        ROOT / "FAQ.docx",
    ]:
        if candidate.exists() and candidate not in paths:
            paths.append(candidate)
    return paths


def main():
    docx_paths = resolve_docx_paths()
    if not docx_paths:
        raise SystemExit("No FAQ.docx or FAQ-1.docx found in Downloads or project root.")

    sections: dict = {}
    for docx in docx_paths:
        lines = extract_lines(docx)
        parsed = normalize_paper_deink(parse_faqs(lines))
        sections = merge_sections(sections, parsed)
        print(f"Parsed {docx.name}: {len(parsed)} sections")

    OUT_PATH.write_text(json.dumps(sections, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LEGACY_OUT_PATH.write_text(json.dumps(sections, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    for slug, data in sorted(sections.items()):
        if "items" in data:
            print(f"  {slug}: {len(data['items'])} FAQs")
        else:
            total = sum(len(g["items"]) for g in data.get("groups", []))
            print(f"  {slug}: {total} FAQs in {len(data.get('groups', []))} groups")


if __name__ == "__main__":
    main()
