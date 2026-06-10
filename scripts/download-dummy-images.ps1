# Downloads placeholder images (Picsum) into assets/images/ for local UI preview
$root = Join-Path $PSScriptRoot "..\assets\images"
$map = @{
  "hero\slide-port.jpg"            = "https://picsum.photos/seed/korvanto-port/1920/1080.jpg"
  "hero\slide-vessel.jpg"          = "https://picsum.photos/seed/korvanto-vessel/1920/1080.jpg"
  "hero\slide-terminal.jpg"        = "https://picsum.photos/seed/korvanto-terminal/1920/1080.jpg"
  "brand\mineral-handling.jpg"     = "https://picsum.photos/seed/korvanto-handling/1400/600.jpg"
  "products\bentonite.jpg"         = "https://picsum.photos/seed/korvanto-bentonite/900/675.jpg"
  "products\kaolin.jpg"            = "https://picsum.photos/seed/korvanto-kaolin/900/675.jpg"
  "products\ball-clay.jpg"         = "https://picsum.photos/seed/korvanto-ballclay/900/675.jpg"
  "products\chamotte.jpg"          = "https://picsum.photos/seed/korvanto-chamotte/900/675.jpg"
  "products\calcined-bauxite.jpg"  = "https://picsum.photos/seed/korvanto-bauxite/900/675.jpg"
  "products\laterite.jpg"          = "https://picsum.photos/seed/korvanto-laterite/900/675.jpg"
  "products\coal-additive.jpg"     = "https://picsum.photos/seed/korvanto-coal/900/675.jpg"
  "process\material.jpg"           = "https://picsum.photos/seed/korvanto-material/900/1125.jpg"
  "process\laboratory.jpg"         = "https://picsum.photos/seed/korvanto-lab/900/1125.jpg"
  "process\jumbo-bags.jpg"         = "https://picsum.photos/seed/korvanto-jumbo/900/1125.jpg"
  "process\port-dispatch.jpg"      = "https://picsum.photos/seed/korvanto-dispatch/900/1125.jpg"
  "cta\logistics.jpg"              = "https://picsum.photos/seed/korvanto-logistics/1920/1080.jpg"
  "about\hero.jpg"                 = "https://picsum.photos/seed/korvanto-about-hero/1200/800.jpg"
  "about\quarry.jpg"               = "https://picsum.photos/seed/korvanto-quarry/900/600.jpg"
  "about\minerals.jpg"             = "https://picsum.photos/seed/korvanto-minerals/900/600.jpg"
  "export\jumbo-bags.jpg"          = "https://picsum.photos/seed/korvanto-export-bags/900/600.jpg"
  "export\container.jpg"           = "https://picsum.photos/seed/korvanto-container/900/600.jpg"
  "export\vessel.jpg"              = "https://picsum.photos/seed/korvanto-export-ship/1920/1080.jpg"
  "quality\lab.jpg"                = "https://picsum.photos/seed/korvanto-quality-lab/900/600.jpg"
  "contact\hero.jpg"               = "https://picsum.photos/seed/korvanto-contact/1200/700.jpg"
  "quote\hero.jpg"                 = "https://picsum.photos/seed/korvanto-quote/900/1100.jpg"
}

foreach ($rel in $map.Keys) {
  $out = Join-Path $root $rel
  $dir = Split-Path $out -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  Write-Host "Downloading $rel ..."
  try {
    Invoke-WebRequest -Uri $map[$rel] -OutFile $out -UseBasicParsing -TimeoutSec 90
    if ((Get-Item $out).Length -lt 1000) { throw "File too small" }
  } catch {
    Write-Warning "Failed: $rel - $_"
  }
}
Write-Host "Done. $(($map.Keys | Measure-Object).Count) files mapped."
