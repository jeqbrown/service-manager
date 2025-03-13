from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from ..models import Instrument, InstrumentType

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'manufacturer']
    list_display = ['name', 'manufacturer']

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'instrument_type', 'customer', 'status_badge']
    list_filter = ['status', 'instrument_type']
    search_fields = ['serial_number', 'location', 'notes']
    autocomplete_fields = ['instrument_type']  # Remove customer temporarily
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'serial_number',
                'instrument_type',
                'customer',
                'status',
                'installation_date'
            )
        }),
        ('Additional Details', {
            'fields': (
                'location',
                'assigned_to',
                'notes'
            )
        }),
        ('System Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'red',
            'maintenance': 'orange',
            'retired': 'gray'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'instrument_type',
            'customer',
            'assigned_to',
            'created_by',
            'updated_by'
        )
