"""Shared deduplication helpers for product benefits and applications."""

import re

SKIP_EXACT = {
    "Website Category Description (for KORVANTO BENTO DRILL)",
}

APPLICATION_GENERIC_TOKENS = {
    "application", "applications", "care", "components", "control", "core",
    "equipment", "formulation", "formulations", "goods", "grade", "grades",
    "hygiene", "industries", "industry", "line", "lines", "manufacturing",
    "materials", "operations", "packaging", "processing", "product", "products",
    "production", "projects", "sector", "solutions", "systems", "type", "types",
    "use", "uses", "works",
}


def filter_items(items):
    skip_prefixes = ("Website Category Description", "Bottom of Form")
    out = []
    for item in items or []:
        if item in SKIP_EXACT:
            continue
        if any(item.startswith(p) for p in skip_prefixes):
            continue
        if item.endswith(" is widely used in:"):
            continue
        out.append(item)
    return out


def normalize_text_key(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def benefit_tokens(text):
    stop = {
        "a", "an", "and", "at", "for", "in", "of", "the", "to", "with",
        "good", "excellent", "effective", "superior", "enhanced", "improved",
        "reliable", "consistent", "high", "low", "quality", "performance",
    }
    return {t for t in normalize_text_key(text).split() if len(t) > 2 and t not in stop}


def application_tokens(text):
    stop = {
        "a", "an", "and", "at", "for", "in", "of", "the", "to", "with",
    }
    return {
        t for t in normalize_text_key(text).split()
        if len(t) > 2 and t not in stop and t not in APPLICATION_GENERIC_TOKENS
    }


def is_benefit_noise(item):
    if not item or len(item.strip()) < 4:
        return True
    if item.startswith("KORVANTO "):
        return True
    if re.match(r"^Al[₂2]?O[₃3]", item):
        return True
    if item.rstrip(": ").lower() in {"suitable for", "key benefits", "applications"}:
        return True
    if re.match(r"^~?\d", item.strip()):
        return True
    return False


def benefits_are_similar(a, b):
    ka, kb = normalize_text_key(a), normalize_text_key(b)
    if not ka or not kb:
        return False
    if ka == kb:
        return True
    if ka in kb or kb in ka:
        return True
    ta, tb = benefit_tokens(a), benefit_tokens(b)
    if not ta or not tb:
        return False
    overlap = ta & tb
    return len(overlap) / min(len(ta), len(tb)) >= 0.55


def applications_are_similar(a, b):
    ka, kb = normalize_text_key(a), normalize_text_key(b)
    if not ka or not kb:
        return False
    if ka == kb:
        return True
    if ka in kb or kb in ka:
        return True

    ta, tb = application_tokens(a), application_tokens(b)
    if not ta or not tb:
        return False

    overlap = ta & tb
    if not overlap:
        return False
    if len(overlap) / min(len(ta), len(tb)) < 0.55:
        return False

    unique = (ta - tb) | (tb - ta)
    if unique and unique.issubset(APPLICATION_GENERIC_TOKENS):
        return True

    raw_a = set(normalize_text_key(a).split())
    raw_b = set(normalize_text_key(b).split())
    raw_unique = (raw_a - raw_b) | (raw_b - raw_a)
    return bool(raw_unique) and raw_unique.issubset(APPLICATION_GENERIC_TOKENS)


def dedupe_benefits(items):
    cleaned = []
    for item in filter_items(items):
        if is_benefit_noise(item):
            continue
        if any(benefits_are_similar(item, kept) for kept in cleaned):
            continue
        cleaned.append(item)
    return cleaned


def dedupe_applications(items):
    cleaned = []
    for item in filter_items(items):
        if any(applications_are_similar(item, kept) for kept in cleaned):
            continue
        cleaned.append(item)
    return cleaned
