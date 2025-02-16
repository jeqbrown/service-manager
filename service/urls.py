from django.urls import path
from .views.filter_views import filter_instruments, filter_entitlements

urlpatterns = [
    path('admin/service/instrument/ajax/filter/', filter_instruments, name='filter_instruments'),
    path('admin/service/entitlement/ajax/filter/', filter_entitlements, name='filter_entitlements'),
]
