"""
Data provider and service layer for Customers & Utang Ledger.
Handles hybrid ORM database persistence with graceful fallback to curated mock data.
"""

from decimal import Decimal
from datetime import datetime, date
from copy import deepcopy
import sys

# Seed dataset of authentic Philippine sari-sari store customers
INITIAL_CUSTOMERS = [
    {
        'id': 1,
        'name': "Dennis Cruz",
        'nickname': "Kuya Dennis",
        'avatar_letter': "D",
        'address': "Purok 1, near Basketball Court",
        'phone': "0918-234-5678",
        'gcash': "0918-234-5678",
        'credit_limit': 1500.00,
        'running_balance': 850.00,
        'status': "overdue",
        'status_label': "Overdue (5 days)",
        'due_date': "Aug 10, 2026",
        'last_payment_date': "Aug 01, 2026",
        'days_overdue': 5,
        'notes': "Promises to pay every 15th and 30th payday (construction worker).",
        'transactions': [
            {
                'id': 101,
                'date': "Aug 01, 2026",
                'time': "06:15 PM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 500.00,
                'balance_after': 350.00,
                'items_summary': "Cash payment given by Dennis personally",
                'reference_no': "PAY-0801-01",
                'notes': "Paid directly at cashier window",
            },
            {
                'id': 102,
                'date': "Aug 04, 2026",
                'time': "07:30 AM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 250.00,
                'balance_after': 600.00,
                'items_summary': "5x Kopiko Blanca, 3x Lucky Me Calamansi, 1kg Bigas",
                'reference_no': "CRD-0804-12",
                'notes': "Almusal groceries for family",
            },
            {
                'id': 103,
                'date': "Aug 08, 2026",
                'time': "08:10 PM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 250.00,
                'balance_after': 850.00,
                'items_summary': "3x San Miguel Pale Pilsen, 1x Chippy BBQ",
                'reference_no': "CRD-0808-44",
                'notes': "Saturday night purchase",
            },
        ],
    },
    {
        'id': 2,
        'name': "Marites Tolentino",
        'nickname': "Ate Marites",
        'avatar_letter': "M",
        'address': "Block 2 Lot 9, Riverside Drive",
        'phone': "0920-567-8901",
        'gcash': "0920-567-8901",
        'credit_limit': 2000.00,
        'running_balance': 1240.00,
        'status': "overdue",
        'status_label': "Overdue (12 days)",
        'due_date': "Aug 03, 2026",
        'last_payment_date': "Jul 22, 2026",
        'days_overdue': 12,
        'notes': "High volume borrower for family carinderia. Friendly reminder needed.",
        'transactions': [
            {
                'id': 201,
                'date': "Jul 22, 2026",
                'time': "02:40 PM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 800.00,
                'balance_after': 400.00,
                'items_summary': "Partial payment via GCash transfer",
                'reference_no': "PAY-0722-09",
                'notes': "Ref: GCASH-8921104",
            },
            {
                'id': 202,
                'date': "Jul 27, 2026",
                'time': "11:15 AM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 840.00,
                'balance_after': 1240.00,
                'items_summary': "Cooking oil 1L, Soy sauce 1L, Onions, 2kg Sugar",
                'reference_no': "CRD-0727-21",
                'notes': "Carinderia ingredients",
            },
        ],
    },
    {
        'id': 3,
        'name': "Mang Tomas Reyes",
        'nickname': "Tito Tomas",
        'avatar_letter': "T",
        'address': "Lot 14 Main Street, across Chapel",
        'phone': "0917-888-4321",
        'gcash': "0917-888-4321",
        'credit_limit': 1000.00,
        'running_balance': 450.00,
        'status': "active",
        'status_label': "Active Utang",
        'due_date': "Aug 20, 2026",
        'last_payment_date': "Aug 05, 2026",
        'days_overdue': 0,
        'notes': "Regular customer. Always pays on time.",
        'transactions': [
            {
                'id': 301,
                'date': "Aug 05, 2026",
                'time': "09:00 AM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 300.00,
                'balance_after': 0.00,
                'items_summary': "Full payment settled",
                'reference_no': "PAY-0805-03",
                'notes': "Paid in cash",
            },
            {
                'id': 302,
                'date': "Aug 09, 2026",
                'time': "04:15 PM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 450.00,
                'balance_after': 450.00,
                'items_summary': "2x Argentina Corned Beef, 1 tray Eggs",
                'reference_no': "CRD-0809-18",
                'notes': "Sunday groceries",
            },
        ],
    },
    {
        'id': 4,
        'name': "Gina Dimaculangan",
        'nickname': "Ate Gina",
        'avatar_letter': "G",
        'address': "Purok 3, Mango Lane",
        'phone': "0919-444-2233",
        'gcash': "0919-444-2233",
        'credit_limit': 800.00,
        'running_balance': 300.00,
        'status': "active",
        'status_label': "Active Utang",
        'due_date': "Aug 25, 2026",
        'last_payment_date': "Jul 29, 2026",
        'days_overdue': 0,
        'notes': "School teacher. Reliable payer.",
        'transactions': [
            {
                'id': 401,
                'date': "Jul 29, 2026",
                'time': "05:10 PM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 200.00,
                'balance_after': 0.00,
                'items_summary': "Cash settlement",
                'reference_no': "PAY-0729-07",
                'notes': "Paid after work",
            },
            {
                'id': 402,
                'date': "Aug 11, 2026",
                'time': "01:20 PM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 300.00,
                'balance_after': 300.00,
                'items_summary': "Shampoo sachets, Safeguard soap, Ariel powder",
                'reference_no': "CRD-0811-05",
                'notes': "Household cleaning supplies",
            },
        ],
    },
    {
        'id': 5,
        'name': "Rodel Pogoy",
        'nickname': "Kuya Rodel",
        'avatar_letter': "R",
        'address': "Block 5 Lot 8, Mahogany Street",
        'phone': "0917-123-9988",
        'gcash': "0917-123-9988",
        'credit_limit': 3000.00,
        'running_balance': 0.00,
        'status': "settled",
        'status_label': "Settled / No Utang",
        'due_date': "Aug 30, 2026",
        'last_payment_date': "Aug 12, 2026",
        'days_overdue': 0,
        'notes': "Excellent credit standing. Highly trustworthy.",
        'transactions': [
            {
                'id': 501,
                'date': "Aug 10, 2026",
                'time': "10:30 AM",
                'type': "utang",
                'type_label': "Pautang (Credit)",
                'amount': 650.00,
                'balance_after': 650.00,
                'items_summary': "5kg Rice, Cooking Oil, 4x Canned Sardines",
                'reference_no': "CRD-0810-15",
                'notes': "Family groceries",
            },
            {
                'id': 502,
                'date': "Aug 12, 2026",
                'time': "03:45 PM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 650.00,
                'balance_after': 0.00,
                'items_summary': "Full payment via GCash",
                'reference_no': "PAY-0812-11",
                'notes': "Settled in full before due date",
            },
        ],
    },
    {
        'id': 6,
        'name': "Lorna Magbanua",
        'nickname': "Nanay Lorna",
        'avatar_letter': "L",
        'address': "Purok 4, near Barangay Hall",
        'phone': "0928-765-4321",
        'gcash': "0928-765-4321",
        'credit_limit': 1200.00,
        'running_balance': 0.00,
        'status': "settled",
        'status_label': "Settled / No Utang",
        'due_date': "Aug 28, 2026",
        'last_payment_date': "Aug 06, 2026",
        'days_overdue': 0,
        'notes': "Senior citizen. Senior discount applied when paying cash.",
        'transactions': [
            {
                'id': 601,
                'date': "Aug 06, 2026",
                'time': "11:00 AM",
                'type': "bayad",
                'type_label': "Bayad (Payment)",
                'amount': 420.00,
                'balance_after': 0.00,
                'items_summary': "Cash payment by daughter",
                'reference_no': "PAY-0806-02",
                'notes': "Account clear",
            },
        ],
    },
]

