/**
 * TindaHan Ledger - Register Feature Client Scripts
 * Vertical Slice: static/js/register/register.js
 */

document.addEventListener('DOMContentLoaded', () => {
  const regForm = document.getElementById('register-form');
  if (regForm) {
    regForm.addEventListener('submit', () => {
      const btn = document.getElementById('register-submit-btn');
      if (btn) {
        btn.disabled = true;
        const label = btn.querySelector('.btn-label');
        if (label) label.textContent = 'Registering Store...';
      }
    });
  }
});
