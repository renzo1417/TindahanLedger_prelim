"""
URL routes for the Inventory app.
"""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list_view, name='inventory_list'),
    path('register/', views.product_create_view, name='product_create'),
    path('<int:product_id>/', views.product_detail_view, name='product_detail'),
]
