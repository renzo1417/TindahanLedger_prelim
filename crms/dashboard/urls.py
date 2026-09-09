"""
URL configuration for the dashboard app.
Serves the home/dashboard screen at the site root.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
]
