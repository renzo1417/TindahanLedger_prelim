"""
Data provider and service layer for Master Inventory Management.
Handles hybrid ORM persistence with graceful fallback to curated mock data.
"""

from decimal import Decimal
from datetime import datetime, date
from copy import deepcopy

CATEGORIES = [
    'All',
    'Instant Noodles',
    'Beverages',
    'Canned Goods',
    'Snacks & Candies',
    'Household',
    'Condiments',
]

INITIAL_PRODUCTS = [
    {
        'id': 1,
        'name': "Lucky Me Pancit Canton (Calamansi)",
        'category': "Instant Noodles",
        'sku': "SKU-NML-001",
        'unit': "pack",
        'selling_price': 18.00,
        'cost_price': 14.50,
        'profit_margin': 3.50,
        'profit_margin_pct': 24.1,
        'stock_quantity': 42,
        'low_stock_threshold': 15,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 2,
        'batches': [
            {
                'batch_code': "BT-2026-0055",
                'expiry_date': "Jan 10, 2027",
                'quantity': 34,
                'status': "healthy",
                'status_label': "Fresh (148d left)",
                'shelf_location': "Shelf A-1",
            },
            {
                'batch_code': "BT-2026-0042",
                'expiry_date': "Nov 05, 2026",
                'quantity': 8,
                'status': "healthy",
                'status_label': "Safe (82d left)",
                'shelf_location': "Shelf A-1",
            },
        ],
    },
    {
        'id': 2,
        'name': "Lucky Me Pancit Canton (Chili Mansi)",
        'category': "Instant Noodles",
        'sku': "SKU-NML-002",
        'unit': "pack",
        'selling_price': 18.00,
        'cost_price': 14.50,
        'profit_margin': 3.50,
        'profit_margin_pct': 24.1,
        'stock_quantity': 8,
        'low_stock_threshold': 15,
        'stock_status': "low_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0033",
                'expiry_date': "Aug 12, 2026",
                'quantity': 8,
                'status': "expiring_soon",
                'status_label': "Expires in 3 days",
                'shelf_location': "Shelf A-2",
            },
        ],
    },
    {
        'id': 3,
        'name': "San Miguel Pale Pilsen 330ml",
        'category': "Beverages",
        'sku': "SKU-BEV-001",
        'unit': "bottle",
        'selling_price': 65.00,
        'cost_price': 54.00,
        'profit_margin': 11.00,
        'profit_margin_pct': 20.4,
        'stock_quantity': 24,
        'low_stock_threshold': 12,
        'stock_status': "in_stock",
        'has_expiry': False,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0019",
                'expiry_date': "Mar 30, 2027",
                'quantity': 24,
                'status': "healthy",
                'status_label': "Fresh",
                'shelf_location': "Chiller B-1",
            },
        ],
    },
    {
        'id': 4,
        'name': "Argentina Corned Beef 150g",
        'category': "Canned Goods",
        'sku': "SKU-CND-001",
        'unit': "can",
        'selling_price': 42.00,
        'cost_price': 34.50,
        'profit_margin': 7.50,
        'profit_margin_pct': 21.7,
        'stock_quantity': 5,
        'low_stock_threshold': 10,
        'stock_status': "low_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0041",
                'expiry_date': "Aug 20, 2026",
                'quantity': 5,
                'status': "expiring_soon",
                'status_label': "Expires in 5 days",
                'shelf_location': "Shelf A-3",
            },
        ],
    },
    {
        'id': 5,
        'name': "555 Sardines in Tomato Sauce 155g",
        'category': "Canned Goods",
        'sku': "SKU-CND-002",
        'unit': "can",
        'selling_price': 26.00,
        'cost_price': 21.00,
        'profit_margin': 5.00,
        'profit_margin_pct': 23.8,
        'stock_quantity': 18,
        'low_stock_threshold': 12,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0077",
                'expiry_date': "Dec 15, 2027",
                'quantity': 18,
                'status': "healthy",
                'status_label': "Fresh (480d left)",
                'shelf_location': "Shelf A-3",
            },
        ],
    },
    {
        'id': 6,
        'name': "Kopiko Blanca 3-in-1 Twin Pack",
        'category': "Beverages",
        'sku': "SKU-BEV-002",
        'unit': "twin-pack",
        'selling_price': 16.00,
        'cost_price': 13.00,
        'profit_margin': 3.00,
        'profit_margin_pct': 23.1,
        'stock_quantity': 36,
        'low_stock_threshold': 15,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0081",
                'expiry_date': "Oct 12, 2026",
                'quantity': 36,
                'status': "healthy",
                'status_label': "Fresh (58d left)",
                'shelf_location': "Hanger 1",
            },
        ],
    },
    {
        'id': 7,
        'name': "Surf Powder Blossom Fresh 65g",
        'category': "Household",
        'sku': "SKU-HSD-001",
        'unit': "sachet",
        'selling_price': 12.00,
        'cost_price': 9.75,
        'profit_margin': 2.25,
        'profit_margin_pct': 23.1,
        'stock_quantity': 4,
        'low_stock_threshold': 10,
        'stock_status': "low_stock",
        'has_expiry': False,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0011",
                'expiry_date': "Jan 01, 2028",
                'quantity': 4,
                'status': "healthy",
                'status_label': "Stock stable",
                'shelf_location': "Shelf C-1",
            },
        ],
    },
    {
        'id': 8,
        'name': "Datu Puti Vinegar (Suka) 350ml",
        'category': "Condiments",
        'sku': "SKU-CND-003",
        'unit': "bottle",
        'selling_price': 22.00,
        'cost_price': 17.50,
        'profit_margin': 4.50,
        'profit_margin_pct': 25.7,
        'stock_quantity': 14,
        'low_stock_threshold': 8,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0029",
                'expiry_date': "Jun 18, 2027",
                'quantity': 14,
                'status': "healthy",
                'status_label': "Fresh (310d left)",
                'shelf_location': "Shelf B-2",
            },
        ],
    },
    {
        'id': 9,
        'name': "Chippy Barbecue 110g",
        'category': "Snacks & Candies",
        'sku': "SKU-SNK-001",
        'unit': "pack",
        'selling_price': 28.00,
        'cost_price': 22.50,
        'profit_margin': 5.50,
        'profit_margin_pct': 24.4,
        'stock_quantity': 15,
        'low_stock_threshold': 10,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0048",
                'expiry_date': "Sep 28, 2026",
                'quantity': 15,
                'status': "healthy",
                'status_label': "Fresh (44d left)",
                'shelf_location': "Rack 2",
            },
        ],
    },
    {
        'id': 10,
        'name': "Bear Brand Fortified Milk 33g",
        'category': "Beverages",
        'sku': "SKU-BEV-003",
        'unit': "sachet",
        'selling_price': 15.00,
        'cost_price': 12.00,
        'profit_margin': 3.00,
        'profit_margin_pct': 25.0,
        'stock_quantity': 28,
        'low_stock_threshold': 12,
        'stock_status': "in_stock",
        'has_expiry': True,
        'active_batches_count': 1,
        'batches': [
            {
                'batch_code': "BT-2026-0062",
                'expiry_date': "Aug 22, 2026",
                'quantity': 18,
                'status': "expiring_soon",
                'status_label': "Expires in 7 days",
                'shelf_location': "Shelf C-2",
            },
        ],
    },
]

