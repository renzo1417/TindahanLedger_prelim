/**
 * TindaHan Ledger - Login Feature Client Scripts
 * Vertical Slice: static/js/login/login.js
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  if (form) {
    form.addEventListener('submit', () => {
      const btn = document.getElementById('login-submit-btn');
      if (btn) {
        btn.disabled = true;
        const label = btn.querySelector('.btn-label');
        if (label) label.textContent = 'Authenticating Store...';
      }
    });
  }
});