# In-memory working copy (persisted during session)
_CUSTOMER_STORE = deepcopy(INITIAL_CUSTOMERS)


def _seed_db_if_empty():
    """Seeds SQLite database tables if Customer model is empty."""
    try:
        from apps.home.models import Customer, CustomerLedgerTransaction, Store, User
        if Customer.objects.exists():
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

        for c in INITIAL_CUSTOMERS:
            cust = Customer.objects.create(
                id=c['id'],
                store=store,
                name=c['name'],
                nickname=c.get('nickname', ''),
                avatar_letter=c['avatar_letter'],
                phone=c.get('phone', ''),
                gcash=c.get('gcash', ''),
                address=c.get('address', ''),
                credit_limit=Decimal(str(c.get('credit_limit', 0))),
                running_balance=Decimal(str(c.get('running_balance', 0))),
                status=c.get('status', 'active'),
                status_label=c.get('status_label', ''),
                days_overdue=c.get('days_overdue', 0),
                notes=c.get('notes', ''),
            )
            for tx in c.get('transactions', []):
                CustomerLedgerTransaction.objects.create(
                    customer=cust,
                    reference_no=tx.get('reference_no', f"TX-{tx['id']}"),
                    transaction_type=tx['type'],
                    type_label=tx.get('type_label', tx['type'].title()),
                    amount=Decimal(str(tx['amount'])),
                    running_balance=Decimal(str(tx.get('balance_after', 0))),
                    items_summary=tx.get('items_summary', ''),
                    notes=tx.get('notes', ''),
                )
    except Exception as e:
        # Graceful fallback: SQLite or connection issue should never break the request
        pass


