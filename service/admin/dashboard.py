from django.contrib.admin.sites import AdminSite
from django.db.models import Count, Q
from django.utils import timezone
from ..models.workorder import WorkOrder
from ..models.servicereport import ServiceReport
from ..models.agreement import ServiceAgreement

class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Get open work orders count
        extra_context['open_work_orders'] = WorkOrder.objects.filter(
            status__in=['pending', 'in_progress']
        ).count()
        
        # Get pending reports count
        extra_context['pending_reports'] = ServiceReport.objects.filter(
            approval_status='pending'
        ).count()
        
        # Get active agreements count
        extra_context['active_agreements'] = ServiceAgreement.objects.filter(
            status='active'
        ).count()
        
        return super().index(request, extra_context=extra_context)