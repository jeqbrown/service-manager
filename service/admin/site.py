from django.contrib.admin import AdminSite
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from ..models import WorkOrder, ServiceReport

class ServiceManagerAdminSite(AdminSite):
    site_header = 'Service Manager Administration'
    site_title = 'Service Manager Admin'
    index_title = 'Service Manager Administration'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['stats'] = self.get_admin_stats(request)
        return super().index(request, extra_context)

    def get_admin_stats(self, request):
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        
        return {
            'work_orders': WorkOrder.objects.aggregate(
                open=Count('id', filter=Q(status='open')),
                in_progress=Count('id', filter=Q(status='in_progress')),
                recent=Count('id', filter=Q(created_at__gte=thirty_days_ago)),
                total=Count('id')
            ),
            'service_reports': ServiceReport.objects.aggregate(
                total=Count('id')
            )
        }

admin_site = ServiceManagerAdminSite(name='service_manager_admin')
