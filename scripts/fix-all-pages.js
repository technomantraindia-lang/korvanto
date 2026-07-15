const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const productHrefs = [
  'bentonite.html',
  'kaolin.html',
  'ball-clay.html',
  'chamotte.html',
  'calcined-bauxite.html',
  'laterite.html',
  'coal-additive.html'
];

function fixEncoding(s) {
  s = s.replace(/<span class="arrow">[^<]*<\/span>/g, '<span class="arrow">&rarr;</span>');
  s = s.replace(
    /<span class="why-panel-arrow"[^>]*>[^<]*<\/span>/g,
    '<span class="why-panel-arrow" aria-hidden="true">&rarr;</span>'
  );
  const reps = [
    [/\u00e2\u20ac\u201d/g, '\u2014'],
    [/\u00e2\u20ac\u201c/g, '\u2014'],
    [/\u00e2\u20ac\u2122/g, "'"],
    [/\u00e2\u20ac\u00a6/g, '\u2026'],
    [/\u00e2\u2020\u2019/g, '\u2192'],
    [/\u00e2\u2020\u0090/g, '\u2190'],
    [/\u00c2\u00b7/g, ' &middot; '],
    [/â€"/g, '\u2014'],
    [/'/g, "'"],
    [/.../g, '\u2026'],
    [/â†'/g, '&rarr;'],
    [/â†\u0090/g, '&larr;']
  ];
  reps.forEach(function (pair) {
    s = s.replace(pair[0], pair[1]);
  });
  return s;
}

function fixIndexAtlas(s) {
  productHrefs.forEach(function (href, i) {
    const re = new RegExp(
      '(<article class="atlas-panel(?: is-active)?" data-index="' + i + '">)\\s*<div class="atlas-panel-link">',
      'g'
    );
    s = s.replace(re, '$1\n                <a href="' + href + '" class="atlas-panel-link">');
  });
  s = s.replace(/<\/div>\s*<\/article>\s*(?=<article class="atlas-panel"|<\/div>\s*<div class="atlas-progress")/g, function (m) {
    return m.replace(/<\/div>\s*<\/article>/, '</a>\n              </article>');
  });
  let idx = 0;
  s = s.replace(/class="atlas-panel-link">[\s\S]*?<\/div>\s*(?=\s*<\/article>)/g, function (block) {
    if (block.indexOf('</a>') !== -1) return block;
    const href = productHrefs[idx++];
    return block.replace('</div>\n              </article>', '</a>\n              </article>').replace(
      /<div class="atlas-panel-link">/,
      '<a href="' + href + '" class="atlas-panel-link">'
    );
  });
  return s;
}

const htmlFiles = fs.readdirSync(root).filter(function (f) {
  return f.endsWith('.html');
});

htmlFiles.forEach(function (file) {
  const fp = path.join(root, file);
  let s = fs.readFileSync(fp, 'utf8');
  s = fixEncoding(s);

  if (file === 'index.html') {
    s = s.replace(
      '<span class="btn btn-gold">Explore Products <span class="arrow">&rarr;</span></span>',
      '<a href="products.html" class="btn btn-gold">Explore Products <span class="arrow">&rarr;</span></a>'
    );
    s = s.replace(
      '<span class="btn btn-outline">Request a Quote <span class="arrow">&rarr;</span></span>',
      '<a href="request-quote.html" class="btn btn-outline">Request a Quote <span class="arrow">&rarr;</span></a>'
    );
    s = s.replace(
      '<span class="btn btn-gold atlas-cta">Full Product Catalogue <span class="arrow">&rarr;</span></span>',
      '<a href="products.html" class="btn btn-gold atlas-cta">Full Product Catalogue <span class="arrow">&rarr;</span></a>'
    );
    s = s.replace(
      '<span class="btn btn-gold">Request a Quote <span class="arrow">&rarr;</span></span>',
      '<a href="request-quote.html" class="btn btn-gold">Request a Quote <span class="arrow">&rarr;</span></a>'
    );
    productHrefs.forEach(function (href, i) {
      s = s.replace(
        new RegExp('(<article class="atlas-panel[^"]*" data-index="' + i + '">)\\s*<div class="atlas-panel-link">'),
        '$1\n                <a href="' + href + '" class="atlas-panel-link">'
      );
    });
    s = s.replace(
      /(<span class="atlas-panel-cta">View specification <span class="arrow">&rarr;<\/span><\/span>\s*<\/div>\s*)<\/div>(\s*<\/article>)/g,
      '$1</a>$2'
    );
    s = s.replace(/<a href="[^"]+" class="atlas-panel-link">[\s\S]*?<\/a>\n              <\/a>/g, function (m) {
      return m.replace(/<\/a>\n              <\/a>/, '</a>');
    });
    if (!s.includes('home-responsive.css')) {
      s = s.replace(
        'assets/css/shared/responsive.css">',
        'assets/css/shared/responsive.css">\n  <link rel="stylesheet" href="assets/css/pages/home-responsive.css">'
      );
    }
    s = s.replace(
      '<section class="section export-world">\n      <div class="container">\n        <p class="section-label reveal">Global Reach</p>\n        <h2 class="section-title reveal">Exporting Minerals Across the World</h2>\n        <p class="section-lead reveal">',
      '<section class="section export-world">\n      <div class="container">\n        <div class="home-section-head reveal">\n        <p class="section-label">Global Reach</p>\n        <h2 class="section-title">Exporting Minerals Across the World</h2>\n        <p class="section-lead">'
    );
    s = s.replace(
      'aligned to your procurement workflow.</p>\n        <div class="export-layout">',
      'aligned to your procurement workflow.</p>\n        </div>\n        <div class="export-layout">'
    );
    s = s.replace(
      '<header class="testimonials-header reveal">',
      '<header class="testimonials-header home-section-head reveal">'
    );
  }

  fs.writeFileSync(fp, s, 'utf8');
  console.log('Fixed', file);
});
