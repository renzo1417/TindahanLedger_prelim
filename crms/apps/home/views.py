"""
Home screen views for TindaHan Ledger.
Phase 1: Vertical Slice implementation rendering the Daily Store Overview with rich mock data.
"""

from django.shortcuts import render
from datetime import date


def home_view(request):
    """Renders the main Daily Store Overview (Home Screen)."""
    # 4 Primary KPIs
    kpis = {
        'today_sales_total': 3847.50,
        'today_sales_count': 23,
        'total_utang_balance': 12450.00,
        'overdue_accounts_count': 4,
        'low_stock_items_count': 7,
        'expiry_alert_batches_count': 4,
        'expired_batches_count': 1,
    }

    # Expiring Soon & Expired Batches (FIFO Priority)
    urgent_batches = [
        {
            'product_name': 'Argentina Corned Beef 150g',
            'batch_code': 'BT-2026-0041',
            'quantity': 12,
            'shelf_location': 'Shelf A-3',
            'status': 'expiring_soon',
            'status_label': 'Expires in 3 days',
            'product_id': 1,
        },
        {
            'product_name': 'Nestea Iced Tea Sachet',
            'batch_code': 'BT-2026-0038',
            'quantity': 24,
            'shelf_location': 'Shelf B-1',
            'status': 'expired',
            'status_label': 'Expired 2 days ago',
            'product_id': 2,
        },
        {
            'product_name': 'Lucky Me Pancit Canton (Calamansi)',
            'batch_code': 'BT-2026-0055',
            'quantity': 36,
            'shelf_location': 'Shelf A-1',
            'status': 'expiring_soon',
            'status_label': 'Expires in 7 days',
            'product_id': 3,
        },
        {
            'product_name': 'Bear Brand Fortified Milk 33g',
            'batch_code': 'BT-2026-0062',
            'quantity': 18,
            'shelf_location': 'Shelf C-2',
            'status': 'expiring_soon',
            'status_label': 'Expires in 5 days',
            'product_id': 4,
        },
    ]

    # Overdue Utang Accounts
    overdue_customers = [
        {
            'id': 1,
            'name': 'Maria Santos',
            'nickname': 'Aling Maria',
            'avatar_letter': 'M',
            'running_balance': 2350.00,
            'credit_limit': 5000,
            'days_overdue': 12,
            'due_date': 'Aug 25, 2026',
        },
        {
            'id': 2,
            'name': 'Pedro Reyes',
            'nickname': 'Mang Pedro',
            'avatar_letter': 'P',
            'running_balance': 1800.00,
            'credit_limit': 3000,
            'days_overdue': 8,
            'due_date': 'Aug 29, 2026',
        },
        {
            'id': 3,
            'name': 'Rosa dela Cruz',
            'nickname': 'Ate Rosa',
            'avatar_letter': 'R',
            'running_balance': 950.00,
            'credit_limit': 2000,
            'days_overdue': 5,
            'due_date': 'Sep 01, 2026',
        },
        {
            'id': 4,
            'name': 'Juan Bautista',
            'nickname': 'Kuya Juan',
            'avatar_letter': 'J',
            'running_balance': 1420.00,
            'credit_limit': 2500,
            'days_overdue': 2,
            'due_date': 'Sep 04, 2026',
        },
    ]

    # Today's Chronological Sales & Transactions Tape
    today_sales_log = [
        {
            'time': '2:15 PM',
            'customer_name': 'Walk-in Customer',
            'payment_method': 'Cash',
            'items_summary': '3 items (Pancit Canton, Coke Mismo, SkyFlakes)',
            'receipt_no': 'TL-0923',
            'total_amount': 245.00,
            'profit_earned': 38.50,
        },
        {
            'time': '1:42 PM',
            'customer_name': 'Aling Maria',
            'payment_method': 'Utang',
            'items_summary': '5 items (Corned Beef, Rice 2kg, Cooking Oil)',
            'receipt_no': 'TL-0922',
            'total_amount': 520.00,
            'profit_earned': 72.00,
        },
        {
            'time': '12:30 PM',
            'customer_name': 'Mang Pedro',
            'payment_method': 'Bayad',
            'items_summary': 'Partial Utang Payment Settlement',
            'receipt_no': 'TL-0921',
            'total_amount': 800.00,
            'profit_earned': 0,
        },
        {
            'time': '11:05 AM',
            'customer_name': 'Walk-in Customer',
            'payment_method': 'Cash',
            'items_summary': '2 items (Great Taste White 3-in-1, Bread)',
            'receipt_no': 'TL-0920',
            'total_amount': 185.00,
            'profit_earned': 27.50,
        },
        {
            'time': '9:20 AM',
            'customer_name': 'Ate Luz',
            'payment_method': 'Cash',
            'items_summary': '7 items (Eggs 1 tray, Sugar 1kg, Milk)',
            'receipt_no': 'TL-0919',
            'total_amount': 632.50,
            'profit_earned': 94.00,
        },
    ]

    context = {
        'active_nav': 'home',
        'current_date': date.today().strftime('%B %d, %Y'),
        'kpis': kpis,
        'urgent_batches': urgent_batches,
        'overdue_customers': overdue_customers,
        'today_sales_log': today_sales_log,
    }
    return render(request, 'home/home.html', context)
