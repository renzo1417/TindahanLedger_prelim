"""
User Settings screen views for TindaHan Ledger.
Phase 1: Vertical Slice implementation rendering the Store & User Settings configuration.
"""

from django.shortcuts import render


def user_settings_view(request):
    """Renders the Store & User Settings screen."""
    settings_data = {
        'store_name': "Aling Nena Tindahan",
        'owner_name': "Elena Santos",
        'phone_number': "+63 917 555 0192",
        'gcash_number': "0917-555-0192",
        'address': "Block 4 Lot 12, Barangay Pinagbuhatan, Pasig City",
        'ledger_volume': "Vol. V • Ledger No. 892",
        # Ledger & Credit Rules
        'default_credit_limit': 3000.00,
        'overdue_grace_days': 7,
        'reminder_threshold_days': 3,
        'block_over_limit': True,
        # Inventory & Spoilage Rules
        'expiry_window_days': 7,
        'low_stock_threshold': 10,
        'auto_fifo_sort': True,
        # Notifications & Audio
        'sound_effects_enabled': True,
        'auto_sms_reminders': True,
        'daily_summary_report': True,
        # Security & Backup
        'terminal_pin': "••••",
        'auto_lock_minutes': 15,
        'last_backup_date': "Today at 02:30 PM",
        'local_cache_size': "2.4 MB (Encrypted)",
    }

    # If user is authenticated, personalize owner name
    if request.user.is_authenticated:
        if request.user.first_name or request.user.last_name:
            settings_data['owner_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        elif request.user.username:
            settings_data['owner_name'] = request.user.username

    context = {
        'active_nav': 'settings',
        'settings': settings_data,
    }
    return render(request, 'user_settings/user_settings.html', context)
