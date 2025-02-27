from django.contrib import admin
from django.utils.html import format_html
from ..models import ServiceReport

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_order_link', 'customer_name', 'instrument_name', 'service_date', 'approval_status')
    list_filter = ('approval_status', 'service_date')
    search_fields = ('work_order__id', 'work_order__customer__name', 'work_order__instrument__serial_number')
    readonly_fields = ('approval_date', 'approved_by')
    
    fieldsets = (
        (None, {
            'fields': ('work_order', 'service_date')
        }),
        ('Service Details', {
            'fields': ('findings', 'actions_taken')
        }),
        ('Approval Information', {
            'fields': ('approval_status', 'approval_notes', 'approval_date', 'approved_by')
        }),
    )
    
    def work_order_link(self, obj):
        url = f"/admin/service/workorder/{obj.work_order.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.work_order)
    work_order_link.short_description = 'Work Order'
    
    def customer_name(self, obj):
        return obj.customer.name if obj.customer else '-'
    customer_name.short_description = 'Customer'
    
    def instrument_name(self, obj):
        return obj.instrument.model_name if obj.instrument else '-'
    instrument_name.short_description = 'Instrument'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
            
        if 'approval_status' in form.changed_data:
            if obj.approval_status == ServiceReport.STATUS_APPROVED:
                obj.approved_by = request.user
                
        super().save_model(request, obj, form, change)
