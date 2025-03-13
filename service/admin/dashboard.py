from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from ..models.workorder import WorkOrder
from ..models.servicereport import ServiceReport
from ..models.agreement import ServiceAgreement
from ..models.customer import Customer
from ..models.instrument import Instrument

# Move the dashboard functionality to the CustomAdminSite class in site.py
def get_admin_stats(request):
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    return {
        'work_orders': {
            'open': WorkOrder.objects.filter(status='open').count(),
            'in_progress': WorkOrder.objects.filter(status='in_progress').count(),
            'recent': WorkOrder.objects.filter(created_at__gte=thirty_days_ago).count(),
            'total': WorkOrder.objects.count()
        },
        'service_reports': {
            'pending': ServiceReport.objects.filter(approval_status='pending').count(),
            'approved': ServiceReport.objects.filter(approval_status='approved').count(),
            'rejected': ServiceReport.objects.filter(approval_status='rejected').count(),
            'total': ServiceReport.objects.count()
        }
    }
