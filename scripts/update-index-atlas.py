import re
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "index.html"
text = path.read_text(encoding="utf-8")
families = [
    ("korvanto-bento.html", "KORVANTO BENTO\u2122", "Premium bentonite grades for drilling, foundry, civil, feed, fertilizer and specialty industrial applications.", "Bentonite.png", "BENTO"),
    ("korvanto-kao.html", "KORVANTO KAO\u2122", "Kaolin grades including crude, levigated, hydrous, calcined and metakaolin for ceramics, paints, paper and plastics.", "Kaolin-China-Clay.png", "KAO"),
    ("korvanto-clay.html", "KORVANTO CLAY\u2122", "KORVANTO CLAY BALL — premium ball clay for ceramic, sanitaryware, tile and porcelain manufacturing.", "Ball-Clay.png", "CLAY"),
    ("korvanto-cham.html", "KORVANTO CHAM\u2122", "Calcined refractory chamotte — grades LF42, LF46, LF54, LF60, LF70 for high-temperature applications.", "Chamotte-Calcined-Clay-Refractory-Clay.png", "CHAM"),
    ("korvanto-baux.html", "KORVANTO BAUX\u2122", "Calcined bauxite refractory aggregate — grades CB80, CB82, CB86 for demanding thermal applications.", "Calcined-Bauxite.png", "BAUX"),
    ("korvanto-lat.html", "KORVANTO LAT\u2122", "Iron and alumina-rich laterite for cement manufacturing, construction and industrial applications.", "Laterite.png", "LAT"),
    ("korvanto-carbo.html", "KORVANTO CARBO\u2122", "Lustrous carbon additive for green sand foundry — grades CA, LCA, HLCA, CS.", "Coal-Additive-Lustrous-Coal.png", "CARBO"),
]
text = text.replace("Seven Minerals.<br>One Export Partner.", "Seven Product Families.<br>One Export Partner.")
for href, title, desc, img, idxname in families:
    text = re.sub(
        r'<a href="[^"]+" class="atlas-panel-link">\s*<div class="atlas-panel-media">\s*<img src="assets/images/Product-Images/[^"]+" alt="[^"]*">',
        f'<a href="{href}" class="atlas-panel-link">\n                  <div class="atlas-panel-media">\n                    <img src="assets/images/Product-Images/{img}" alt="{title}">',
        text,
        count=1,
    )
    text = re.sub(
        r'<h3 class="atlas-panel-title">[^<]+</h3>\s*<p class="atlas-panel-desc">[^<]+</p>',
        f'<h3 class="atlas-panel-title">{title}</h3>\n                    <p class="atlas-panel-desc">{desc}</p>',
        text,
        count=1,
    )
    text = re.sub(
        r'<span class="atlas-index-name">[^<]+</span></button>',
        f'<span class="atlas-index-name">{idxname}</span></button>',
        text,
        count=1,
    )
path.write_text(text, encoding="utf-8")
print("index.html atlas updated")
