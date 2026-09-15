"""
Login feature views for TindaHan Ledger.
Vertical slice: apps.login
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    """Renders the login screen and processes authentication."""
    if request.user.is_authenticated:
        return redirect("home:home")

    prefilled_identifier = request.session.pop("registered_phone", "")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip() or request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        prefilled_identifier = identifier

        # Authenticate by username
        user = authenticate(request, username=identifier, password=password)

        if user is None:
            # Try by email
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            if "store_name" not in request.session:
                request.session["store_name"] = f"{user.first_name or 'My'}'s Tindahan"
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next", "")
            return redirect(next_url if next_url else "home:home")
        else:
            messages.error(request, "Invalid credentials. Please check your mobile/email and password.")

    return render(request, "login/login.html", {
        "prefilled_identifier": prefilled_identifier,
    })


def logout_view(request):
    """Logs the user out and redirects to the login page."""
    logout(request)
    return redirect("login:login")