# In-memory working copy
_PRODUCT_STORE = deepcopy(INITIAL_PRODUCTS)


def _seed_inventory_db_if_empty():
    """Seeds SQLite database tables if Product model is empty."""
    try:
        from apps.home.models import Product, Category, ProductBatch, Store, User
        if Product.objects.exists():
            return

        store = Store.objects.first()
        if not store:
            user = User.objects.first()
            if not user:
                user = User.objects.create(
                    username="admin_store",
                    password_hash="mock_hash",
                    first_name="Elena",
                    last_name="Santos",
                )
            store = Store.objects.create(
                user=user,
                store_name="Aling Nena Tindahan",
                owner_name="Elena Santos",
                phone_number="+63 917 555 0192",
                gcash_number="0917-555-0192",
                is_device_synced=True,
            )

        category_map = {}
        for cat_name in ['Instant Noodles', 'Beverages', 'Canned Goods', 'Snacks & Candies', 'Household', 'Condiments']:
            cat, _ = Category.objects.get_or_create(store=store, name=cat_name, slug=cat_name.lower().replace(' ', '-'))
            category_map[cat_name] = cat

        for p in INITIAL_PRODUCTS:
            cat = category_map.get(p['category'])
            prod = Product.objects.create(
                id=p['id'],
                store=store,
                category=cat,
                name=p['name'],
                sku=p['sku'],
                unit=p['unit'],
                selling_price=Decimal(str(p['selling_price'])),
                cost_price=Decimal(str(p['cost_price'])),
                profit_margin=Decimal(str(p['profit_margin'])),
                profit_margin_pct=Decimal(str(p['profit_margin_pct'])),
                stock_quantity=p['stock_quantity'],
                low_stock_threshold=p['low_stock_threshold'],
                stock_status=p['stock_status'],
                has_expiry=p['has_expiry'],
                active_batches_count=p['active_batches_count'],
            )
            for b in p.get('batches', []):
                ProductBatch.objects.create(
                    product=prod,
                    batch_code=b['batch_code'],
                    quantity=b['quantity'],
                    cost_price=prod.cost_price,
                    selling_price=prod.selling_price,
                    status=b.get('status', 'healthy'),
                    status_label=b.get('status_label', ''),
                    shelf_location=b.get('shelf_location', ''),
                )
    except Exception:
        pass