def get_all_customers(status_filter='all', search_query=''):
    """Returns list of all customers matching optional status filter and search query."""
    _seed_db_if_empty()
    
    # Try querying ORM first
    try:
        from apps.home.models import Customer
        db_customers = Customer.objects.all().order_by('-running_balance')
        if db_customers.exists():
            results = []
            for c in db_customers:
                cust_dict = {
                    'id': c.id,
                    'name': c.name,
                    'nickname': c.nickname or '',
                    'avatar_letter': c.avatar_letter or (c.name[0].upper() if c.name else 'A'),
                    'address': c.address or 'Brgy. Poblacion',
                    'phone': c.phone or '',
                    'gcash': c.gcash or c.phone or '',
                    'credit_limit': float(c.credit_limit),
                    'running_balance': float(c.running_balance),
                    'status': c.status,
                    'status_label': c.status_label or ('Overdue' if c.status == 'overdue' else ('Active Utang' if c.status == 'active' else 'Settled')),
                    'due_date': c.due_date.strftime('%b %d, %Y') if c.due_date else 'Aug 30, 2026',
                    'last_payment_date': c.last_payment_date.strftime('%b %d, %Y') if c.last_payment_date else 'Aug 01, 2026',
                    'days_overdue': c.days_overdue,
                    'notes': c.notes or '',
                }
                results.append(cust_dict)
            return _filter_customers(results, status_filter, search_query)
    except Exception:
        pass

    # Fallback to in-memory store
    return _filter_customers(_CUSTOMER_STORE, status_filter, search_query)


def _filter_customers(customers_list, status_filter='all', search_query=''):
    """Filters a list of customer dicts by status and search text."""
    filtered = deepcopy(customers_list)

    if status_filter and status_filter != 'all':
        if status_filter == 'overdue':
            filtered = [c for c in filtered if c['status'] == 'overdue']
        elif status_filter == 'active':
            filtered = [c for c in filtered if c['status'] == 'active']
        elif status_filter == 'settled':
            filtered = [c for c in filtered if c['status'] == 'settled']

    if search_query:
        q = search_query.strip().lower()
        filtered = [
            c for c in filtered
            if q in c['name'].lower()
            or q in c.get('nickname', '').lower()
            or q in c.get('phone', '').lower()
            or q in c.get('address', '').lower()
        ]

    return filtered


def get_customer_by_id(customer_id):
    """Retrieves customer detail with full transaction history."""
    try:
        from apps.home.models import Customer
        c = Customer.objects.filter(id=customer_id).first()
        if c:
            txs = []
            for tx in c.ledger_transactions.all().order_by('-transaction_date'):
                txs.append({
                    'id': tx.id,
                    'date': tx.transaction_date.strftime('%b %d, %Y'),
                    'time': tx.transaction_date.strftime('%I:%M %p'),
                    'type': tx.transaction_type,
                    'type_label': tx.type_label or tx.transaction_type.title(),
                    'amount': float(tx.amount),
                    'balance_after': float(tx.running_balance),
                    'items_summary': tx.items_summary or 'Sari-sari store items',
                    'reference_no': tx.reference_no,
                    'notes': tx.notes,
                })
            return {
                'id': c.id,
                'name': c.name,
                'nickname': c.nickname or '',
                'avatar_letter': c.avatar_letter or (c.name[0].upper() if c.name else 'A'),
                'address': c.address or 'Brgy. Poblacion',
                'phone': c.phone or '',
                'gcash': c.gcash or c.phone or '',
                'credit_limit': float(c.credit_limit),
                'running_balance': float(c.running_balance),
                'status': c.status,
                'status_label': c.status_label or ('Overdue' if c.status == 'overdue' else ('Active Utang' if c.status == 'active' else 'Settled')),
                'due_date': c.due_date.strftime('%b %d, %Y') if c.due_date else 'Aug 30, 2026',
                'last_payment_date': c.last_payment_date.strftime('%b %d, %Y') if c.last_payment_date else 'Aug 01, 2026',
                'days_overdue': c.days_overdue,
                'notes': c.notes or '',
                'transactions': txs,
            }
    except Exception:
        pass

    for c in _CUSTOMER_STORE:
        if c['id'] == int(customer_id):
            return deepcopy(c)
    # Fallback to customer 1 if not found
    return deepcopy(_CUSTOMER_STORE[0]) if _CUSTOMER_STORE else None


