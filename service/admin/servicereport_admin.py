from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from ..models.servicereport import ServiceReport
import logging

logger = logging.getLogger(__name__)

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'work_order_link', 'customer', 'approval_status', 'service_date', 'technician')
    list_filter = ('approval_status', 'work_order__customer', 'service_date', 'technician')
    search_fields = ('work_order__instrument__serial_number', 'work_order__customer__name', 'technician__username')
    readonly_fields = ('approval_date', 'approved_by')
    
    def work_order_link(self, obj):
        url = reverse("admin:service_workorder_change", args=[obj.work_order.id])
        return format_html('<a href="{}">{}</a>', url, obj.work_order)
    work_order_link.short_description = 'Work Order'
    work_order_link.admin_order_field = 'work_order'

    def customer(self, obj):
        return obj.work_order.customer

    fieldsets = (
        (None, {
            'fields': ('work_order', 'technician', 'service_date')
        }),
        ('Service Details', {
            'fields': ('findings', 'actions_taken')
        }),
        ('Approval Information', {
            'fields': ('approval_status', 'approval_date', 'approval_notes', 'approved_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)
