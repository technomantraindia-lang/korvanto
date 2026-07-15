(function () {
  'use strict';

  var index = [];
  var indexLoaded = false;
  var indexPromise = null;

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

  function loadIndex(base) {
    if (indexLoaded) return Promise.resolve(index);
    if (indexPromise) return indexPromise;

    indexPromise = fetch((base || '') + 'assets/js/product-search-index.json')
      .then(function (response) {
        if (!response.ok) throw new Error('Search index unavailable');
        return response.json();
      })
      .then(function (data) {
        index = Array.isArray(data) ? data : [];
        indexLoaded = true;
        return index;
      })
      .catch(function () {
        index = [];
        indexLoaded = true;
        return index;
      });

    return indexPromise;
  }

  function isHeaderSearch(root) {
    return root.classList.contains('header-search') || root.id === 'headerSearchOverlay';
  }

  function initProductSearch(root, base) {
    if (!root || root.getAttribute('data-search-initialized') === 'true') return;

    var input = isHeaderSearch(root)
      ? document.getElementById('headerSearchInput')
      : root.querySelector('.product-search-input');
    var results = isHeaderSearch(root)
      ? document.getElementById('headerSearchResults')
      : root.querySelector('.product-search-results');
    if (!input || !results) return;

    root.setAttribute('data-search-initialized', 'true');

    var activeIdx = -1;
    var maxResults = isHeaderSearch(root) ? 12 : 12;

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
        results.innerHTML =
          '<p class="product-search-empty">No matches found. Try a grade code such as F30 LF42 or Hydrous Kaolin.</p>';
        results.hidden = false;
        setExpanded(true);
        return;
      }

      results.innerHTML = items
        .slice(0, maxResults)
        .map(function (item, idx) {
          var activeClass = idx === activeIdx ? ' is-active' : '';
          var meta = item.family
            ? item.family + ' · ' + typeLabel(item.type)
            : typeLabel(item.type);
          return (
            '<a href="' +
            (base || '') +
            item.url +
            '" class="product-search-item' +
            activeClass +
            '" role="option">' +
            '<span class="product-search-item-label">' +
            item.label +
            '</span>' +
            '<span class="product-search-item-meta">' +
            meta +
            '</span>' +
            '</a>'
          );
        })
        .join('');

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

    loadIndex(base).then(updateResults);

    input.addEventListener('input', updateResults);

    input.addEventListener('focus', function () {
      if (normalize(input.value).length >= 2) updateResults();
    });

    if (isHeaderSearch(root)) {
      input.addEventListener('mousedown', function (event) {
        event.stopPropagation();
      });

      root.addEventListener('mousedown', function (event) {
        event.stopPropagation();
      });
    } else {
      document.addEventListener('click', function (event) {
        if (!root.contains(event.target)) hideResults();
      });
    }

    var field = root.querySelector('.product-search-field');
    if (field) {
      field.addEventListener('click', function (event) {
        if (event.target.closest('.product-search-results')) return;
        input.focus();
      });
    }

    input.addEventListener('keydown', function (event) {
      var items = results.querySelectorAll('.product-search-item');
      if (!items.length) return;

      if (event.key === 'ArrowDown') {
        event.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
        items.forEach(function (node, idx) {
          node.classList.toggle('is-active', idx === activeIdx);
        });
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
      } else if (event.key === 'Escape' && !isHeaderSearch(root)) {
        hideResults();
        input.blur();
      }
    });
  }

  function initAll(base) {
    document.querySelectorAll('.product-search').forEach(function (root) {
      initProductSearch(root, base);
    });
  }

  window.KorvantoProductSearch = {
    initAll: initAll,
    init: initProductSearch,
    loadIndex: loadIndex
  };
})();
