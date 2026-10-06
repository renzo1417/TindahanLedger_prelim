"""
Customer and Utang Ledger views for TindaHan Ledger.
Vertical Slice implementing:
  1. Utang Ledger Directory (/utang/)
  2. Customer Utang Ledger Detail Sheet (/utang/<int:customer_id>/)
  3. Register New Customer / Borrower (/utang/register/)
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .data import (
    get_all_customers,
    get_customer_by_id,
    add_customer,
    record_utang,
    record_bayad,
    get_sms_message,
)


def customer_list_view(request):
    """Renders Screen 1: Utang Ledger Directory."""
    filter_status = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '').strip()

    all_custs = get_all_customers(status_filter='all')
    filtered_customers = get_all_customers(status_filter=filter_status, search_query=search_query)

    # Compute summary stats
    total_balance = sum(c['running_balance'] for c in all_custs)
    overdue_count = sum(1 for c in all_custs if c['status'] == 'overdue')
    active_count = sum(1 for c in all_custs if c['status'] == 'active')
    settled_count = sum(1 for c in all_custs if c['status'] == 'settled')

    context = {
        'active_nav': 'utang',
        'customers': filtered_customers,
        'selected_filter': filter_status,
        'search_query': search_query,
        'total_customers_count': len(all_custs),
        'overdue_count': overdue_count,
        'active_count': active_count,
        'settled_count': settled_count,
        'total_utang_balance': total_balance,
    }
    return render(request, 'customers/customer_list.html', context)


def customer_detail_view(request, customer_id):
    """Renders Screen 2: Customer Utang Ledger Detail Sheet."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        customer = get_customer_by_id(1)

    # Handle Modal Actions (Log Utang / Log Bayad)
    if request.method == 'POST':
        action_type = request.POST.get('action_type', '').strip().lower()
        amount = request.POST.get('amount', 0)
        try:
            amount_val = float(amount)
        except (ValueError, TypeError):
            amount_val = 0.00

        if action_type == 'utang' and amount_val > 0:
            items_summary = request.POST.get('items_summary', '')
            due_date = request.POST.get('due_date', None)
            notes = request.POST.get('notes', '')
            record_utang(customer['id'], amount_val, items_summary, due_date, notes)
            messages.success(request, f"₱{amount_val:,.2f} utang recorded for {customer['name']}.")
            return redirect('customers:customer_detail', customer_id=customer['id'])

        elif action_type == 'bayad' and amount_val > 0:
            payment_mode = request.POST.get('payment_mode', 'Cash')
            notes = request.POST.get('notes', '')
            record_bayad(customer['id'], amount_val, payment_mode, notes)
            messages.success(request, f"₱{amount_val:,.2f} payment recorded for {customer['name']}.")
            return redirect('customers:customer_detail', customer_id=customer['id'])

    # Re-fetch customer after potential transaction
    customer = get_customer_by_id(customer['id'])

    # Store profile defaults
    store_name = "Aling Nena Tindahan"
    gcash_number = "0917-555-0192"
    if hasattr(request, 'global_store_profile'):
        store_name = request.global_store_profile.get('store_name', store_name)
        gcash_number = request.global_store_profile.get('gcash_number', gcash_number)

    polite_sms = get_sms_message(
        customer['name'], customer['running_balance'], store_name, gcash_number, tone='polite'
    )
    firm_sms = get_sms_message(
        customer['name'], customer['running_balance'], store_name, gcash_number, tone='firm'
    )
    default_sms = firm_sms if customer['status'] == 'overdue' else polite_sms

    context = {
        'active_nav': 'utang',
        'customer': customer,
        'polite_sms': polite_sms,
        'firm_sms': firm_sms,
        'default_sms': default_sms,
    }
    return render(request, 'customers/customer_detail.html', context)


def customer_create_view(request):
    """Renders Screen 3: Register New Customer / Borrower."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        nickname = request.POST.get('nickname', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        credit_limit = request.POST.get('credit_limit', 1000.00)
        initial_balance = request.POST.get('initial_balance', 0.00)
        initial_summary = request.POST.get('initial_summary', '').strip()

        if name:
            new_cust = add_customer(
                name=name,
                nickname=nickname,
                phone=phone,
                address=address,
                credit_limit=credit_limit,
                initial_balance=initial_balance,
                initial_summary=initial_summary,
            )
            messages.success(request, f"Customer {name} successfully added to ledger!")
            return redirect('customers:customer_detail', customer_id=new_cust['id'])

    context = {
        'active_nav': 'utang',
    }
    return render(request, 'customers/customer_create.html', context)
