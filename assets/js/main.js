(function () {
  'use strict';

  var BASE = (function () {
    var path = window.location.pathname;
    if (path.indexOf('/products/') !== -1 || path.match(/\/[^/]+\/[^/]+\.html/)) {
      return '../';
    }
    return '';
  })();

  function $(sel, ctx) {
    return (ctx || document).querySelector(sel);
  }

  function $$(sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  }

  /* ——— Load header & footer ——— */
  function loadPartial(id, url, callback) {
    var el = document.getElementById(id);
    if (!el) return;
    fetch(BASE + url)
      .then(function (r) {
        if (!r.ok) throw new Error('Failed to load ' + url);
        return r.text();
      })
      .then(function (html) {
        el.innerHTML = html;
        fixRelativeLinks(el);
        if (callback) callback();
      })
      .catch(function () {
        if (id === 'header-placeholder') {
          el.innerHTML =
            '<header class="site-header is-scrolled"><div class="container header-inner"><a href="' +
            BASE +
            'index.html" class="logo" aria-label="Korvanto Home"><span class="logo-mark-wrap"><img src="' +
            BASE +
            'assets/images/logo/Korvanto%20logo_Black.png" alt="Korvanto LLP — Delivering Quality Globally" class="logo-img" width="280" height="92"></span></a><p style="color:#fff;font-size:0.85rem;">Run via local server (e.g. npx serve) to load full navigation.</p></div></header>';
        }
      });
  }

  function fixRelativeLinks(container) {
    if (!BASE) return;
    $$('a[href]', container).forEach(function (a) {
      var href = a.getAttribute('href');
      if (
        href &&
        !href.startsWith('http') &&
        !href.startsWith('mailto:') &&
        !href.startsWith('tel:') &&
        !href.startsWith('#') &&
        !href.startsWith(BASE)
      ) {
        a.setAttribute('href', BASE + href);
      }
    });
    $$('img[src]', container).forEach(function (img) {
      var src = img.getAttribute('src');
      if (
        src &&
        !src.startsWith('http') &&
        !src.startsWith('data:') &&
        !src.startsWith(BASE)
      ) {
        img.setAttribute('src', BASE + src);
      }
    });
  }

  function initHeader() {
    var header = $('#siteHeader');
    var toggle = $('#navToggle');
    var nav = $('#mainNav');
    if (!header) return;

    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if (toggle && nav) {
      var closeBtn = $('#navClose');
      var backdrop = $('#navBackdrop');

      function setNavOpen(open) {
        nav.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        document.body.classList.toggle('nav-open', open);
        if (backdrop) {
          backdrop.hidden = !open;
          backdrop.setAttribute('aria-hidden', open ? 'false' : 'true');
        }
      }

      toggle.addEventListener('click', function () {
        setNavOpen(!nav.classList.contains('is-open'));
      });

      if (closeBtn) {
        closeBtn.addEventListener('click', function () {
          setNavOpen(false);
        });
      }

      if (backdrop) {
        backdrop.addEventListener('click', function () {
          setNavOpen(false);
        });
      }

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && nav.classList.contains('is-open')) {
          setNavOpen(false);
        }
      });

      $$('.main-nav a', nav).forEach(function (link) {
        link.addEventListener('click', function () {
          setNavOpen(false);
        });
      });
    }

    $$('.dropdown-trigger').forEach(function (btn) {
      var parent = btn.closest('.has-dropdown');
      if (!parent) return;

      var mobileDropdown = window.matchMedia('(max-width: 768px), (hover: none)');

      btn.addEventListener('click', function (e) {
        if (!mobileDropdown.matches) return;
        e.preventDefault();
        var open = parent.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });

      if (window.matchMedia('(hover: hover)').matches) {
        parent.addEventListener('mouseenter', function () {
          if (mobileDropdown.matches) return;
          parent.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
        });
        parent.addEventListener('mouseleave', function () {
          if (mobileDropdown.matches) return;
          parent.classList.remove('is-open');
          btn.setAttribute('aria-expanded', 'false');
        });
      }
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.has-dropdown')) {
        $$('.has-dropdown.is-open').forEach(function (d) {
          d.classList.remove('is-open');
          var t = $('.dropdown-trigger', d);
          if (t) t.setAttribute('aria-expanded', 'false');
        });
      }
    });

    setActiveNav();
    bootProductSearch();
  }

  function bootProductSearch() {
    if (!window.KorvantoProductSearch) return;

    var headerOverlay = document.getElementById('headerSearchOverlay');
    if (headerOverlay) {
      headerOverlay.removeAttribute('data-search-initialized');
      window.KorvantoProductSearch.init(headerOverlay, BASE);
    }

    document.querySelectorAll('.product-search').forEach(function (root) {
      if (root.id !== 'headerSearchOverlay') {
        window.KorvantoProductSearch.init(root, BASE);
      }
    });
  }

  function setActiveNav() {
    var page = window.location.pathname.split('/').pop() || 'index.html';
    var map = {
      'index.html': 'home',
      'about.html': 'about',
      'quality-assurance.html': 'quality',
      'certifications.html': 'quality',
      'export-packaging.html': 'export',
      'global-supply.html': 'global',
      'contact.html': 'contact',
      'request-quote.html': 'contact'
    };
    var key = map[page];
    if (key) {
      $$('[data-nav="' + key + '"]').forEach(function (a) {
        a.classList.add('is-active');
      });
    }
    if (
      page === 'products.html' ||
      page.indexOf('korvanto-') === 0 ||
      [
        'bentonite.html',
        'kaolin.html',
        'ball-clay.html',
        'chamotte.html',
        'calcined-bauxite.html',
        'laterite.html',
        'coal-additive.html'
      ].indexOf(page) !== -1
    ) {
      $$('.dropdown-trigger').forEach(function (b) {
        b.classList.add('is-active');
      });
    }
  }

  /* ——— Hero slider ——— */
  function initHeroSlider() {
    var slider = $('.hero-slider');
    if (!slider) return;
    var slides = $$('.hero-slide', slider);
    var dots = $$('.hero-dot', slider.parentElement || slider);
    var current = 0;
    var interval = 5500;
    var timer;

    function goTo(i) {
      current = (i + slides.length) % slides.length;
      slides.forEach(function (s, idx) {
        s.classList.toggle('is-active', idx === current);
      });
      dots.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === current);
        d.setAttribute('aria-selected', idx === current);
      });
    }

    function next() {
      goTo(current + 1);
    }

    function start() {
      clearInterval(timer);
      timer = setInterval(next, interval);
    }

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        goTo(i);
        start();
      });
    });

    goTo(0);
    start();
  }

  function initPortfolioHeroSlider() {
    var slider = $('.products-hero-slider');
    if (!slider) return;
    var root = slider.closest('.products-hero-showcase') || slider.parentElement;
    var slides = $$('.products-hero-slide', slider);
    var dots = $$('.products-hero-dot', root);
    var captions = $$('.products-hero-caption', root);
    var metas = $$('.products-hero-meta', root);
    var counter = $('.products-hero-counter .is-current', root);
    var current = 0;
    var interval = 5000;
    var timer;

    function goTo(i) {
      current = (i + slides.length) % slides.length;
      slides.forEach(function (s, idx) {
        s.classList.toggle('is-active', idx === current);
      });
      captions.forEach(function (c, idx) {
        c.classList.toggle('is-active', idx === current);
      });
      metas.forEach(function (m, idx) {
        m.classList.toggle('is-active', idx === current);
      });
      dots.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === current);
        d.setAttribute('aria-selected', idx === current);
      });
      if (counter) {
        counter.textContent = String(current + 1).padStart(2, '0');
      }
    }

    function next() {
      goTo(current + 1);
    }

    function start() {
      clearInterval(timer);
      timer = setInterval(next, interval);
    }

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        goTo(i);
        start();
      });
    });

    goTo(0);
    start();
  }

  /* ——— Scroll reveal ——— */
  function initReveal() {
    var els = $$('.reveal');
    if (!els.length || !('IntersectionObserver' in window)) {
      els.forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
    );
    els.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ——— Parallax ——— */
  function initParallax() {
    var items = $$('[data-parallax]');
    if (!items.length) return;

    var onMove = function (e) {
      if (window.innerWidth < 992) return;
      var x = (e.clientX / window.innerWidth - 0.5) * 2;
      var y = (e.clientY / window.innerHeight - 0.5) * 2;
      items.forEach(function (el) {
        var strength = parseFloat(el.getAttribute('data-parallax')) || 12;
        el.style.transform =
          'translate3d(' + x * strength + 'px,' + y * strength * 0.6 + 'px,0)';
      });
    };

    function resetParallax() {
      if (window.innerWidth >= 992) return;
      items.forEach(function (el) {
        el.style.transform = '';
      });
    }

    window.addEventListener('mousemove', onMove, { passive: true });
    window.addEventListener('resize', resetParallax);
    resetParallax();

    var scrollItems = $$('[data-scroll-parallax]');
    if (!scrollItems.length) return;
    var onScroll = function () {
      if (window.innerWidth < 768) {
        scrollItems.forEach(function (el) {
          el.style.transform = '';
        });
        return;
      }
      scrollItems.forEach(function (el) {
        var rect = el.getBoundingClientRect();
        var center = rect.top + rect.height / 2 - window.innerHeight / 2;
        var factor = parseFloat(el.getAttribute('data-scroll-parallax')) || 0.08;
        el.style.transform = 'translate3d(0,' + center * factor + 'px,0)';
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ——— Hero 3D card ——— */
  function initHeroCard() {
    var card = $('.hero-float-card');
    var wrap = $('.hero-3d-wrap');
    if (!card || !wrap) return;
    wrap.addEventListener('mousemove', function (e) {
      var r = wrap.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width - 0.5;
      var py = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform =
        'rotateY(' + px * 8 + 'deg) rotateX(' + -py * 8 + 'deg) translateZ(24px)';
    });
    wrap.addEventListener('mouseleave', function () {
      card.style.transform = 'rotateY(0) rotateX(0) translateZ(24px)';
    });
  }

  /* ——— Product card tilt ——— */
  function initCardTilt() {
    if (window.matchMedia('(hover: none), (max-width: 768px)').matches) return;
    $$('.tilt-card').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.setProperty('--tilt-x', y * -6 + 'deg');
        card.style.setProperty('--tilt-y', x * 6 + 'deg');
      });
      card.addEventListener('mouseleave', function () {
        card.style.setProperty('--tilt-x', '0deg');
        card.style.setProperty('--tilt-y', '0deg');
      });
    });
  }

  /* ——— Journey: pinned multi-step scroll, then next section ——— */
  function initJourney() {
    var section = $('#journeySection');
    var scrollTrack = $('#journeyScrollTrack');
    if (!section || !scrollTrack) return;

    var rail = $('#journeyRail');
    var fill = $('#journeyRailFill');
    var steps = $$('.journey-step', section);
    var dots = $$('.journey-rail-icon', rail);
    var iconCenter = 23;
    var visuals = $$('.journey-visual img', section);
    var stepCount = steps.length;
    var activeIndex = 0;
    var usePinScroll = window.innerWidth > 768;

    function syncRailGeometry() {
      if (!rail || !dots.length) return;
      var trackEl = $('.journey-rail-track', rail);
      var h = rail.offsetHeight;
      var max = Math.max(0, h - 46);

      dots.forEach(function (dot, i) {
        var pct = stepCount <= 1 ? 0 : i / (stepCount - 1);
        dot.style.top = pct * max + 'px';
      });

      if (trackEl && dots[0] && dots[stepCount - 1]) {
        var top = parseFloat(dots[0].style.top, 10) + iconCenter;
        var bottom = parseFloat(dots[stepCount - 1].style.top, 10) + iconCenter;
        trackEl.style.top = top + 'px';
        trackEl.style.height = Math.max(0, bottom - top) + 'px';
      }

      updateProgress(activeIndex, 1);
    }

    function updateProgress(index, segmentT) {
      if (!fill || !dots.length) return;
      var t = typeof segmentT === 'number' ? segmentT : 1;
      var start = parseFloat(dots[0].style.top, 10) + iconCenter;
      var end0 = parseFloat(dots[index].style.top, 10) + iconCenter;
      var end1 =
        index < stepCount - 1
          ? parseFloat(dots[index + 1].style.top, 10) + iconCenter
          : end0;
      var end = end0 + (end1 - end0) * t;
      if (isNaN(start)) start = 0;
      if (isNaN(end)) end = start;
      fill.style.top = start + 'px';
      fill.style.height = Math.max(0, end - start) + 'px';
    }

    function setActive(index, segmentT) {
      activeIndex = index;
      steps.forEach(function (step, i) {
        step.classList.toggle('is-active', i === index);
        step.classList.toggle('is-passed', i < index);
      });
      dots.forEach(function (dot, i) {
        dot.classList.toggle('is-active', i === index);
        dot.classList.toggle('is-passed', i < index);
      });
      visuals.forEach(function (img, i) {
        img.classList.toggle('is-active', i === index);
      });
      updateProgress(index, segmentT);
    }

    function onScrollPin() {
      var rect = scrollTrack.getBoundingClientRect();
      var scrollRange = scrollTrack.offsetHeight - window.innerHeight;
      if (scrollRange <= 0) return;

      var scrolled = Math.max(0, -rect.top);
      var progress = Math.min(1, scrolled / scrollRange);
      var scaled = progress * stepCount;
      var index = Math.min(stepCount - 1, Math.floor(scaled));
      var segmentT = scaled - index;

      if (progress >= 0.999) {
        index = stepCount - 1;
        segmentT = 1;
      }

      setActive(index, segmentT);
    }

    function onScrollMobile() {
      var center = window.innerHeight * 0.42;
      var closest = 0;
      var minDist = Infinity;
      steps.forEach(function (step, i) {
        var r = step.getBoundingClientRect();
        var mid = r.top + r.height / 2;
        var dist = Math.abs(mid - center);
        if (dist < minDist) {
          minDist = dist;
          closest = i;
        }
      });
      setActive(closest, 1);
    }

    function bindScrollMode() {
      usePinScroll = window.innerWidth > 768;
      if (usePinScroll) {
        onScrollPin();
      } else {
        onScrollMobile();
      }
      syncRailGeometry();
    }

    window.addEventListener(
      'scroll',
      function () {
        if (usePinScroll) onScrollPin();
        else onScrollMobile();
      },
      { passive: true }
    );
    window.addEventListener('resize', bindScrollMode);
    window.addEventListener('load', bindScrollMode);
    setTimeout(bindScrollMode, 150);
    bindScrollMode();
    setActive(0, 0);
  }

  /* ——— Testimonials spotlight ——— */
  function initTestimonials() {
    var stage = $('#testimonialsStage');
    if (!stage) return;

    var panels = $$('.spotlight-panel', stage);
    var picks = $$('.testimonial-pick', stage);
    var prevBtn = $('#testimonialsPrev');
    var nextBtn = $('#testimonialsNext');
    var progress = $('#testimonialsProgress');
    var index = 0;
    var total = panels.length;
    var duration = 8000;
    var timer;
    var progressTimer;

    if (!total) return;

    function goTo(i, syncProgress) {
      index = (i + total) % total;
      panels.forEach(function (p, n) {
        p.classList.toggle('is-active', n === index);
      });
      picks.forEach(function (p, n) {
        var on = n === index;
        p.classList.toggle('is-active', on);
        p.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      if (syncProgress !== false) resetProgress();
    }

    function activatePick(pick) {
      var i = parseInt(pick.getAttribute('data-panel'), 10);
      if (!isNaN(i)) goTo(i, false);
    }

    function next() {
      goTo(index + 1);
    }

    function prev() {
      goTo(index - 1);
    }

    function resetProgress() {
      if (!progress) return;
      progress.style.width = '0%';
      clearInterval(progressTimer);
      var start = Date.now();
      progressTimer = setInterval(function () {
        var pct = Math.min(100, ((Date.now() - start) / duration) * 100);
        progress.style.width = pct + '%';
        if (pct >= 100) clearInterval(progressTimer);
      }, 50);
    }

    function startAutoplay() {
      clearInterval(timer);
      timer = setInterval(next, duration);
      resetProgress();
    }

    function stopAutoplay() {
      clearInterval(timer);
      clearInterval(progressTimer);
    }

    picks.forEach(function (pick) {
      pick.addEventListener('click', function () {
        activatePick(pick);
        stopAutoplay();
      });
      pick.addEventListener('mouseenter', function () {
        if (!window.matchMedia('(hover: hover)').matches) return;
        activatePick(pick);
        stopAutoplay();
      });
      pick.addEventListener('focus', function () {
        activatePick(pick);
        stopAutoplay();
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        prev();
        startAutoplay();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        next();
        startAutoplay();
      });
    }

    stage.addEventListener('mouseenter', stopAutoplay);
    stage.addEventListener('mouseleave', startAutoplay);

    goTo(0);
    startAutoplay();
  }

  /* ——— World map: cursor glow + proximity routes ——— */
  function initWorldMap() {
    var wrap = $('#worldMap');
    if (!wrap) return;

    var routes = $$('.map-route', wrap);
    var routeShadows = $$('.map-route-shadow', wrap);
    var nodes = $$('.map-node:not(.map-hub)', wrap);
    var tooltip = $('#mapTooltip');
    var cursor = $('#mapCursor');
    var hub = $('.map-hub', wrap);
    var hubCx = 714;
    var hubCy = 189;
    var hubRadius = 52;
    var nodeRadius = 78;
    var mapW = 1000;
    var mapH = 500;

    var nodeData = nodes.map(function (node) {
      var hit = $('.node-hit', node) || $('.node-dot', node);
      return {
        idx: parseInt(node.getAttribute('data-route'), 10),
        label: node.getAttribute('data-label') || '',
        cx: hit ? parseFloat(hit.getAttribute('cx')) : 0,
        cy: hit ? parseFloat(hit.getAttribute('cy')) : 0,
        el: node
      };
    });

    function animatePath(path, i) {
      var len = path.getTotalLength();
      path.style.strokeDasharray = len;
      path.style.strokeDashoffset = len;
      path.style.transition = 'stroke-dashoffset 1.2s ease ' + i * 0.12 + 's, stroke 0.4s ease, stroke-width 0.4s ease';
      path.getBoundingClientRect();
      path.style.strokeDashoffset = '0';
      path.classList.add('is-drawn');
    }

    function drawRoutes() {
      routes.forEach(animatePath);
      routeShadows.forEach(animatePath);
    }

    function setActiveRoute(index) {
      routes.forEach(function (r, i) {
        r.classList.toggle('is-active', index !== null && i === index);
      });
      routeShadows.forEach(function (r, i) {
        r.classList.toggle('is-active', index !== null && i === index);
      });
      nodes.forEach(function (n, i) {
        n.classList.toggle('is-active', index !== null && i === index);
      });
    }

    function setAllRoutesActive(on) {
      routes.forEach(function (r) {
        r.classList.toggle('is-active', on);
      });
      routeShadows.forEach(function (r) {
        r.classList.toggle('is-active', on);
      });
      nodes.forEach(function (n) {
        n.classList.remove('is-active');
      });
    }

    function showTooltipAt(label, evt) {
      if (!tooltip || !label) return;
      tooltip.textContent = label;
      tooltip.hidden = false;
      var rect = wrap.getBoundingClientRect();
      tooltip.style.left = evt.clientX - rect.left + 'px';
      tooltip.style.top = evt.clientY - rect.top + 'px';
    }

    function hideTooltip() {
      if (tooltip) tooltip.hidden = true;
    }

    function moveCursor(evt) {
      if (!cursor) return;
      var rect = wrap.getBoundingClientRect();
      var x = evt.clientX - rect.left;
      var y = evt.clientY - rect.top;
      cursor.style.left = (x / rect.width) * 100 + '%';
      cursor.style.top = (y / rect.height) * 100 + '%';
      cursor.hidden = false;
      wrap.classList.add('is-cursor-active');

      var vx = (x / rect.width) * mapW;
      var vy = (y / rect.height) * mapH;
      var hubDist = Math.hypot(vx - hubCx, vy - hubCy);

      if (hubDist < hubRadius) {
        setAllRoutesActive(true);
        showTooltipAt(hub ? hub.getAttribute('data-label') : 'India', evt);
        return;
      }

      var nearest = null;
      var best = nodeRadius;
      nodeData.forEach(function (d) {
        var dist = Math.hypot(vx - d.cx, vy - d.cy);
        if (dist < best) {
          best = dist;
          nearest = d;
        }
      });

      if (nearest) {
        setActiveRoute(nearest.idx);
        showTooltipAt(nearest.label, evt);
      } else {
        setActiveRoute(null);
        hideTooltip();
      }
    }

    function hideCursor() {
      if (cursor) cursor.hidden = true;
      wrap.classList.remove('is-cursor-active');
      setActiveRoute(null);
      setAllRoutesActive(false);
      hideTooltip();
    }

    wrap.addEventListener('mousemove', moveCursor);
    wrap.addEventListener('mouseenter', moveCursor);
    wrap.addEventListener('mouseleave', hideCursor);

    nodes.forEach(function (node) {
      var idx = parseInt(node.getAttribute('data-route'), 10);
      node.addEventListener('focus', function (e) {
        setActiveRoute(idx);
        showTooltipAt(node.getAttribute('data-label') || '', e);
      });
      node.addEventListener('blur', function () {
        setActiveRoute(null);
        hideTooltip();
      });
    });

    if (hub) {
      hub.addEventListener('focus', function (e) {
        setAllRoutesActive(true);
        showTooltipAt(hub.getAttribute('data-label') || '', e);
      });
      hub.addEventListener('blur', function () {
        setAllRoutesActive(false);
        hideTooltip();
      });
    }

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              drawRoutes();
              io.unobserve(wrap);
            }
          });
        },
        { threshold: 0.25 }
      );
      io.observe(wrap);
    } else {
      drawRoutes();
    }
  }

  /* ——— Form validation ——— */
  function getFormFieldValue(field) {
    if (field.tagName === 'SELECT') {
      var opt = field.options[field.selectedIndex];
      return opt && opt.value ? opt.text.replace(/\s+/g, ' ').trim() : '';
    }
    return (field.value || '').trim();
  }

  function buildMailtoLink(form) {
    var to = form.getAttribute('data-mailto') || 'exports@korvanto.com';
    var subjectField = form.querySelector('[name="subject"]');
    var companyField = form.querySelector('[name="company"]');
    var subject = form.getAttribute('data-mailto-subject');
    if (!subject) {
      if (subjectField && subjectField.value.trim()) {
        subject = subjectField.value.trim();
      } else if (companyField && companyField.value.trim()) {
        subject = 'Korvanto Quote Request — ' + companyField.value.trim();
      } else {
        subject = 'Korvanto Website Enquiry';
      }
    }
    var lines = [];
    $$('input, textarea, select', form).forEach(function (field) {
      if (field.type === 'submit' || field.type === 'hidden' || !field.name) return;
      var val = getFormFieldValue(field);
      if (!val) return;
      var group = field.closest('.form-group');
      var labelEl = group ? group.querySelector('label') : null;
      var label = labelEl ? labelEl.textContent.replace(/\*/g, '').trim() : field.name;
      lines.push(label + ': ' + val);
    });
    var body = lines.join('\r\n');
    return 'mailto:' + to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  }

  function initForms() {
    $$('form[data-validate]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var valid = true;
        $$('[required]', form).forEach(function (field) {
          var err = field.parentElement.querySelector('.field-error');
          if (err) err.remove();
          field.classList.remove('is-invalid');
          if (!getFormFieldValue(field)) {
            valid = false;
            field.classList.add('is-invalid');
            showError(field, 'This field is required.');
          } else if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
            valid = false;
            field.classList.add('is-invalid');
            showError(field, 'Please enter a valid email address.');
          }
        });
        var success = $('.form-success', form);
        if (valid) {
          var mailtoHref = form.getAttribute('data-mailto') ? buildMailtoLink(form) : null;
          if (success) {
            success.hidden = false;
          }
          if (mailtoHref) {
            window.location.href = mailtoHref;
          }
          form.reset();
          if (success) {
            setTimeout(function () {
              success.hidden = true;
            }, 8000);
          }
        }
      });
    });
  }

  function showError(field, msg) {
    var p = document.createElement('p');
    p.className = 'field-error';
    p.textContent = msg;
    field.parentElement.appendChild(p);
  }

  /* ——— Mineral Atlas showcase ——— */
  function initMineralAtlas() {
    var root = $('#mineralAtlas');
    if (!root) return;

    var panels = $$('.atlas-panel', root);
    var indexItems = $$('.atlas-index-item', root);
    var counter = $('#atlasCounter');
    var progress = $('#atlasProgress');
    var prevBtn = $('#atlasPrev');
    var nextBtn = $('#atlasNext');
    var stageWrap = $('.atlas-stage-wrap', root);
    var current = 0;
    var total = panels.length;
    var timer;
    var autoplayMs = 6500;

    function pad(n) {
      return n < 9 ? '0' + (n + 1) : String(n + 1);
    }

    function goTo(i, restartTimer) {
      current = (i + total) % total;
      panels.forEach(function (p, idx) {
        p.classList.toggle('is-active', idx === current);
      });
      indexItems.forEach(function (btn, idx) {
        btn.classList.toggle('is-active', idx === current);
      });
      if (counter) counter.textContent = pad(current);
      if (progress) progress.style.width = ((current + 1) / total) * 100 + '%';
      if (restartTimer !== false) startAutoplay();
    }

    function startAutoplay() {
      clearInterval(timer);
      timer = setInterval(function () {
        goTo(current + 1, false);
      }, autoplayMs);
    }

    indexItems.forEach(function (btn) {
      btn.addEventListener('click', function () {
        goTo(parseInt(btn.getAttribute('data-index'), 10));
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        goTo(current - 1);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        goTo(current + 1);
      });
    }

    root.addEventListener('mouseenter', function () {
      clearInterval(timer);
    });
    root.addEventListener('mouseleave', startAutoplay);

    if (stageWrap && window.innerWidth >= 992) {
      stageWrap.addEventListener('mousemove', function (e) {
        var r = stageWrap.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        var stage = $('.atlas-stage', stageWrap);
        if (stage) {
          stage.style.transform =
            'rotateY(' + px * 5 + 'deg) rotateX(' + -py * 4 + 'deg)';
        }
      });
      stageWrap.addEventListener('mouseleave', function () {
        var stage = $('.atlas-stage', stageWrap);
        if (stage) stage.style.transform = '';
      });
    }

    goTo(0, false);
    startAutoplay();
  }

  var FOOTER_ASSET_VERSION = '12';

  var FOOTER_MENU_HTML =
    '<div class="footer-col">' +
    '<h4>Products</h4>' +
    '<ul>' +
    '<li><a href="korvanto-bento.html">Bentonite</a></li>' +
    '<li><a href="kaolin.html">Kaolin (China Clay)</a></li>' +
    '<li><a href="ball-clay.html">Ball Clay</a></li>' +
    '<li><a href="chamotte.html">Chamotte / Calcined Clay</a></li>' +
    '<li><a href="calcined-bauxite.html">Calcined Bauxite</a></li>' +
    '<li><a href="laterite.html">Laterite</a></li>' +
    '<li><a href="coal-additive.html">Coal Additive</a></li>' +
    '<li><a href="assets/documents/korvanto-product-catalogue.pdf" download="Korvanto-Product-Catalogue.pdf">Download Product Catalogue</a></li>' +
    '</ul></div>' +
    '<div class="footer-col">' +
    '<h4>Company</h4>' +
    '<ul>' +
    '<li><a href="about.html">About Us</a></li>' +
    '<li><a href="products.html">Products</a></li>' +
    '<li><a href="quality-assurance.html">Quality &amp; Documentation</a></li>' +
    '<li><a href="certifications.html">Certifications &amp; Registrations</a></li>' +
    '<li><a href="export-packaging.html">Export &amp; Packaging</a></li>' +
    '<li><a href="contact.html">Contact Us</a></li>' +
    '<li><a href="request-quote.html">Request a Quote</a></li>' +
    '<li><a href="assets/documents/korvanto-company-profile.pdf" download="Korvanto-Company-Profile.pdf">Download Company Profile</a></li>' +
    '</ul></div>' +
    '<div class="footer-col footer-contact">' +
    '<h4>Contact</h4>' +
    '<ul class="contact-list">' +
    '<li><span class="label">Email</span><a href="mailto:[your-email@company.com]">[your-email@company.com]</a></li>' +
    '<li><span class="label">Phone</span><a href="tel:[your-phone]">[your-phone]</a></li>' +
    '<li><span class="label">Address</span><span class="contact-value">[Your business address]</span></li>' +
    '</ul></div>';

  function ensureFooterMenus() {
    var grid = $('.footer-grid');
    if (!grid || grid.querySelector('.footer-col')) return;

    var wrapper = grid.querySelector('.footer-links');
    if (wrapper) {
      wrapper.innerHTML = FOOTER_MENU_HTML;
      fixRelativeLinks(wrapper);
      return;
    }

    grid.insertAdjacentHTML('beforeend', FOOTER_MENU_HTML);
    fixRelativeLinks(grid);
  }

  /* ——— Footer year ——— */
  function initFooterYear() {
    var y = $('#footerYear');
    if (y) y.textContent = new Date().getFullYear();
  }

  /* ——— About page 3D scenes ——— */
  function bindScene3d(scene, layerSelector) {
    var layer = $(layerSelector, scene);
    if (!layer) return;
    scene.addEventListener('mousemove', function (e) {
      if (window.innerWidth < 992) return;
      var r = scene.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5;
      var y = (e.clientY - r.top) / r.height - 0.5;
      layer.style.transform =
        'rotateY(' + x * 10 + 'deg) rotateX(' + -y * 8 + 'deg) translateZ(16px)';
    });
    scene.addEventListener('mouseleave', function () {
      layer.style.transform = '';
    });
  }

  function initPremiumScenes() {
    $$('.premium-scene-3d').forEach(function (scene) {
      bindScene3d(scene, '.premium-scene-layer');
    });
    $$('.about-scene-3d').forEach(function (scene) {
      bindScene3d(scene, '.about-scene-layer');
    });
    $$('.about-vision-3d').forEach(function (scene) {
      bindScene3d(scene, '.about-vision-layer');
    });
    $$('.premium-hero-float').forEach(function (scene) {
      var badge = $('.premium-hero-badge', scene);
      if (!badge) return;
      scene.addEventListener('mousemove', function (e) {
        if (window.innerWidth < 992) return;
        var r = scene.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        badge.style.transform =
          'rotateY(' + x * 8 + 'deg) rotateX(' + -y * 6 + 'deg) translateZ(20px)';
      });
      scene.addEventListener('mouseleave', function () {
        badge.style.transform = '';
      });
    });
  }

  function initAbout() {
    initPremiumScenes();
  }

  /* ——— Floating contact hub ——— */
  function loadLiveChatBot(callback) {
    if (window.KorvantoLiveChat) {
      callback();
      return;
    }
    var script = document.createElement('script');
    script.src = BASE + 'assets/js/live-chat-bot.js';
    script.onload = callback;
    script.onerror = function () {
      console.warn('Korvanto live chat bot failed to load');
      callback();
    };
    document.head.appendChild(script);
  }

  function initFloatingContact() {
    if (document.getElementById('floatContact')) return;

    var email = 'exports@korvanto.com';
    var phoneDisplay = '+91 90540 07999';
    var phoneTel = '+919054007999';
    var whatsapp = 'https://wa.me/919054007999';

    var chatIcon =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2m0 14H5.17L4 17.17V4h16z"/></svg>';
    var waIcon =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>';
    var mailIcon =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2m0 4-8 5L4 8V6l8 5 8-5z"/></svg>';
    var phoneIcon =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1C10.07 21 3 13.93 3 5a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.46.57 3.58a1 1 0 0 1-.25 1.01l-2.2 2.2z"/></svg>';
    var callbackIcon =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 15.5c-1.25 0-2.45-.2-3.57-.57a1.02 1.02 0 0 0-1.02.24l-2.2 2.2a15.07 15.07 0 0 1-6.59-6.59l2.2-2.21a1 1 0 0 0 .24-1.02A11.36 11.36 0 0 1 8.5 4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.5c0-.55-.45-1-1-1M16 4h2v2h-2zm4 0h2v2h-2zm-8 0h2v2h-2zm4 4h2v2h-2zm4 0h2v2h-2z"/></svg>';

    var wrap = document.createElement('div');
    wrap.className = 'float-contact';
    wrap.id = 'floatContact';
    wrap.setAttribute('aria-label', 'Quick contact options');
    wrap.innerHTML =
      '<div class="float-side-tabs" aria-label="Quick actions">' +
      '<a href="' +
      BASE +
      'request-quote.html" class="float-quote-tab"><span class="float-quote-tab-inner">Get Instant Quote</span></a>' +
      '<a href="' +
      BASE +
      'assets/documents/korvanto-product-catalogue.pdf" class="float-quote-tab float-catalogue-tab" download="Korvanto-Product-Catalogue.pdf"><span class="float-quote-tab-inner">Download Catalogue</span></a>' +
      '</div>' +
      '<div class="float-live-chat" id="floatLiveChat" role="dialog" aria-label="Live chat with Korvanto" aria-hidden="true">' +
      '<div class="float-live-chat-header">' +
      '<div><div class="float-live-chat-title">Live Chat</div><div class="float-live-chat-subtitle">Riya · Export Support</div></div>' +
      '<button type="button" class="float-live-chat-close" id="floatLiveChatClose" aria-label="Close chat">' +
      '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>' +
      '</button></div>' +
      '<div class="float-live-chat-messages" id="floatLiveChatMessages"></div>' +
      '<div class="float-live-chat-quick" id="floatLiveChatQuick">' +
      '<button type="button" data-chat-quick="What products do you supply?">Products</button>' +
      '<button type="button" data-chat-quick="I need a quote">Get Quote</button>' +
      '<button type="button" data-chat-quick="What documents do you provide?">Documents</button>' +
      '<button type="button" data-chat-quick="Contact details">Contact</button>' +
      '</div>' +
      '<form class="float-live-chat-form" id="floatLiveChatForm">' +
      '<input type="text" id="floatLiveChatInput" placeholder="Type your message…" autocomplete="off" aria-label="Chat message">' +
      '<button type="submit">Send</button></form></div>' +
      '<div class="float-contact-panel" id="floatContactPanel" role="dialog" aria-label="Contact options" aria-hidden="true">' +
      '<ul class="float-contact-list" id="floatContactList">' +
      '<li><a href="' +
      whatsapp +
      '" class="float-contact-link" target="_blank" rel="noopener noreferrer">' +
      '<span class="float-contact-icon float-contact-icon--whatsapp">' +
      waIcon +
      '</span><span class="float-contact-text"><span class="float-contact-label">WhatsApp</span></span></a></li>' +
      '<li><a href="' +
      BASE +
      'contact.html" class="float-contact-link">' +
      '<span class="float-contact-icon float-contact-icon--email">' +
      mailIcon +
      '</span><span class="float-contact-text"><span class="float-contact-label">Send an inquiry</span></span></a></li>' +
      '<li><button type="button" class="float-contact-link" id="floatContactCallbackBtn">' +
      '<span class="float-contact-icon float-contact-icon--callback">' +
      callbackIcon +
      '</span><span class="float-contact-text"><span class="float-contact-label">Schedule a call</span></span></button></li>' +
      '<li><a href="tel:' +
      phoneTel +
      '" class="float-contact-link">' +
      '<span class="float-contact-icon float-contact-icon--call">' +
      phoneIcon +
      '</span><span class="float-contact-text"><span class="float-contact-label">Call Now</span><span class="float-contact-meta">' +
      phoneDisplay +
      '</span></span></a></li>' +
      '</ul></div>' +
      '<button type="button" class="float-contact-toggle" id="floatContactToggle" aria-expanded="false" aria-label="Open contact menu">' +
      '<svg class="float-contact-toggle-icon--open" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2m0 14H5.17L4 17.17V4h16z"/></svg>' +
      '<svg class="float-contact-toggle-icon--close" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>' +
      '</button>';

    var callbackModal = document.createElement('div');
    callbackModal.className = 'float-callback-modal';
    callbackModal.id = 'floatCallbackModal';
    callbackModal.setAttribute('aria-hidden', 'true');
    callbackModal.innerHTML =
      '<div class="float-callback-dialog" role="document">' +
      '<h3>Schedule a Call</h3>' +
      '<p>Share your number and we will call you back during business hours (Mon–Sat, 9:30 AM – 6:30 PM IST).</p>' +
      '<form id="floatCallbackForm">' +
      '<div class="float-callback-field"><label for="floatCallbackName">Name *</label><input type="text" id="floatCallbackName" name="name" required autocomplete="name"></div>' +
      '<div class="float-callback-field"><label for="floatCallbackPhone">Phone *</label><input type="tel" id="floatCallbackPhone" name="phone" required autocomplete="tel"></div>' +
      '<div class="float-callback-field"><label for="floatCallbackNote">Preferred time / product</label><textarea id="floatCallbackNote" name="note" rows="3"></textarea></div>' +
      '<div class="float-callback-actions">' +
      '<button type="button" class="float-callback-cancel" id="floatCallbackCancel">Cancel</button>' +
      '<button type="submit" class="float-callback-submit">Schedule Call</button>' +
      '</div></form></div>';

    document.body.appendChild(wrap);
    document.body.appendChild(callbackModal);

    var toggle = document.getElementById('floatContactToggle');
    var panel = document.getElementById('floatContactPanel');
    var liveChat = document.getElementById('floatLiveChat');
    var liveChatClose = document.getElementById('floatLiveChatClose');
    var liveChatMessages = document.getElementById('floatLiveChatMessages');
    var liveChatForm = document.getElementById('floatLiveChatForm');
    var liveChatInput = document.getElementById('floatLiveChatInput');
    var liveChatQuick = document.getElementById('floatLiveChatQuick');
    var contactList = document.getElementById('floatContactList');
    var callbackBtn = document.getElementById('floatContactCallbackBtn');
    var callbackCancel = document.getElementById('floatCallbackCancel');
    var callbackForm = document.getElementById('floatCallbackForm');

    var chatBot = null;
    var chatStarted = false;
    var chatBusy = false;

    function setMenuOpen(open) {
      toggle.classList.toggle('is-open', open);
      panel.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close contact menu' : 'Open contact menu');
      panel.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) setChatOpen(false);
    }

    function setChatOpen(open) {
      liveChat.classList.toggle('is-open', open);
      liveChat.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) {
        setMenuOpen(false);
        if (!chatStarted && chatBot) {
          chatStarted = true;
          appendChatMessage(chatBot.welcome(), 'agent');
        }
        setTimeout(function () {
          liveChatInput.focus();
        }, 280);
      }
    }

    function setCallbackOpen(open) {
      callbackModal.classList.toggle('is-open', open);
      callbackModal.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open) setMenuOpen(false);
    }

    function scrollChatToBottom() {
      liveChatMessages.scrollTop = liveChatMessages.scrollHeight;
    }

    function appendChatMessage(text, type) {
      var msg = document.createElement('div');
      msg.className = 'float-live-chat-msg float-live-chat-msg--' + type;
      msg.textContent = text;
      liveChatMessages.appendChild(msg);
      scrollChatToBottom();
      return msg;
    }

    function removeTypingIndicator(node) {
      if (node && node.parentNode) node.parentNode.removeChild(node);
    }

    function sendChatMessage(text) {
      var trimmed = (text || '').trim();
      if (!trimmed || chatBusy) return;
      appendChatMessage(trimmed, 'user');
      liveChatInput.value = '';

      if (!chatBot) {
        appendChatMessage('Chat is loading — please email ' + email + ' or call ' + phoneDisplay + '.', 'agent');
        return;
      }

      chatBusy = true;
      var typing = appendChatMessage(chatBot.typingLabel(), 'typing');

      setTimeout(function () {
        removeTypingIndicator(typing);
        appendChatMessage(chatBot.reply(trimmed), 'agent');
        chatBusy = false;
      }, 600 + Math.random() * 500);
    }

    function appendLiveChatOption() {
      if (!contactList || document.getElementById('floatContactChatBtn')) return;
      var li = document.createElement('li');
      li.innerHTML =
        '<button type="button" class="float-contact-link" id="floatContactChatBtn">' +
        '<span class="float-contact-icon float-contact-icon--chat">' +
        chatIcon +
        '</span><span class="float-contact-text"><span class="float-contact-label">Live Chat</span></span></button>';
      contactList.appendChild(li);
      li.querySelector('#floatContactChatBtn').addEventListener('click', function () {
        setChatOpen(true);
      });
    }

    loadLiveChatBot(function () {
      if (window.KorvantoLiveChat) {
        chatBot = window.KorvantoLiveChat();
        appendLiveChatOption();
      }
    });

    toggle.addEventListener('click', function () {
      setMenuOpen(!panel.classList.contains('is-open'));
    });

    liveChatClose.addEventListener('click', function () {
      setChatOpen(false);
    });

    liveChatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      sendChatMessage(liveChatInput.value);
    });

    liveChatQuick.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-chat-quick]');
      if (!btn) return;
      sendChatMessage(btn.getAttribute('data-chat-quick'));
    });

    callbackBtn.addEventListener('click', function () {
      setCallbackOpen(true);
    });

    callbackCancel.addEventListener('click', function () {
      setCallbackOpen(false);
    });

    callbackModal.addEventListener('click', function (e) {
      if (e.target === callbackModal) setCallbackOpen(false);
    });

    callbackForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = document.getElementById('floatCallbackName').value.trim();
      var phone = document.getElementById('floatCallbackPhone').value.trim();
      var note = document.getElementById('floatCallbackNote').value.trim();
      var body =
        'Schedule a call request from Korvanto website\r\n\r\n' +
        'Name: ' +
        name +
        '\r\nPhone: ' +
        phone;
      if (note) body += '\r\nNote: ' + note;
      window.location.href =
        'mailto:' + email + '?subject=' + encodeURIComponent('Schedule a Call — ' + name) + '&body=' + encodeURIComponent(body);
      setCallbackOpen(false);
      callbackForm.reset();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (callbackModal.classList.contains('is-open')) setCallbackOpen(false);
      else if (liveChat.classList.contains('is-open')) setChatOpen(false);
      else if (panel.classList.contains('is-open')) setMenuOpen(false);
    });
  }

  /* ——— Init ——— */
  document.addEventListener('DOMContentLoaded', function () {
    loadPartial('header-placeholder', 'components/header.html?v=2', function () {
      var stale = document.querySelector('#headerProductSearch #headerSearchOverlay');
      if (stale) stale.remove();
      initHeader();
    });
    bootProductSearch();
    loadPartial(
      'footer-placeholder',
      'components/footer.html?v=' + FOOTER_ASSET_VERSION,
      function () {
        ensureFooterMenus();
        initFooterYear();
        initFloatingContact();
      }
    );

    initHeroSlider();
    initPortfolioHeroSlider();
    initReveal();
    initParallax();
    initHeroCard();
    initCardTilt();
    initMineralAtlas();
    initJourney();
    initTestimonials();
    initWorldMap();
    initForms();
    initAbout();
    if (!document.body.classList.contains('about-page')) {
      initPremiumScenes();
    }
  });
})();
