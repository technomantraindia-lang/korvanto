const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'index.html');
let s = fs.readFileSync(file, 'utf8');

s = s.replace(/<span class="arrow">[^<]*<\/span>/g, '<span class="arrow">&rarr;</span>');
s = s.replace(
  /<span class="why-panel-arrow"[^>]*>[^<]*<\/span>/g,
  '<span class="why-panel-arrow" aria-hidden="true">&rarr;</span>'
);
s = s.replace(
  /(<button[^>]*id="atlasPrev"[^>]*>)[^<]*(<\/button>)/,
  '$1&larr;$2'
);
s = s.replace(
  /(<button[^>]*id="atlasNext"[^>]*>)[^<]*(<\/button>)/,
  '$1&rarr;$2'
);

const replacements = [
  [/\u00e2\u20ac\u201d/g, '\u2014'],
  [/\u00e2\u20ac\u201c/g, '\u2014'],
  [/\u00e2\u20ac\u2122/g, "'"],
  [/\u00e2\u20ac\u00a6/g, '\u2026'],
  [/\u00e2\u2020\u2019/g, '\u2192'],
  [/\u00e2\u2020\u0090/g, '\u2190'],
  [/\u00e2\u2020\u2018/g, '\u2192'],
  [/&larr;\u2019/g, '&rarr;'],
  [/&larr;\u0090/g, '&larr;'],
  [/â€"/g, '\u2014'],
  [/â€™/g, "'"],
  [/â€¦/g, '\u2026']
];

replacements.forEach(function (pair) {
  s = s.replace(pair[0], pair[1]);
});

s = s.replace(/<span aria-hidden="true">[^<]*<\/span>(?=\s*<\/div>\s*<\/div>\s*<blockquote)/g, '<span aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span>');
s = s.replace(/<div class="spotlight-rating"[^>]*><span aria-hidden="true">[^<]*<\/span><\/div>/g, '<div class="spotlight-rating" aria-label="5 out of 5 stars"><span aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span></div>');
s = s.replace(/\u00c2\u00b7/g, ' &middot; ');
s = s.replace(/ Â· /g, ' &middot; ');
s = s.replace(/YÄ±lmaz/g, 'Yilmaz');
s = s.replace(/\u00e2\u02dc\u2026/g, '\u2605');
s = s.replace(/â˜…/g, '\u2605');

fs.writeFileSync(file, s, 'utf8');
console.log('index.html encoding fixed');
