/**
 * TindaHan Ledger - User Settings Client Scripts
 * Vertical Slice: static/js/user_settings/user_settings.js
 */

function saveSettings() {
  showToast('Store & ledger settings saved successfully!', 'check');
}

function resetSettingsDefaults() {
  if (confirm('Reset all ledger and alert settings to factory defaults?')) {
    showToast('Settings restored to standard ledger defaults.', 'info');
  }
}

function exportJsonBackup() {
  showToast('Packaging encrypted store ledger JSON backup...', 'info');
  setTimeout(() => {
    // Generate simulated download
    const dummyData = {
      store: "Aling Nena Tindahan",
      timestamp: new Date().toISOString(),
      version: "2.0-Vertical-Slice",
      records: { customers: 48, transactions: 154, batches: 28 }
    };
    const blob = new Blob([JSON.stringify(dummyData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tindahan_backup_${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Ledger JSON backup downloaded successfully.', 'check');
  }, 600);
}

function exportCsvData() {
  showToast('Compiling customer ledger CSV...', 'info');
  setTimeout(() => {
    const csvContent = "data:text/csv;charset=utf-8,ID,Name,Nickname,RunningBalance,CreditLimit,DaysOverdue\n1,Maria Santos,Aling Maria,2350.00,5000,12\n2,Pedro Reyes,Mang Pedro,1800.00,3000,8\n3,Rosa dela Cruz,Ate Rosa,950.00,2000,5\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `customer_utang_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('Customer CSV exported.', 'check');
  }, 600);
}
