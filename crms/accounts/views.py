"""
Views for the accounts app.
Handles user login, registration, and logout.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    """Renders the login screen and processes authentication."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    prefilled_identifier = request.session.pop('registered_phone', '')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')
        prefilled_identifier = identifier

        # Try to authenticate by username or email
        user = authenticate(request, username=identifier, password=password)

        if user is None:
            # Try finding user by email
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            if 'store_name' not in request.session:
                request.session['store_name'] = f"{user.first_name or 'My'}'s Tindahan"
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials. Please check your mobile/email and password.')

    return render(request, 'auth/login.html', {
        'prefilled_identifier': prefilled_identifier,
    })


def register_view(request):
    """Renders the registration screen and creates a new user account."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    # Preserved form values and field-level errors for re-rendering
    form_data = {}
    field_errors = {}

    if request.method == 'POST':
        store_name = request.POST.get('store_name', '').strip()
        owner_name = request.POST.get('owner_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Preserve values so user doesn't re-type on error
        form_data = {
            'store_name': store_name,
            'owner_name': owner_name,
            'phone': phone,
            'password': password,
            'confirm_password': confirm_password,
        }

        has_errors = False

        # Validate required fields individually
        if not store_name:
            field_errors['store_name'] = 'Store business name is required.'
            has_errors = True
        if not owner_name:
            field_errors['owner_name'] = 'Owner full name is required.'
            has_errors = True
        if not phone:
            field_errors['phone'] = 'Store mobile number is required.'
            has_errors = True
        if not password:
            field_errors['password'] = 'Password is required.'
            has_errors = True

        # Check if username (phone) already exists
        if phone and User.objects.filter(username=phone).exists():
            field_errors['phone'] = 'An account with this mobile number already exists.'
            has_errors = True

        # Check password length
        if password and len(password) < 8:
            field_errors['password'] = 'Password must be at least 8 characters long.'
            has_errors = True

        # Check confirm password match
        if password and confirm_password and password != confirm_password:
            field_errors['confirm_password'] = 'Passwords do not match.'
            has_errors = True
        elif not confirm_password and password:
            field_errors['confirm_password'] = 'Please confirm your password.'
            has_errors = True

        if has_errors:
            return render(request, 'auth/register.html', {
                'form_data': form_data,
                'field_errors': field_errors,
            })

        # Create the user
        # Split owner_name into first/last name
        name_parts = owner_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Save store name mapping for session
        request.session['registered_phone'] = phone
        request.session['store_name'] = store_name

        messages.success(request, f'Account for "{store_name}" created successfully! Please sign in to access your ledger.')
        return redirect('accounts:login')

    return render(request, 'auth/register.html', {
        'form_data': form_data,
        'field_errors': field_errors,
    })


def logout_view(request):
    """Logs the user out and redirects to the login page without notification."""
    logout(request)
    return redirect('accounts:login')
