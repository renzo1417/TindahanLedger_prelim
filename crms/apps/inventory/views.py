"""
Inventory management views for TindaHan Ledger.
Vertical Slice implementing Master Inventory Management (/inventory/).
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .data import (
    get_all_products,
    get_product_by_id,
    add_product,
    restock_product,
    CATEGORIES,
)


def inventory_list_view(request):
    """Renders Screen 4: Master Inventory Management."""
    category_filter = request.GET.get('category', 'all')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    all_products = get_all_products(category_filter='all', status_filter='all')
    filtered_products = get_all_products(
        category_filter=category_filter,
        status_filter=status_filter,
        search_query=search_query,
    )

    # Compute inventory KPIs
    total_items = len(all_products)
    low_stock_count = sum(1 for p in all_products if p['stock_status'] == 'low_stock')
    expiring_count = sum(1 for p in all_products if p.get('has_expiry', False))
    in_stock_count = sum(1 for p in all_products if p['stock_status'] == 'in_stock')
    
    # Financial metrics for inventory
    total_puhunan_value = sum(
        (float(p.get('cost_price', 0)) * int(p.get('stock_quantity', 0)))
        for p in all_products
    )
    total_retail_value = sum(
        (float(p.get('selling_price', 0)) * int(p.get('stock_quantity', 0)))
        for p in all_products
    )
    total_projected_profit = total_retail_value - total_puhunan_value
    total_units_on_hand = sum(int(p.get('stock_quantity', 0)) for p in all_products)

    context = {
        'active_nav': 'inventory',
        'products': filtered_products,
        'selected_category': category_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'categories': CATEGORIES,
        'total_products_count': total_items,
        'low_stock_count': low_stock_count,
        'expiring_count': expiring_count,
        'in_stock_count': in_stock_count,
        'total_puhunan_value': total_puhunan_value,
        'total_retail_value': total_retail_value,
        'total_projected_profit': total_projected_profit,
        'total_units_on_hand': total_units_on_hand,
    }
    return render(request, 'inventory/inventory_list.html', context)


def product_create_view(request):
    """Handles adding a new paninda product."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'Instant Noodles')
        sku = request.POST.get('sku', '').strip()
        unit = request.POST.get('unit', 'pc')
        cost_price = request.POST.get('cost_price', 0.0)
        selling_price = request.POST.get('selling_price', 0.0)
        stock_quantity = request.POST.get('stock_quantity', 0)
        low_stock_threshold = request.POST.get('low_stock_threshold', 10)
        has_expiry = request.POST.get('has_expiry') == 'on'

        if name:
            add_product(
                name=name,
                category=category,
                sku=sku,
                unit=unit,
                cost_price=cost_price,
                selling_price=selling_price,
                low_stock_threshold=low_stock_threshold,
                initial_stock=stock_quantity,
                has_expiry=has_expiry,
            )
            messages.success(request, f"Product '{name}' registered into inventory!")
            return redirect('inventory:inventory_list')

    context = {
        'active_nav': 'inventory',
        'categories': [c for c in CATEGORIES if c != 'All'],
    }
    return render(request, 'inventory/inventory_list.html', context)


def product_detail_view(request, product_id):
    """View product detail and handle restocking."""
    product = get_product_by_id(product_id)
    if not product:
        product = get_product_by_id(1)

    if request.method == 'POST':
        add_qty = request.POST.get('quantity', 0)
        cost = request.POST.get('cost_price', None)
        selling = request.POST.get('selling_price', None)
        restock_product(product['id'], add_qty, cost, selling)
        messages.success(request, f"Successfully restocked {add_qty} {product['unit']}s for {product['name']}!")
        return redirect('inventory:inventory_list')

    context = {
        'active_nav': 'inventory',
        'product': product,
    }
    return render(request, 'inventory/inventory_list.html', context)
