"""
Profile screen views for TindaHan Ledger.
Phase 1: Vertical Slice implementation rendering the Store Owner & Merchant Profile.
"""

from django.shortcuts import render


def profile_view(request):
    """Renders the Store Owner & Business Profile screen."""
    profile_data = {
        'store_name': "Aling Nena Tindahan",
        'owner_name': "Elena Santos",
        'avatar_initial': "A",
        'store_role': "Store Owner & Master Merchant",
        'business_category': "Neighborhood Sari-Sari & Retail Convenience",
        'address': "Block 4 Lot 12, Barangay Pinagbuhatan, Pasig City",
        'city': "Pasig City, Metro Manila",
        'postal_code': "1600",
        'phone_number': "+63 917 555 0192",
        'gcash_number': "0917-555-0192",
        'email': "elena.santos@tindahanledger.ph",
        'operating_hours': "6:00 AM – 10:00 PM (Monday – Sunday)",
        'ledger_volume': "Vol. V • Ledger No. 892",
        'member_since': "March 15, 2024 (2+ Years Verified)",
        'terminal_id': "TL-TERM-PASIG-042",
        'device_name': "Samsung Galaxy Tab A9+ (Store POS Terminal)",
        'last_backup': "Today, August 2026 at 02:30 PM",
        'sync_status': "Online • Local Sync Active",
        'active_customers': 48,
        'total_active_utang': 12450.00,
        'settled_accounts': 32,
        'store_rating': "4.9 / 5.0",
        'pos_registers': 1,
    }

    # If user is authenticated, personalize owner name
    if request.user.is_authenticated:
        if request.user.first_name or request.user.last_name:
            profile_data['owner_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        elif request.user.username:
            profile_data['owner_name'] = request.user.username
        if request.user.email:
            profile_data['email'] = request.user.email

    context = {
        'active_nav': 'profile',
        'profile': profile_data,
    }
    return render(request, 'profile/profile.html', context)
