"""
URL patterns for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('api-info/', views.api_info, name='api_info'),
    path('system-status/', views.system_status, name='system_status'),
]