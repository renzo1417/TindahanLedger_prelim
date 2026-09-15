"""
Register feature views for TindaHan Ledger.
Vertical slice: apps.register
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


def register_view(request):
    """Renders the registration screen and creates a new user account."""
    if request.user.is_authenticated:
        return redirect("home:home")

    form_data = {}
    field_errors = {}

    if request.method == "POST":
        store_name = request.POST.get("store_name", "").strip()
        owner_name = request.POST.get("owner_name", "").strip()
        phone = request.POST.get("phone", "").strip() or request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        form_data = {
            "store_name": store_name,
            "owner_name": owner_name,
            "phone": phone,
            "password": password,
            "confirm_password": confirm_password,
        }

        has_errors = False

        if not store_name:
            field_errors["store_name"] = "Store business name is required."
            has_errors = True
        if not owner_name:
            field_errors["owner_name"] = "Owner full name is required."
            has_errors = True
        if not phone:
            field_errors["phone"] = "Store mobile number is required."
            has_errors = True
        if not password:
            field_errors["password"] = "Password is required."
            has_errors = True

        if phone and User.objects.filter(username=phone).exists():
            field_errors["phone"] = "An account with this mobile number already exists."
            has_errors = True

        if password and len(password) < 8:
            field_errors["password"] = "Password must be at least 8 characters long."
            has_errors = True

        if password and confirm_password and password != confirm_password:
            field_errors["confirm_password"] = "Passwords do not match."
            has_errors = True
        elif not confirm_password and password:
            field_errors["confirm_password"] = "Please confirm your password."
            has_errors = True

        if has_errors:
            return render(request, "register/register.html", {
                "form_data": form_data,
                "field_errors": field_errors,
            })

        name_parts = owner_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        request.session["registered_phone"] = phone
        request.session["store_name"] = store_name

        messages.success(request, f'Account for "{store_name}" created successfully! Please sign in to access your ledger.')
        return redirect("login:login")

    return render(request, "register/register.html", {
        "form_data": form_data,
        "field_errors": field_errors,
    })
