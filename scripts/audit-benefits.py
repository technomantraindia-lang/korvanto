import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "assets/js/products-data.json").read_text(encoding="utf-8"))

DRILL_BENEFITS = {
    "API / OCMA compliant",
    "High Yield",
    "Excellent Gel Strength",
    "Low Fluid Loss",
    "Borehole Stabilization",
    "Efficient Cuttings Suspension",
    "Easy Mixing",
    "Thermal Stability",
    "Consistent Batch Quality",
}
DRILL_SLUGS = {"korvanto-bento-drill", "korvanto-bento-drill-api", "korvanto-bento-drill-ocma"}

GRADE_NAME_RE = re.compile(
    r"(?:"
    r"\b(?:API|OCMA|AG-\d+|C-\d+|F-\d+|LF\d+)\b.*(?:grade|compliant)"
    r"|(?:High Purity )?[A-Za-z]+ Grade (?:Bentonite|Kaolin)"
    r"|^OCMA-compliant quality$"
    r"|^API / OCMA compliant$"
    r"|\b(?:KORVANTO )?BENTO (?:FEED|FERT|IOP|DRILL|CIVIL|SEAL)\b"
    r"|Grade [A-Z]{1,3}-\d+"
    r")",
    re.I,
)


def all_products(d):
    prods = list(d.get("products", []))
    for fam in d.get("families", []):
        prods.extend(fam.get("products", []))
    return prods


def audit_benefit(slug, benefit):
    issues = []
    if benefit in DRILL_BENEFITS and slug not in DRILL_SLUGS:
        issues.append("drilling-benefit-on-wrong-page")
    if GRADE_NAME_RE.search(benefit):
        issues.append("grade-name-in-benefit")
    if re.match(r"^[A-Z]{2,}-\d{2,3}\b", benefit.strip()):
        issues.append("grade-code-as-benefit")
    return issues


print("=== products-data.json key_benefits audit ===\n")
for product in all_products(data):
    slug = product.get("slug", "")
    sections = product.get("sections") or {}
    benefits = sections.get("key_benefits") or sections.get("key_features") or []
    if not benefits:
        continue
    product_issues = []
    for i, benefit in enumerate(benefits, 1):
        for issue in audit_benefit(slug, benefit):
            product_issues.append((issue, i, benefit))
    if product_issues:
        print(slug)
        for issue, i, benefit in product_issues:
            print(f"  [{issue}] #{i}: {benefit}")
        print()

print("=== rendered HTML audit ===\n")
pattern = re.compile(r'<span class="pd-benefit-num">\d+</span>\s*<p>([^<]+)</p>')
for html in sorted(ROOT.glob("korvanto-*.html")):
    text = html.read_text(encoding="utf-8")
    if "pd-benefit-num" not in text:
        continue
    slug = html.stem
    benefits = pattern.findall(text)
    product_issues = []
    for i, benefit in enumerate(benefits, 1):
        for issue in audit_benefit(slug, benefit):
            product_issues.append((issue, i, benefit))
    if product_issues:
        print(html.name)
        for issue, i, benefit in product_issues:
            print(f"  [{issue}] #{i}: {benefit}")
        print()
