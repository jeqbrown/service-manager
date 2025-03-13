from django.contrib import admin
from ..models import WorkOrder

class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name', 'description']
    raw_id_fields = ['customer']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
