from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q, F
from django.contrib.admin import SimpleListFilter
from datetime import datetime, date
from django.utils.timezone import make_aware
from ..models.instrument import InstrumentType, Instrument
from ..models.workorder import WorkOrder, ServiceReport
from ..utils.admin_links import work_order_links
from ..utils.status_colors import get_status_badge
from django.db.models import Prefetch
from django.contrib.auth.models import User

class AssignedToFilter(SimpleListFilter):
    title = 'Assigned To'
    parameter_name = 'assigned_to'

    def lookups(self, request, model_admin):
        # Get all users who are assigned to instruments
        users = (User.objects.filter(assigned_instruments__isnull=False)
                .distinct()
                .order_by('first_name', 'last_name'))
        return [(user.id, user.get_full_name() or user.username) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_to_id=self.value())
        return queryset

class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'instrument_count')
    search_fields = ('name',)

    def instrument_count(self, obj):
        return obj.instrument_set.count()
    instrument_count.short_description = "Instruments"

class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quick_actions', 'customer', 'serial_number', 'installation_date', 'assigned_to_full_name')
    list_filter = ('instrument_type', 'customer', AssignedToFilter)
    search_fields = ('serial_number', 'customer__name')
    autocomplete_fields = ['customer', 'instrument_type', 'assigned_to']
    readonly_fields = ('service_history',)
    actions = ['create_work_order']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer',
            'instrument_type',
            'assigned_to'
        )

    def assigned_to_full_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return "-"
    assigned_to_full_name.short_description = 'Assigned To'
    assigned_to_full_name.admin_order_field = 'assigned_to__first_name'

    def service_history(self, obj):
        if not obj:
            return "No service history available"

        # Get work orders with assigned_to information
        work_orders = WorkOrder.objects.filter(
            instrument=obj
        ).select_related(
            'assigned_to',
            'entitlement__entitlement_type'
        ).prefetch_related(
            Prefetch(
                'service_reports',
                queryset=ServiceReport.objects.select_related('created_by')
            )
        ).order_by('-created_at')

        if not work_orders:
            return "No service history available"

        # Generate HTML table
        html = ['<div class="service-history">']
        
        for wo in work_orders:
            status_badge = get_status_badge(wo.status)
            description = wo.description or "No description"
            if len(description) > 100:
                description = description[:97] + "..."

            # Work Order header
            html.append(f'''
                <div class="work-order-entry" style="margin-bottom: 20px; border: 1px solid #ddd; padding: 10px;">
                    <div style="margin-bottom: 10px;">
                        <strong>WO-{wo.pk}</strong> - {status_badge}
                        <br>
                        <span style="color: #666;">{description}</span>
                    </div>
            ''')

            # Service Reports table
            html.append('''
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 8px; border: 1px solid #ddd;">Date</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Technician</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Status</th>
                        <th style="padding: 8px; border: 1px solid #ddd;">Actions</th>
                    </tr>
            ''')

            # Service Reports for this Work Order
            service_reports = wo.service_reports.all()
            
            for sr in service_reports:
                technician_name = sr.created_by.get_full_name() if sr.created_by else "Unassigned"
                status_badge = get_status_badge(sr.approval_status)
                sr_url = reverse('admin:service_servicereport_change', args=[sr.id])
                
                html.append(f'''
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">{sr.service_date.strftime("%Y-%m-%d")}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{technician_name}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{status_badge}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">
                            <a href="{sr_url}" class="button">View SR</a>
                        </td>
                    </tr>
                ''')

            html.append('</table></div>')

        html.append('</div>')
        return format_html(''.join(html))

    service_history.short_description = 'Service History'

    fieldsets = (
        (None, {
            'fields': ('serial_number', 'instrument_type', 'customer', 'assigned_to', 'installation_date')
        }),
        ('Service History', {
            'fields': ('service_history',),
            'classes': ('collapse',)
        })
    )

    def work_order_actions(self, obj):
        return work_order_links(obj)
    work_order_actions.short_description = "Actions"

    def quick_actions(self, obj):
        """Display quick action button for work order creation"""
        wo_url = reverse('admin:service_workorder_add') + f'?instrument={obj.pk}'
        return format_html(
            '<a href="{}" class="button">New WO</a>',
            wo_url
        )
    quick_actions.short_description = "Actions"

    def create_work_order(self, request, queryset):
        """Bulk action to create a work order for selected instrument"""
        if queryset.count() == 1:
            instrument = queryset.first()
            return redirect(f"{reverse('admin:service_workorder_add')}?instrument={instrument.pk}")
        else:
            self.message_user(request, "Please select only one instrument to create a work order.")
    create_work_order.short_description = "Create Work Order"

class ServiceReportInline(admin.TabularInline):
    model = ServiceReport
    extra = 0
    fields = ('service_date', 'created_by', 'findings', 'actions_taken')
    readonly_fields = ('created_by',)
