#!/usr/bin/env python3
"""Point legacy product pages to korvanto-branded pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REDIRECTS = {
    "kaolin.html": "korvanto-kao.html",
    "ball-clay.html": "korvanto-clay.html",
    "chamotte.html": "korvanto-cham.html",
    "calcined-bauxite.html": "korvanto-baux.html",
    "laterite.html": "korvanto-lat.html",
    "coal-additive.html": "korvanto-carbo.html",
}


def redirect_page(src: str, target: str) -> None:
    title = target.replace("korvanto-", "").replace(".html", "").replace("-", " ").title()
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
  <title>{title} | Korvanto</title>
  <script>location.replace("{target}");</script>
</head>
<body>
  <p>Redirecting to <a href="{target}">{target}</a>…</p>
</body>
</html>
"""
    (ROOT / src).write_text(content, encoding="utf-8")
    print(f"Redirect {src} -> {target}")


def main():
    for src, target in REDIRECTS.items():
        redirect_page(src, target)


if __name__ == "__main__":
    main()
