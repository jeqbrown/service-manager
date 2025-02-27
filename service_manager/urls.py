"""
URL configuration for service_manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from service.views.landing_page import LandingPageView
from service.admin.site import admin_site  # Import the custom admin site
from django.contrib.auth.views import LogoutView

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),  # Add landing page
    path('admin/', admin_site.urls),  # Use custom admin site
    path('health/', health_check, name='health_check'),
    path('admin/logout/', LogoutView.as_view(next_page='admin:login'), name='admin_logout'),
    path('api/v1/', include('service.api.urls')),  # Include the API URLs
    path('service/', include('service.urls')),  # Include service app URLs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
