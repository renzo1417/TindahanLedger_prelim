from django.urls import path
from . import views

app_name = 'user_settings'

urlpatterns = [
    path('', views.user_settings_view, name='index'),
]