def get_all_products(category_filter='all', status_filter='all', search_query=''):
    """Returns list of products matching category, status, and search filters."""
    _seed_inventory_db_if_empty()

    # Try ORM query
    try:
        from apps.home.models import Product
        db_products = Product.objects.all().select_related('category')
        if db_products.exists():
            results = []
            for p in db_products:
                prod_dict = {
                    'id': p.id,
                    'name': p.name,
                    'category': p.category.name if p.category else 'General',
                    'sku': p.sku or f"SKU-{p.id:03d}",
                    'unit': p.unit,
                    'selling_price': float(p.selling_price),
                    'cost_price': float(p.cost_price),
                    'profit_margin': float(p.profit_margin),
                    'profit_margin_pct': float(p.profit_margin_pct),
                    'stock_quantity': p.stock_quantity,
                    'low_stock_threshold': p.low_stock_threshold,
                    'stock_status': p.stock_status,
                    'has_expiry': p.has_expiry,
                    'active_batches_count': p.active_batches_count,
                }
                results.append(prod_dict)
            return _filter_products(results, category_filter, status_filter, search_query)
    except Exception:
        pass

    return _filter_products(_PRODUCT_STORE, category_filter, status_filter, search_query)


def _filter_products(products_list, category_filter='all', status_filter='all', search_query=''):
    """Filters product dictionaries."""
    filtered = deepcopy(products_list)

    if category_filter and category_filter != 'all':
        filtered = [p for p in filtered if p['category'].lower() == category_filter.lower()]

    if status_filter and status_filter != 'all':
        if status_filter == 'low_stock':
            filtered = [p for p in filtered if p['stock_status'] == 'low_stock']
        elif status_filter == 'in_stock':
            filtered = [p for p in filtered if p['stock_status'] == 'in_stock']
        elif status_filter == 'expiring':
            filtered = [p for p in filtered if p.get('has_expiry', False)]

    if search_query:
        q = search_query.strip().lower()
        filtered = [
            p for p in filtered
            if q in p['name'].lower()
            or q in p.get('sku', '').lower()
            or q in p.get('category', '').lower()
        ]

    return filtered


def get_product_by_id(product_id):
    """Retrieves product detail."""
    for p in _PRODUCT_STORE:
        if p['id'] == int(product_id):
            return deepcopy(p)
    return deepcopy(_PRODUCT_STORE[0]) if _PRODUCT_STORE else None


def add_product(name, category="Instant Noodles", sku="", unit="pc", cost_price=0.0, selling_price=0.0, low_stock_threshold=10, initial_stock=0, has_expiry=False):
    """Adds a new paninda item into inventory."""
    cost = float(cost_price or 0.0)
    selling = float(selling_price or 0.0)
    margin = selling - cost
    margin_pct = round((margin / cost * 100), 1) if cost > 0 else 0.0
    stock = int(initial_stock or 0)
    threshold = int(low_stock_threshold or 10)
    stock_status = 'low_stock' if stock <= threshold else 'in_stock'

    new_id = len(_PRODUCT_STORE) + 1
    new_prod = {
        'id': new_id,
        'name': name.strip(),
        'category': category.strip(),
        'sku': sku.strip() or f"SKU-{category[:3].upper()}-{new_id:03d}",
        'unit': unit.strip() or 'pc',
        'selling_price': selling,
        'cost_price': cost,
        'profit_margin': margin,
        'profit_margin_pct': margin_pct,
        'stock_quantity': stock,
        'low_stock_threshold': threshold,
        'stock_status': stock_status,
        'has_expiry': bool(has_expiry),
        'active_batches_count': 1 if stock > 0 else 0,
        'batches': [],
    }

    _PRODUCT_STORE.insert(0, new_prod)

    # Save to DB if available
    try:
        from apps.home.models import Product, Category, Store
        store = Store.objects.first()
        cat = Category.objects.filter(name=category).first()
        if not cat and store:
            cat = Category.objects.create(store=store, name=category, slug=category.lower().replace(' ', '-'))
        if store:
            db_p = Product.objects.create(
                store=store,
                category=cat,
                name=name.strip(),
                sku=new_prod['sku'],
                unit=unit,
                selling_price=Decimal(str(selling)),
                cost_price=Decimal(str(cost)),
                profit_margin=Decimal(str(margin)),
                profit_margin_pct=Decimal(str(margin_pct)),
                stock_quantity=stock,
                low_stock_threshold=threshold,
                stock_status=stock_status,
                has_expiry=bool(has_expiry),
                active_batches_count=1 if stock > 0 else 0,
            )
            new_prod['id'] = db_p.id
    except Exception:
        pass

    return new_prod


def restock_product(product_id, add_quantity, cost_price=None, selling_price=None, batch_code='', expiry_date=None, shelf_location=''):
    """Restocks an inventory item with a new batch."""
    add_qty = int(add_quantity or 0)
    for p in _PRODUCT_STORE:
        if p['id'] == int(product_id):
            p['stock_quantity'] += add_qty
            if p['stock_quantity'] > p['low_stock_threshold']:
                p['stock_status'] = 'in_stock'
            if cost_price:
                p['cost_price'] = float(cost_price)
            if selling_price:
                p['selling_price'] = float(selling_price)
                p['profit_margin'] = p['selling_price'] - p['cost_price']
                p['profit_margin_pct'] = round((p['profit_margin'] / p['cost_price'] * 100), 1) if p['cost_price'] > 0 else 0.0
            p['active_batches_count'] = p.get('active_batches_count', 0) + 1
            break