def add_customer(name, nickname='', phone='', address='', credit_limit=1000.00, initial_balance=0.00, initial_summary=''):
    """Registers a new customer in the ledger, persisting to both DB and memory."""
    credit_limit = float(credit_limit or 1000.00)
    initial_balance = float(initial_balance or 0.00)
    avatar_letter = name.strip()[0].upper() if name.strip() else 'A'
    status = 'active' if initial_balance > 0 else 'settled'
    status_label = 'Active Utang' if initial_balance > 0 else 'Settled / No Utang'

    new_id = len(_CUSTOMER_STORE) + 1
    new_cust = {
        'id': new_id,
        'name': name.strip(),
        'nickname': nickname.strip(),
        'avatar_letter': avatar_letter,
        'address': address.strip() or 'Brgy. Poblacion',
        'phone': phone.strip(),
        'gcash': phone.strip(),
        'credit_limit': credit_limit,
        'running_balance': initial_balance,
        'status': status,
        'status_label': status_label,
        'due_date': "Aug 30, 2026",
        'last_payment_date': "N/A" if initial_balance == 0 else "Today",
        'days_overdue': 0,
        'notes': "Newly registered customer ledger line.",
        'transactions': [],
    }

    if initial_balance > 0:
        new_cust['transactions'].append({
            'id': 1000 + new_id,
            'date': date.today().strftime('%b %d, %Y'),
            'time': datetime.now().strftime('%I:%M %p'),
            'type': 'utang',
            'type_label': 'Pautang (Initial)',
            'amount': initial_balance,
            'balance_after': initial_balance,
            'items_summary': initial_summary.strip() or 'Starting balance from notebook',
            'reference_no': f"INIT-{new_id:04d}",
            'notes': 'Beginning ledger balance',
        })

    # Save to memory store first
    _CUSTOMER_STORE.insert(0, new_cust)

    # Save to DB if available
    try:
        from apps.home.models import Customer, CustomerLedgerTransaction, Store
        store = Store.objects.first()
        if store:
            db_cust = Customer.objects.create(
                store=store,
                name=name.strip(),
                nickname=nickname.strip(),
                avatar_letter=avatar_letter,
                phone=phone.strip(),
                gcash=phone.strip(),
                address=address.strip(),
                credit_limit=Decimal(str(credit_limit)),
                running_balance=Decimal(str(initial_balance)),
                status=status,
                status_label=status_label,
                notes=new_cust['notes'],
            )
            if initial_balance > 0:
                CustomerLedgerTransaction.objects.create(
                    customer=db_cust,
                    reference_no=f"INIT-{db_cust.id:04d}",
                    transaction_type='utang',
                    type_label='Pautang (Initial)',
                    amount=Decimal(str(initial_balance)),
                    running_balance=Decimal(str(initial_balance)),
                    items_summary=initial_summary.strip() or 'Starting balance',
                )
            new_cust['id'] = db_cust.id
    except Exception:
        pass

    return new_cust


