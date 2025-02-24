"""
URL configuration for service_manager project.
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from service.views.landing_page import LandingPageView
from service.admin.site import admin_site  # Import the custom admin site

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),  # Add landing page
    path('admin/', admin_site.urls),  # Use custom admin site
    path('health/', health_check, name='health_check'),
]
