"""
Global context processors and data providers for TindaHan Ledger.
Provides store profile, KPIs, and search datasets to all templates and layouts.
"""

from copy import deepcopy

# Default Store Profile
STORE_PROFILE = {
    'store_name': "Aling Nena Tindahan",
    'owner_name': "Elena Santos",
    'address': "Block 4 Lot 12, Barangay Pinagbuhatan, Pasig City",
    'phone_number': "+63 917 555 0192",
    'gcash_number': "0917-555-0192",
    'email': "alingnena.tindahan@gmail.com",
    'business_category': "Sari-Sari & Retail Convenience",
    'operating_hours': "6:00 AM – 10:00 PM Daily",
    'ledger_volume': "Vol. V • Ledger No. 892",
    'current_date_display': "Today, August 2026",
    'current_time_display': "04:30 PM",
    'avatar_initial': "A",
    'is_device_synced': True,
    'sync_status': "Local Synchronized",
    'store_role': "Master Merchant / Owner",
    'member_since': "March 2024",
    'total_customers': 48,
    'active_ledgers': 24,
    'store_rating': "4.9 / 5.0",
}

# Global KPIs
STORE_KPIS = {
    'today_sales_total': 3847.50,
    'today_sales_count': 23,
    'total_utang_balance': 12450.00,
    'overdue_accounts_count': 4,
    'active_utang_accounts_count': 18,
    'settled_accounts_count': 32,
    'low_stock_items_count': 7,
    'expiry_alert_batches_count': 4,
    'expired_batches_count': 1,
    'expired_capital_loss': 116.00,
    'expiring_in_7_days_capital': 345.00,
    'healthy_batches_count': 28,
}

# Search dataset for customer records
SEARCH_CUSTOMERS = [
    {
        'id': 1,
        'name': "Maria Santos",
        'nickname': "Aling Maria",
        'avatar_letter': "M",
        'running_balance': 2350.00,
        'credit_limit': 5000,
        'days_overdue': 12,
        'due_date': "Aug 25, 2026",
        'phone': "0918-123-4567",
    },
    {
        'id': 2,
        'name': "Pedro Reyes",
        'nickname': "Mang Pedro",
        'avatar_letter': "P",
        'running_balance': 1800.00,
        'credit_limit': 3000,
        'days_overdue': 8,
        'due_date': "Aug 29, 2026",
        'phone': "0919-234-5678",
    },
    {
        'id': 3,
        'name': "Rosa dela Cruz",
        'nickname': "Ate Rosa",
        'avatar_letter': "R",
        'running_balance': 950.00,
        'credit_limit': 2000,
        'days_overdue': 5,
        'due_date': "Sep 01, 2026",
        'phone': "0920-345-6789",
    },
    {
        'id': 4,
        'name': "Juan Bautista",
        'nickname': "Kuya Juan",
        'avatar_letter': "J",
        'running_balance': 1420.00,
        'credit_limit': 2500,
        'days_overdue': 2,
        'due_date': "Sep 04, 2026",
        'phone': "0921-456-7890",
    },
]


def global_store_context(request):
    """Injects store profile, KPI summaries, and search items for base layout and components."""
    profile = deepcopy(STORE_PROFILE)
    # If user is authenticated, personalize owner name
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.first_name or request.user.last_name:
            profile['owner_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        elif request.user.username:
            profile['owner_name'] = request.user.username

    return {
        'global_store_profile': profile,
        'global_store_kpis': deepcopy(STORE_KPIS),
        'global_search_customers': SEARCH_CUSTOMERS,
    }
