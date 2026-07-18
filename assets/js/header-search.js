(function () {
  'use strict';
  var lastFocus = null;

  function getBase() {
    var path = window.location.pathname;
    if (path.indexOf('/products/') !== -1 || path.match(/\/[^/]+\/[^/]+\.html/)) {
      return '../';
    }
    return '';
  }

  function buildOverlay() {
    var stale = document.querySelector('#headerProductSearch #headerSearchOverlay');
    if (stale) stale.remove();

    if (document.getElementById('headerSearchOverlay')) {
      var existing = document.getElementById('headerSearchOverlay');
      if (existing.parentNode !== document.body) {
        document.body.appendChild(existing);
      }
      return;
    }

    var overlay = document.createElement('div');
    overlay.id = 'headerSearchOverlay';
    overlay.className = 'search-overlay product-search';
    overlay.setAttribute('hidden', '');
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML =
      '<button type="button" class="search-overlay-backdrop" aria-label="Close search" tabindex="-1"></button>' +
      '<div class="search-overlay-dialog" role="dialog" aria-modal="true" aria-labelledby="headerSearchLabel">' +
      '<div class="search-overlay-inner">' +
      '<div class="search-overlay-top">' +
      '<p id="headerSearchLabel" class="search-overlay-label">Search products &amp; grades</p>' +
      '<button type="button" class="search-overlay-close" id="headerSearchClose" aria-label="Close search">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">' +
      '<path d="M6 6l12 12M18 6L6 18"/>' +
      '</svg>' +
      '</button>' +
      '</div>' +
      '<div class="search-overlay-field product-search-field">' +
      '<input type="search" id="headerSearchInput" class="search-overlay-input product-search-input" ' +
      'placeholder="Type product name grade or code..." autocomplete="off" ' +
      'aria-controls="headerSearchResults" aria-expanded="false" aria-autocomplete="list">' +
      '</div>' +
      '<div class="product-search-results search-overlay-results" id="headerSearchResults" role="listbox" hidden></div>' +
      '</div>' +
      '</div>';

    function mount() {
      if (!overlay.parentNode) {
        document.body.appendChild(overlay);
      }
    }

    if (document.body) mount();
    else document.addEventListener('DOMContentLoaded', mount);
  }

  function bootSearchLogic() {
    if (!window.KorvantoProductSearch) return;
    var overlay = document.getElementById('headerSearchOverlay');
    if (!overlay || overlay.getAttribute('data-search-initialized') === 'true') return;
    window.KorvantoProductSearch.init(overlay, getBase());
  }

  function setOpen(open) {
    buildOverlay();
    var overlay = document.getElementById('headerSearchOverlay');
    var input = document.getElementById('headerSearchInput');
    var results = document.getElementById('headerSearchResults');
    var toggle = document.getElementById('headerSearchToggle');

    if (!overlay || !input) return;

    if (open) {
      lastFocus = document.activeElement;
      overlay.removeAttribute('hidden');
      overlay.classList.add('is-open');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.classList.add('search-overlay-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'true');
      bootSearchLogic();
      window.setTimeout(function () {
        input.focus();
      }, 60);
      return;
    }

    overlay.setAttribute('hidden', '');
    overlay.classList.remove('is-open');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('search-overlay-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
    input.value = '';
    input.blur();
    if (results) {
      results.hidden = true;
      results.innerHTML = '';
    }
    input.setAttribute('aria-expanded', 'false');
    if (lastFocus && typeof lastFocus.focus === 'function') {
      lastFocus.focus();
    }
    lastFocus = null;
  }

  function bindEvents() {
    if (document.documentElement.getAttribute('data-header-search-bound') === 'true') return;
    document.documentElement.setAttribute('data-header-search-bound', 'true');

    document.addEventListener(
      'click',
      function (event) {
        if (event.target.closest('#headerSearchToggle')) {
          event.preventDefault();
          event.stopPropagation();
          setOpen(true);
          return;
        }

        if (
          event.target.closest('#headerSearchClose') ||
          event.target.closest('.search-overlay-backdrop')
        ) {
          event.preventDefault();
          setOpen(false);
        }
      },
      false
    );

    document.addEventListener('keydown', function (event) {
      var overlay = document.getElementById('headerSearchOverlay');
      if (event.key === 'Escape' && overlay && overlay.classList.contains('is-open')) {
        setOpen(false);
        return;
      }
      if (event.key !== 'Tab' || !overlay || !overlay.classList.contains('is-open')) return;
      var focusable = Array.prototype.slice.call(
        overlay.querySelectorAll(
          'button:not([disabled]), [href], input:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      ).filter(function (el) {
        return el.offsetParent !== null;
      });
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  window.KorvantoHeaderSearch = {
    open: function () {
      setOpen(true);
    },
    close: function () {
      setOpen(false);
    }
  };

  buildOverlay();
  bindEvents();

  document.addEventListener('DOMContentLoaded', function () {
    buildOverlay();
    bootSearchLogic();
  });
})();
