from django.contrib.admin.sites import AdminSite
from .dashboard import get_admin_stats

class CustomAdminSite(AdminSite):
    site_header = 'Service Manager Administration'
    site_title = 'Service Manager Admin'
    index_title = 'Service Manager Administration'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(get_admin_stats(request))
        return super().index(request, extra_context=extra_context)

# Create a single instance to be used throughout the application
admin_site = CustomAdminSite(name='custom_admin')
