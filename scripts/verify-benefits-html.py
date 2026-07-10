import html as html_lib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("generate_pages", ROOT / "scripts" / "generate-pages.py")
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)

data = json.loads((ROOT / "assets/js/products-data.json").read_text(encoding="utf-8"))
CARD_RE = re.compile(r'pd-benefit-card[^>]*>.*?<p>([^<]+)</p>', re.S)
SHARED = set(gp.SHARED_KEY_BENEFITS) | {
    "Meets API and OCMA performance standards",
    "Meets API 13A performance standards",
    "Meets OCMA performance standards",
}

issues = []
for product in data["products"]:
    page_file = product.get("page_file")
    if not page_file:
        continue
    path = ROOT / page_file
    if not path.exists():
        issues.append((page_file, "missing file"))
        continue
    expected = gp.resolve_product_benefits(product)
    rendered = [html_lib.unescape(b) for b in CARD_RE.findall(path.read_text(encoding="utf-8"))]
    slug = product.get("slug", "")
    if rendered != expected:
        issues.append((page_file, f"count rendered={len(rendered)} expected={len(expected)}"))
        for i, (a, b) in enumerate(zip(rendered, expected), 1):
            if a != b:
                issues.append((page_file, f"  #{i} rendered={a!r} expected={b!r}"))
                break
    for benefit in rendered:
        if benefit in SHARED and slug not in gp.DRILLING_BENEFIT_SLUGS:
            issues.append((page_file, f"drilling benefit on wrong page: {benefit}"))
        if gp.is_grade_name_benefit(benefit):
            issues.append((page_file, f"grade-like benefit: {benefit}"))

if issues:
    print("ISSUES FOUND:\n")
    for page, msg in issues:
        print(f"{page}: {msg}")
    raise SystemExit(1)

print("All product detail pages match resolved benefits with no drilling or grade-name issues.")
