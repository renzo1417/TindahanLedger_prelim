/**
 * TindaHan Ledger - Store & Owner Profile Client Scripts
 * Vertical Slice: static/js/profile/profile.js
 */

document.addEventListener('DOMContentLoaded', () => {
  // Setup copy helpers if needed
  window.copyToClipboard = function(text, successMsg) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        showToast(successMsg || 'Copied to clipboard!', 'copy');
      });
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      showToast(successMsg || 'Copied to clipboard!', 'copy');
    }
  };
});
