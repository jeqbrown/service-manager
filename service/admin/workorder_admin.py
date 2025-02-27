from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from ..models import WorkOrder

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'instrument', 'status', 'created_at', 'assigned_to', 'has_reports_indicator')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'instrument__serial_number', 'description')
    readonly_fields = ('created_by', 'created_at', 'service_reports_list')
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'instrument', 'description', 'status')
        }),
        ('Assignment', {
            'fields': ('entitlement', 'assigned_to')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at')
        }),
        ('Service Reports', {
            'fields': ('service_reports_list',),
        }),
    )
    
    def has_reports_indicator(self, obj):
        if obj.has_reports():
            if obj.has_approved_reports():
                return format_html('<span style="color: green;">✓</span>')
            else:
                return format_html('<span style="color: orange;">⚠</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_reports_indicator.short_description = 'Reports'
    
    def service_reports_list(self, obj):
        reports = obj.service_reports.all().order_by('-service_date')
        if not reports:
            return "No service reports"
            
        html = '<ul>'
        for report in reports:
            url = reverse('admin:service_servicereport_change', args=[report.id])
            status_color = {
                'draft': 'gray',
                'in_progress': 'blue',
                'awaiting': 'orange',
                'approved': 'green',
                'rejected': 'red'
            }.get(report.approval_status, 'black')
            
            html += f'<li><a href="{url}">SR-{report.id}</a> ({report.service_date}) - ' \
                   f'<span style="color: {status_color};">{report.get_approval_status_display()}</span></li>'
        html += '</ul>'
        return format_html(html)
    service_reports_list.short_description = 'Service Reports'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
