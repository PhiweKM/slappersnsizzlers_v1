/**
 * Slappers n Sizzlers — Frontend JS
 * Module 0: Mobile menu toggle
 */

document.addEventListener('DOMContentLoaded', function () {

  // ─── Mobile menu toggle ──────────────────────────────────────
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const iconMenu = document.querySelector('.icon-menu');
  const iconClose = document.querySelector('.icon-close');

  if (menuToggle && mobileDrawer) {
    menuToggle.addEventListener('click', function () {
      const isOpen = mobileDrawer.classList.toggle('open');
      menuToggle.setAttribute('aria-expanded', isOpen);
      mobileDrawer.setAttribute('aria-hidden', !isOpen);

      // Swap hamburger / close icon
      if (iconMenu && iconClose) {
        iconMenu.style.display  = isOpen ? 'none'  : 'block';
        iconClose.style.display = isOpen ? 'block' : 'none';
      }
    });
  }

  // ─── Auto-dismiss messages after 4s ─────────────────────────
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.4s';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });

  // ─── Pickup slot selector (checkout page) ───────────────────
  const pickupSlots = document.querySelectorAll('.pickup-slot');
  pickupSlots.forEach(function (slot) {
    slot.addEventListener('click', function () {
      pickupSlots.forEach(function (s) { s.classList.remove('selected'); });
      slot.classList.add('selected');

      // Update hidden input if present
      const hiddenInput = document.getElementById('pickup-time-input');
      if (hiddenInput) { hiddenInput.value = slot.dataset.time; }

      // Enable confirm button
      const confirmBtn = document.querySelector('.btn-confirm');
      if (confirmBtn) { confirmBtn.classList.add('ready'); }
    });
  });

  // ─── Payment method selector (checkout page) ────────────────
  const paymentOptions = document.querySelectorAll('.payment-option');
  paymentOptions.forEach(function (option) {
    option.addEventListener('click', function () {
      paymentOptions.forEach(function (o) { o.classList.remove('selected'); });
      option.classList.add('selected');

      const hiddenInput = document.getElementById('payment-method-input');
      if (hiddenInput) { hiddenInput.value = option.dataset.method; }
    });
  });

  // ─── Size selector (food detail page) ───────────────────────
  const sizeOptions = document.querySelectorAll('.size-option');
  sizeOptions.forEach(function (option) {
    option.addEventListener('click', function () {
      sizeOptions.forEach(function (o) { o.classList.remove('selected'); });
      option.classList.add('selected');
    });
  });

});
