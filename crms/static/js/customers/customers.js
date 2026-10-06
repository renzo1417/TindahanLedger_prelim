/**
 * TidaHan Ledger - Customers & Utang Client-Side Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Auto-focus amount input when modals open
  window.addEventListener('click', (e) => {
    if (e.target.matches('[onclick*="log-utang-modal"]')) {
      setTimeout(() => {
        const input = document.getElementById('id_utang_amount');
        if (input) input.focus();
      }, 100);
    } else if (e.target.matches('[onclick*="log-bayad-modal"]')) {
      setTimeout(() => {
        const input = document.getElementById('id_bayad_amount');
        if (input) input.focus();
      }, 100);
    }
  });
});
