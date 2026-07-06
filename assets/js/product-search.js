(function () {
  var input = document.getElementById('productSearchInput');
  var results = document.getElementById('productSearchResults');
  if (!input || !results) return;

  var index = [];
  var activeIdx = -1;
  var maxResults = 12;

  function normalize(value) {
    return String(value || '')
      .toLowerCase()
      .replace(/[^\w\s-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function itemHaystack(item) {
    return normalize([item.label, item.family].concat(item.keywords || []).join(' '));
  }

  function matches(item, query) {
    var haystack = itemHaystack(item);
    return query.split(' ').every(function (token) {
      return token && haystack.indexOf(token) !== -1;
    });
  }

  function typeLabel(type) {
    if (type === 'grade') return 'Grade';
    if (type === 'family') return 'Family';
    return 'Product';
  }

  function setExpanded(isOpen) {
    input.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  }

  function hideResults() {
    results.hidden = true;
    results.innerHTML = '';
    activeIdx = -1;
    setExpanded(false);
  }

  function render(items) {
    if (!items.length) {
      results.innerHTML = '<p class="product-search-empty">No matches found. Try a grade code such as LF42, CB80, or F-100.</p>';
      results.hidden = false;
      setExpanded(true);
      return;
    }

    results.innerHTML = items.slice(0, maxResults).map(function (item, idx) {
      var activeClass = idx === activeIdx ? ' is-active' : '';
      var meta = item.family ? item.family + ' · ' + typeLabel(item.type) : typeLabel(item.type);
      return (
        '<a href="' + item.url + '" class="product-search-item' + activeClass + '" role="option">' +
          '<span class="product-search-item-label">' + item.label + '</span>' +
          '<span class="product-search-item-meta">' + meta + '</span>' +
        '</a>'
      );
    }).join('');

    results.hidden = false;
    setExpanded(true);
  }

  function currentMatches() {
    var query = normalize(input.value);
    if (query.length < 2) return [];
    return index.filter(function (item) {
      return matches(item, query);
    });
  }

  function updateResults() {
    activeIdx = -1;
    var query = normalize(input.value);
    if (query.length < 2) {
      hideResults();
      return;
    }
    render(currentMatches());
  }

  fetch('assets/js/product-search-index.json')
    .then(function (response) {
      if (!response.ok) throw new Error('Search index unavailable');
      return response.json();
    })
    .then(function (data) {
      index = Array.isArray(data) ? data : [];
    })
    .catch(function () {
      index = [];
    });

  input.addEventListener('input', updateResults);

  input.addEventListener('keydown', function (event) {
    var items = results.querySelectorAll('.product-search-item');
    if (!items.length) return;

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      activeIdx = Math.min(activeIdx + 1, items.length - 1);
      items[activeIdx].classList.add('is-active');
      if (activeIdx > 0) items[activeIdx - 1].classList.remove('is-active');
      items[activeIdx].scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      activeIdx = Math.max(activeIdx - 1, 0);
      items.forEach(function (node, idx) {
        node.classList.toggle('is-active', idx === activeIdx);
      });
      items[activeIdx].scrollIntoView({ block: 'nearest' });
    } else if (event.key === 'Enter' && activeIdx >= 0) {
      event.preventDefault();
      items[activeIdx].click();
    } else if (event.key === 'Escape') {
      hideResults();
    }
  });

  document.addEventListener('click', function (event) {
    if (!document.getElementById('productSearch').contains(event.target)) {
      hideResults();
    }
  });
})();
