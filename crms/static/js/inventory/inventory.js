/**
 * TidaHan Ledger - Inventory Client-Side Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Focus helper on modal triggers
  window.addEventListener('click', (e) => {
    if (e.target.matches('[onclick*="add-product-modal"]')) {
      setTimeout(() => {
        const input = document.getElementById('id_prod_name');
        if (input) input.focus();
      }, 100);
    }
  });
});
