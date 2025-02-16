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
            'recent': ServiceReport.objects.filter(service_date__gte=thirty_days_ago).count(),
            'approved': ServiceReport.objects.filter(approval_status='approved').count(),
            'rejected': ServiceReport.objects.filter(approval_status='rejected').count()
        },
        'agreements': {
            'active': ServiceAgreement.objects.filter(status='active').count(),
            'expiring_soon': ServiceAgreement.objects.filter(
                status='active',
                end_date__lte=today + timedelta(days=30)
            ).count(),
            'expired': ServiceAgreement.objects.filter(
                status='active',
                end_date__lt=today
            ).count()
        },
        'recent_work_orders': WorkOrder.objects.select_related(
            'customer', 'assigned_to', 'instrument'
        ).order_by('-created_at')[:5],
        'recent_reports': ServiceReport.objects.select_related(
            'work_order', 'created_by'
        ).order_by('-service_date')[:5],
        'total_customers': Customer.objects.count(),
        'total_instruments': Instrument.objects.count(),
    }
