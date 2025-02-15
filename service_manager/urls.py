"""
URL configuration for service_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from service.views import LandingPageView
from service.admin.dashboard import CustomAdminSite
from django.contrib import admin
from service.admin.user_admin import UserAdmin
from django.contrib.auth import get_user_model

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Copy all registered models from the default admin site
for model, model_admin in admin.site._registry.items():
    admin_site.register(model, model_admin.__class__)

# Unregister and register the User model with custom admin
admin_site.unregister(get_user_model())
admin_site.register(get_user_model(), UserAdmin)

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('admin/', admin_site.urls),
]
