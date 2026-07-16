/**
 * Pop-up documentation request forms — Quality & Documentation page
 * Uses shared product → grade filter from product-grades.js
 */
(function () {
  var triggers = document.querySelectorAll('[data-doc-modal]');
  if (!triggers.length) return;

  var modals = document.querySelectorAll('.doc-request-modal');
  var activeModal = null;
  var lastFocus = null;
  var productTpl = document.getElementById('docProductOptionsTpl');
  var GradeFilter = window.KorvantoGradeFilter;

  if (productTpl) {
    document.querySelectorAll('.doc-product-select').forEach(function (select) {
      select.appendChild(productTpl.content.cloneNode(true));
    });
  }

  function openModal(id) {
    var modal = document.getElementById(id);
    if (!modal) return;
    lastFocus = document.activeElement;
    activeModal = modal;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('doc-request-open');
    var firstField = modal.querySelector('input, select, textarea');
    if (firstField) {
      setTimeout(function () {
        firstField.focus();
      }, 50);
    }
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    if (activeModal === modal) activeModal = null;
    if (!document.querySelector('.doc-request-modal.is-open')) {
      document.body.classList.remove('doc-request-open');
    }
    if (lastFocus && typeof lastFocus.focus === 'function') {
      lastFocus.focus();
    }
  }

  function closeActiveModal() {
    if (activeModal) closeModal(activeModal);
  }

  triggers.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = btn.getAttribute('data-doc-modal');
      if (target) openModal(target);
    });
  });

  modals.forEach(function (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal(modal);
    });

    var closeBtn = modal.querySelector('.doc-request-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        closeModal(modal);
      });
    }

    var form = modal.querySelector('form[data-validate]');
    if (form) {
      if (GradeFilter) GradeFilter.wireForm(form);
      form.addEventListener('submit', function () {
        setTimeout(function () {
          var success = form.querySelector('.form-success');
          if (success && !success.hidden) {
            setTimeout(function () {
              closeModal(modal);
              success.hidden = true;
            }, 2500);
          }
        }, 0);
      });
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeActiveModal();
  });
})();
