"""
URL configuration for service_manager project.
"""
from django.urls import path, include
from django.contrib import admin
from service.views import LandingPageView, health_check
from service.admin.site import admin_site

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('admin/', admin_site.urls),
    path('', include('service.urls')),  # Include the service app URLs
    path('health/', health_check, name='health_check'),
]
