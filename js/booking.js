/* =========================================================
   Ready2Glow – WhatsApp booking system (vanilla JS)
   The service catalogue is read from the HTML cards
   (data-id / data-name / data-price / data-duration), so
   the HTML stays the single source of truth for prices.
   ========================================================= */
(function () {
  'use strict';

  var WHATSAPP_NUMBER = '918820369048';
  var STORAGE_KEY = 'r2g-selected-v1';
  var SLOT_START = 8 * 60;   // 8:00 AM
  var SLOT_END = 20 * 60;    // 8:00 PM
  var SLOT_STEP = 30;        // minutes

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------- Catalogue from DOM ---------- */
  var catalog = {};
  $$('.svc[data-id]').forEach(function (el) {
    var id = el.dataset.id;
    if (catalog[id]) return;
    catalog[id] = {
      id: id,
      name: el.dataset.name,
      price: parseInt(el.dataset.price, 10) || 0,
      duration: el.dataset.duration || ''
    };
  });

  /* ---------- State ---------- */
  var selected = loadSelection();

  function loadSelection() {
    try {
      var raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      return Array.isArray(raw) ? raw.filter(function (id, i) { return catalog[id] && raw.indexOf(id) === i; }) : [];
    } catch (e) { return []; }
  }
  function saveSelection() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(selected)); } catch (e) { /* storage unavailable */ }
  }
  function isSelected(id) { return selected.indexOf(id) !== -1; }
  function addService(id) {
    if (!catalog[id] || isSelected(id)) return;
    selected.push(id); commit();
  }
  function removeService(id) {
    var i = selected.indexOf(id);
    if (i === -1) return;
    selected.splice(i, 1); commit();
  }
  function toggleService(id) {
    if (isSelected(id)) { removeService(id); toast(catalog[id].name + ' removed'); }
    else { addService(id); toast(catalog[id].name + ' added to your booking'); }
  }
  function clearServices() { selected = []; commit(); }
  function selectedItems() { return selected.map(function (id) { return catalog[id]; }); }
  function total() { return selectedItems().reduce(function (sum, s) { return sum + s.price; }, 0); }
  function commit() { saveSelection(); render(); }

  /* ---------- Formatting ---------- */
  function rupee(n) { return '₹' + Number(n).toLocaleString('en-IN'); }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function formatTime(mins) {
    var h = Math.floor(mins / 60), m = mins % 60;
    var suffix = h >= 12 ? 'PM' : 'AM';
    var h12 = h % 12 === 0 ? 12 : h % 12;
    return h12 + ':' + (m < 10 ? '0' : '') + m + ' ' + suffix;
  }
  function parseLocalDate(value) {           // "2026-11-15" -> local Date (avoids UTC shift)
    var p = value.split('-');
    return new Date(+p[0], +p[1] - 1, +p[2]);
  }
  function formatDate(value) {
    return parseLocalDate(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  }
  function todayISO() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  /* ---------- Rendering ---------- */
  function render() {
    var items = selectedItems();
    var count = items.length;

    // Card states (a service can appear in several sections)
    $$('[data-id]').forEach(function (el) {
      var on = isSelected(el.dataset.id);
      el.classList.toggle('is-selected', on);
      var btn = $('.js-toggle', el);
      if (btn) {
        btn.textContent = on ? '✓ Added' : 'Add';
        btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        btn.setAttribute('aria-label', (on ? 'Remove ' : 'Add ') + el.dataset.name + (on ? ' from booking' : ' to booking'));
      }
    });

    // Counts and totals
    $$('.js-count').forEach(function (el) {
      el.textContent = count;
      if (el.closest('.header-count, .wa-fab-count') || el.classList.contains('header-count') || el.classList.contains('wa-fab-count')) {
        el.hidden = count === 0;
      }
    });
    $$('.js-count-label').forEach(function (el) { el.textContent = count === 1 ? 'service' : 'services'; });
    $$('.js-total').forEach(function (el) { el.textContent = rupee(total()); });

    // Summary lists
    var listHtml = count
      ? '<ol class="summary-list">' + items.map(function (s) {
          return '<li class="summary-item">' +
            '<span class="summary-name">' + escapeHtml(s.name) + '</span>' +
            '<span class="summary-price">' + rupee(s.price) + '</span>' +
            '<button type="button" class="summary-remove js-summary-remove" data-remove-id="' + escapeHtml(s.id) +
            '" aria-label="Remove ' + escapeHtml(s.name) + '">×</button></li>';
        }).join('') + '</ol>'
      : '<p class="summary-empty">No services selected yet. <a href="#services" class="js-add-more">Browse services</a> and tap <strong>Add</strong>.</p>';
    $$('.js-summary-list').forEach(function (el) { el.innerHTML = listHtml; });

    // Floating summary visibility
    var fs = $('#floating-summary');
    fs.hidden = count === 0;
    document.body.classList.toggle('has-selection', count > 0);
    if (count === 0) setFloatingOpen(false);
  }

  /* ---------- Floating summary (mobile expand) ---------- */
  function setFloatingOpen(open) {
    var fs = $('#floating-summary');
    fs.classList.toggle('is-open', open);
    $('.js-fs-toggle').setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.classList.toggle('fs-expanded', open);
  }

  /* ---------- Toast ---------- */
  var toastTimer;
  function toast(msg) {
    var t = $('#toast');
    t.textContent = msg;
    t.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('is-visible'); }, 2600);
  }

  /* ---------- Modal ---------- */
  var modal = $('#booking-modal');
  var form = $('#booking-form');

  function openBooking(preselectId) {
    if (preselectId) addService(preselectId);
    if (!selected.length) {
      toast('Please select at least one service to book.');
      var target = $('#services');
      if (target) target.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    showView('form');
    setFloatingOpen(false);
    if (typeof modal.showModal === 'function') { if (!modal.open) modal.showModal(); }
    else modal.setAttribute('open', '');
    document.body.classList.add('modal-open');
    setTimeout(function () {
      var first = $('#bf-name');
      if (first && !first.value) first.focus();
    }, 50);
  }
  function closeBooking() {
    if (modal.open) { if (typeof modal.close === 'function') modal.close(); else modal.removeAttribute('open'); }
    document.body.classList.remove('modal-open');
  }
  function showView(which) {
    $('.js-view-form', modal).hidden = which !== 'form';
    $('.js-view-done', modal).hidden = which !== 'done';
    $('#modal-title').textContent = which === 'done' ? 'Booking Request Ready' : 'Booking Details';
  }
  modal.addEventListener('close', function () { document.body.classList.remove('modal-open'); });
  modal.addEventListener('click', function (e) { if (e.target === modal) closeBooking(); }); // backdrop click

  /* ---------- Form setup ---------- */
  (function initForm() {
    var timeSel = $('#bf-time');
    for (var m = SLOT_START; m <= SLOT_END; m += SLOT_STEP) {
      var opt = document.createElement('option');
      opt.value = String(m);
      opt.textContent = formatTime(m);
      timeSel.appendChild(opt);
    }
    var dateInput = $('#bf-date');
    dateInput.min = todayISO();
    var max = new Date(); max.setDate(max.getDate() + 90);
    dateInput.max = max.getFullYear() + '-' + String(max.getMonth() + 1).padStart(2, '0') + '-' + String(max.getDate()).padStart(2, '0');

    // Keep phone input numeric
    $('#bf-phone').addEventListener('input', function (e) { e.target.value = e.target.value.replace(/[^\d+\s]/g, ''); });
    // Clear field error on edit
    $$('input, select, textarea', form).forEach(function (el) {
      el.addEventListener('input', function () { setError(el.name, ''); });
      el.addEventListener('change', function () { setError(el.name, ''); });
    });
  })();

  function setError(name, msg) {
    var input = form.elements[name];
    if (!input) return;
    var field = input.closest('.field');
    var err = $('#bf-' + name + '-err');
    if (err) err.textContent = msg;
    if (field) field.classList.toggle('has-error', !!msg);
    input.setAttribute('aria-invalid', msg ? 'true' : 'false');
  }

  function normalisePhone(raw) {
    var digits = raw.replace(/\D/g, '');
    if (digits.length === 12 && digits.indexOf('91') === 0) digits = digits.slice(2);
    if (digits.length === 11 && digits.charAt(0) === '0') digits = digits.slice(1);
    return digits;
  }

  function validate() {
    var data = {
      name: form.elements.name.value.trim().replace(/\s+/g, ' '),
      phone: normalisePhone(form.elements.phone.value),
      date: form.elements.date.value,
      time: form.elements.time.value,
      area: form.elements.area.value.trim().replace(/\s+/g, ' '),
      notes: form.elements.notes.value.trim()
    };
    var errors = {};
    if (data.name.length < 2) errors.name = 'Please enter your name.';
    if (!/^[6-9]\d{9}$/.test(data.phone)) errors.phone = 'Please enter a valid 10-digit Indian mobile number.';
    if (!data.date) errors.date = 'Please choose a date.';
    else if (data.date < todayISO()) errors.date = 'Please choose today or a future date.';
    if (!data.time) errors.time = 'Please choose a time.';
    else if (data.date === todayISO()) {
      var now = new Date();
      if (+data.time <= now.getHours() * 60 + now.getMinutes()) errors.time = 'This time has passed – please pick a later slot.';
    }
    if (data.area.length < 2) errors.area = 'Please enter your area or locality.';

    ['name', 'phone', 'date', 'time', 'area'].forEach(function (k) { setError(k, errors[k] || ''); });
    var firstBad = Object.keys(errors)[0];
    if (firstBad) form.elements[firstBad].focus();
    return firstBad ? null : data;
  }

  /* ---------- WhatsApp message ---------- */
  function buildMessage(d) {
    var items = selectedItems();
    var location = /indore/i.test(d.area) ? d.area : d.area + ', Indore';
    var lines = [
      'Hello Ready2Glow! 💗',
      '',
      'I would like to book a home beauty appointment.',
      '',
      'My Details:',
      'Name: ' + d.name,
      'Phone: ' + d.phone,
      'Location: ' + location,
      '',
      'Selected Services:'
    ];
    items.forEach(function (s, i) { lines.push((i + 1) + '. ' + s.name + ' – ' + rupee(s.price)); });
    lines.push(
      '',
      'Estimated Total: ' + rupee(total()),
      '',
      'Preferred Date: ' + formatDate(d.date),
      'Preferred Time: ' + formatTime(+d.time)
    );
    if (d.notes) lines.push('', 'Additional Instructions: ' + d.notes);
    lines.push('', 'Please confirm availability for my appointment.', '', 'Thank you!');
    return lines.join('\n');
  }
  function whatsappUrl(message) {
    return 'https://wa.me/' + WHATSAPP_NUMBER + '?text=' + encodeURIComponent(message);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var formError = $('.js-form-error', form);
    formError.textContent = '';
    if (!selected.length) { formError.textContent = 'Please select at least one service before booking.'; return; }
    var data = validate();
    if (!data) return;

    var url = whatsappUrl(buildMessage(data));
    $('.js-wa-fallback').href = url;
    var win = window.open(url, '_blank');   // opened synchronously on submit, so not popup-blocked
    if (win) { try { win.opener = null; } catch (err) { /* ignore */ } }
    showView('done');                       // never claims confirmation – the customer still has to press Send
    if (!win) window.location.href = url;   // popup blocked: open WhatsApp in this tab
  });

  /* ---------- Global click handling ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    var card = t.closest('.svc[data-id]');

    if (t.closest('.js-toggle') && card) { toggleService(card.dataset.id); return; }
    if (t.closest('.js-remove') && card) { removeService(card.dataset.id); toast(catalog[card.dataset.id].name + ' removed'); return; }
    if (t.closest('.js-book') && card) { openBooking(card.dataset.id); return; }

    var bookId = t.closest('.js-book-id');
    if (bookId) { openBooking(bookId.dataset.bookId); return; }

    var rm = t.closest('.js-summary-remove');
    if (rm) { removeService(rm.dataset.removeId); return; }

    if (t.closest('.js-open-booking')) { openBooking(); return; }
    if (t.closest('.js-close-modal')) { closeBooking(); return; }

    if (t.closest('.js-add-more')) {
      if (modal.open) closeBooking();
      return; // default anchor scroll continues
    }
    if (t.closest('.js-edit-booking')) { showView('form'); return; }
    if (t.closest('.js-new-booking')) {
      clearServices(); form.reset(); showView('form'); closeBooking();
      var s = $('#services'); if (s) s.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    if (t.closest('.js-fs-toggle')) {
      if (window.matchMedia('(max-width: 860px)').matches) setFloatingOpen(!$('#floating-summary').classList.contains('is-open'));
      return;
    }

    // Category filter chips / tiles
    var chip = t.closest('[data-filter]');
    if (chip) { applyFilter(chip.dataset.filter); return; }
    var tile = t.closest('[data-filter-link]');
    if (tile) { applyFilter(tile.dataset.filterLink); return; }

    if (t.closest('.js-view-all')) { toggleViewAll(); return; }

    if (t.closest('.js-nav-toggle')) { toggleNav(); return; }
    if (t.closest('.main-nav a')) toggleNav(false);
  });

  /* ---------- Services: filter + view all ---------- */
  var grid = $('.js-services-grid');
  var viewAllBtn = $('.js-view-all');
  var showingAll = false;

  function applyFilter(cat) {
    $$('.chip[data-filter]').forEach(function (c) {
      var on = c.dataset.filter === cat;
      c.classList.toggle('is-active', on);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    $$('.svc', grid).forEach(function (el) {
      el.classList.toggle('is-filtered-out', cat !== 'all' && el.dataset.cat !== cat);
      // a specific category always shows every item in it
      if (cat !== 'all') el.classList.add('is-shown');
      else el.classList.toggle('is-shown', showingAll);
    });
    viewAllBtn.parentElement.hidden = cat !== 'all' || !$$('.svc.is-extra', grid).length;
  }
  function toggleViewAll() {
    showingAll = !showingAll;
    $$('.svc.is-extra', grid).forEach(function (el) { el.classList.toggle('is-shown', showingAll); });
    viewAllBtn.textContent = showingAll ? 'Show Less' : 'View All';
    viewAllBtn.setAttribute('aria-expanded', showingAll ? 'true' : 'false');
    if (!showingAll) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------- Mobile nav ---------- */
  function toggleNav(force) {
    var nav = $('#main-nav'), btn = $('.js-nav-toggle');
    var open = typeof force === 'boolean' ? force : !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  /* ---------- Hero slider ---------- */
  (function initHero() {
    var track = $('.js-hero-track');
    if (!track) return;
    var slides = $$('.hero-slide', track);
    var dotsWrap = $('.js-hero-dots');
    var current = 0, timer;
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      b.addEventListener('click', function () { go(i); restart(); });
      dotsWrap.appendChild(b);
    });
    var dots = $$('button', dotsWrap);
    function mark(i) {
      current = i;
      dots.forEach(function (d, j) { d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    }
    function go(i) {
      i = (i + slides.length) % slides.length;
      track.scrollTo({ left: i * track.clientWidth, behavior: 'smooth' });
      mark(i);
    }
    track.addEventListener('scroll', function () {
      var i = Math.round(track.scrollLeft / track.clientWidth);
      if (i !== current) mark(i);
    }, { passive: true });
    $('.js-hero-prev').addEventListener('click', function () { go(current - 1); restart(); });
    $('.js-hero-next').addEventListener('click', function () { go(current + 1); restart(); });
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function restart() {
      clearInterval(timer);
      if (!reduce) timer = setInterval(function () { go(current + 1); }, 5000);
    }
    var hero = $('.hero');
    hero.addEventListener('mouseenter', function () { clearInterval(timer); });
    hero.addEventListener('mouseleave', restart);
    hero.addEventListener('focusin', function () { clearInterval(timer); });
    mark(0); restart();
  })();

  /* ---------- Category carousel arrows ---------- */
  (function initCats() {
    var track = $('.js-cat-track');
    if (!track) return;
    function step(dir) { track.scrollBy({ left: dir * (track.clientWidth * 0.75), behavior: 'smooth' }); }
    $('.js-cat-prev').addEventListener('click', function () { step(-1); });
    $('.js-cat-next').addEventListener('click', function () { step(1); });
  })();

  /* ---------- Init ---------- */
  $$('.js-year').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  render();
  applyFilter('all');
})();
