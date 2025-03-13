from django.contrib import admin
from ..models import ServiceReport

class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'work_order', 'service_date', 'approval_status']
    list_filter = ['service_date', 'approval_status']
    search_fields = ['work_order__id', 'description']
    raw_id_fields = ['work_order']
    readonly_fields = ['created_at', 'updated_at', 'approved_by']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        if obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)