def record_utang(customer_id, amount, items_summary='', due_date=None, notes=''):
    """Records a new credit transaction (Pautang) for a customer."""
    amount = float(amount)
    now_str = date.today().strftime('%b %d, %Y')
    time_str = datetime.now().strftime('%I:%M %p')

    # Update memory
    for c in _CUSTOMER_STORE:
        if c['id'] == int(customer_id):
            c['running_balance'] += amount
            c['status'] = 'active'
            c['status_label'] = 'Active Utang'
            tx_id = len(c.get('transactions', [])) + 1
            new_tx = {
                'id': tx_id + 500,
                'date': now_str,
                'time': time_str,
                'type': 'utang',
                'type_label': 'Pautang (Credit)',
                'amount': amount,
                'balance_after': c['running_balance'],
                'items_summary': items_summary or 'Sari-sari store purchase',
                'reference_no': f"CRD-{datetime.now().strftime('%m%d')}-{tx_id:02d}",
                'notes': notes,
            }
            c['transactions'].insert(0, new_tx)
            break

    # Update DB if available
    try:
        from apps.home.models import Customer, CustomerLedgerTransaction
        db_c = Customer.objects.filter(id=customer_id).first()
        if db_c:
            db_c.running_balance += Decimal(str(amount))
            db_c.status = 'active'
            db_c.status_label = 'Active Utang'
            db_c.save()
            CustomerLedgerTransaction.objects.create(
                customer=db_c,
                reference_no=f"CRD-{datetime.now().strftime('%m%d%H%M')}",
                transaction_type='utang',
                type_label='Pautang (Credit)',
                amount=Decimal(str(amount)),
                running_balance=db_c.running_balance,
                items_summary=items_summary or 'Sari-sari store purchase',
                notes=notes,
            )
    except Exception:
        pass


def record_bayad(customer_id, amount, payment_mode='Cash', notes=''):
    """Records a payment settlement transaction (Bayad) for a customer."""
    amount = float(amount)
    now_str = date.today().strftime('%b %d, %Y')
    time_str = datetime.now().strftime('%I:%M %p')

    # Update memory
    for c in _CUSTOMER_STORE:
        if c['id'] == int(customer_id):
            c['running_balance'] = max(0.00, c['running_balance'] - amount)
            if c['running_balance'] <= 0:
                c['status'] = 'settled'
                c['status_label'] = 'Settled / No Utang'
            c['last_payment_date'] = now_str
            tx_id = len(c.get('transactions', [])) + 1
            new_tx = {
                'id': tx_id + 700,
                'date': now_str,
                'time': time_str,
                'type': 'bayad',
                'type_label': 'Bayad (Payment)',
                'amount': amount,
                'balance_after': c['running_balance'],
                'items_summary': f"Payment via {payment_mode}",
                'reference_no': f"PAY-{datetime.now().strftime('%m%d')}-{tx_id:02d}",
                'notes': notes,
            }
            c['transactions'].insert(0, new_tx)
            break

    # Update DB if available
    try:
        from apps.home.models import Customer, CustomerLedgerTransaction
        db_c = Customer.objects.filter(id=customer_id).first()
        if db_c:
            db_c.running_balance = max(Decimal('0.00'), db_c.running_balance - Decimal(str(amount)))
            if db_c.running_balance <= Decimal('0.00'):
                db_c.status = 'settled'
                db_c.status_label = 'Settled / No Utang'
            db_c.last_payment_date = date.today()
            db_c.save()
            CustomerLedgerTransaction.objects.create(
                customer=db_c,
                reference_no=f"PAY-{datetime.now().strftime('%m%d%H%M')}",
                transaction_type='bayad',
                type_label='Bayad (Payment)',
                amount=Decimal(str(amount)),
                running_balance=db_c.running_balance,
                items_summary=f"Payment via {payment_mode}",
                payment_mode=payment_mode,
                notes=notes,
            )
    except Exception:
        pass


def get_sms_message(customer_name, balance, store_name, gcash_number, tone='polite'):
    """Generates localized Tagalog collection reminders."""
    balance_fmt = f"₱{balance:,.2f}"
    if tone == 'firm':
        return (
            f"PAALALA: Magandang araw {customer_name}. Lagpas na po sa due date ang inyong utang na {balance_fmt} "
            f"sa {store_name}. Paki-settle po agad sa tindahan o via GCash ({gcash_number}) para mapanatili ang inyong credit line. Salamat."
        )
    return (
        f"Magandang araw po {customer_name}! Paalala lang po mula sa {store_name}. Ang inyong kasalukuyang utang balance po ay "
        f"{balance_fmt}. Maaari po itong bayaran sa tindahan o via GCash sa {gcash_number}. Maraming salamat po!"
    )
