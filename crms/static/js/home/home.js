/**
 * TindaHan Ledger - Home & Daily Store Overview Client Scripts
 * Vertical Slice: static/js/home/home.js
 */

document.addEventListener('DOMContentLoaded', () => {
  // Micro-interaction: Log sale shortcut
  const logSaleBtn = document.querySelector('.section-header .btn-primary');
  if (logSaleBtn) {
    logSaleBtn.addEventListener('click', () => {
      // Future POS entry trigger
    });
  }

  // Interactive KPI card feedback
  document.querySelectorAll('.kpi-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-2px)';
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
});
