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
            'assets/images/logo/Korvanto%20logo.png" alt="Korvanto LLP" class="logo-img" width="280" height="92"></span></a><p style="color:#fff;font-size:0.85rem;">Run via local server (e.g. npx serve) to load full navigation.</p></div></header>';
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
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var parent = btn.closest('.has-dropdown');
        var open = parent.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open);
      });
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
  }

  function setActiveNav() {
    var page = window.location.pathname.split('/').pop() || 'index.html';
    var map = {
      'index.html': 'home',
      'about.html': 'about',
      'quality-assurance.html': 'quality',
      'export-packaging.html': 'export',
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
      [
        'bentonite.html',
        'kaolin.html',
        'ball-clay.html',
        'chamotte.html',
        'calcined-bauxite.html',
        'laterite.html',
        'coal-additive.html',
        'products.html'
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

    window.addEventListener('mousemove', onMove, { passive: true });

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

  /* ——— Journey: pinned 4-step scroll, then next section ——— */
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
    var countEl = $('#mapRouteCount');
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

    if (countEl) countEl.textContent = String(nodes.length);

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
  function initForms() {
    $$('form[data-validate]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var valid = true;
        $$('[required]', form).forEach(function (field) {
          var err = field.parentElement.querySelector('.field-error');
          if (err) err.remove();
          field.classList.remove('is-invalid');
          if (!field.value.trim()) {
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
          if (success) {
            success.hidden = false;
            form.reset();
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

  /* ——— Footer year ——— */
  function initFooterYear() {
    var y = $('#footerYear');
    if (y) y.textContent = new Date().getFullYear();
  }

  /* ——— About page 3D scenes ——— */
  function initAbout() {
    if (!document.body.classList.contains('about-page')) return;

    function bindAboutScene3d(scene, layerSelector) {
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

    $$('.about-scene-3d').forEach(function (scene) {
      bindAboutScene3d(scene, '.about-scene-layer');
    });

    $$('.about-vision-3d').forEach(function (scene) {
      bindAboutScene3d(scene, '.about-vision-layer');
    });

  }

  /* ——— Init ——— */
  document.addEventListener('DOMContentLoaded', function () {
    loadPartial('header-placeholder', 'components/header.html', function () {
      initHeader();
    });
    loadPartial('footer-placeholder', 'components/footer.html', function () {
      initFooterYear();
    });

    initHeroSlider();
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
  });
})();
