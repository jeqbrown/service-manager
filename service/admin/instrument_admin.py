from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q, F
from datetime import datetime, date
from django.utils.timezone import make_aware
from ..models.instrument import InstrumentType, Instrument
from ..models.workorder import WorkOrder, ServiceReport
from ..utils.admin_links import work_order_links
from ..utils.status_colors import get_status_badge

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'instrument_count')
    search_fields = ('name',)

    def instrument_count(self, obj):
        return obj.instrument_set.count()
    instrument_count.short_description = "Instruments"

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'customer', 'instrument_type', 'work_order_actions')
    list_filter = ('customer', 'instrument_type')
    search_fields = ('serial_number', 'instrument_type__name')
    readonly_fields = ('service_history',)

    def service_history(self, obj):
        # Get work orders with assigned_to information
        work_orders = WorkOrder.objects.filter(
            instrument=obj
        ).select_related(
            'assigned_to',
            'entitlement__entitlement_type'
        ).annotate(
            event_date=F('created_at')
        ).values_list(
            'id', 
            'event_date',
            'status',
            'assigned_to__first_name',
            'assigned_to__last_name',
            'entitlement__entitlement_type__name'
        )

        # Get service reports with technician information
        service_reports = ServiceReport.objects.filter(
            work_order__instrument=obj
        ).select_related(
            'technician'
        ).values_list(
            'id',
            'service_date',
            'technician__first_name',
            'technician__last_name',
            'approval_status',
            'work_order_id'
        )

        service_events = []

        # Add work orders
        for wo in work_orders:
            wo_id, event_date, status, first_name, last_name, entitlement_type = wo
            
            # Format assigned_to name
            assigned_to = "Unassigned"
            if first_name or last_name:
                assigned_to = f"{first_name or ''} {last_name or ''}".strip()
            
            service_events.append({
                'date': event_date,
                'type': 'work_order',
                'data': {
                    'id': wo_id,
                    'status': status,
                    'assigned_to': assigned_to,
                    'entitlement_type': entitlement_type or "No entitlement"
                }
            })

        # Add service reports
        for sr in service_reports:
            sr_id, service_date, first_name, last_name, status, wo_id = sr
            
            # Format technician name
            technician_name = "Unassigned"
            if first_name or last_name:
                technician_name = f"{first_name or ''} {last_name or ''}".strip()
            
            if isinstance(service_date, date):
                service_date = make_aware(datetime.combine(service_date, datetime.min.time()))
            
            service_events.append({
                'date': service_date,
                'type': 'service_report',
                'data': {
                    'id': sr_id,
                    'technician_name': technician_name,
                    'status': status,
                    'work_order_id': wo_id
                }
            })

        # Sort all events by date, most recent first
        service_events.sort(key=lambda x: x['date'], reverse=True)

        if not service_events:
            return "No service history available"

        # Generate HTML table
        html = ['<table class="service-history">']
        html.append('''
            <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Details</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        ''')

        for event in service_events:
            if event['type'] == 'work_order':
                wo = event['data']
                status_badge = get_status_badge(wo['status'])
                
                html.append(format_html('''
                    <tr>
                        <td>{}</td>
                        <td>Work Order</td>
                        <td>WO-{} ({})</td>
                        <td>{}</td>
                        <td><a href="{}" class="button">View WO</a></td>
                    </tr>
                ''',
                    event['date'].strftime("%Y-%m-%d"),
                    wo['id'],
                    wo['entitlement_type'],
                    status_badge,
                    reverse('admin:service_workorder_change', args=[wo['id']])
                ))
            
            else:  # service_report
                sr = event['data']
                status_badge = get_status_badge(sr['status'])
                
                html.append(format_html('''
                    <tr>
                        <td>{}</td>
                        <td>Service Report</td>
                        <td>SR-{}</td>
                        <td>{}</td>
                        <td><a href="{}" class="button">View SR</a></td>
                    </tr>
                ''',
                    event['date'].strftime("%Y-%m-%d"),
                    sr['id'],
                    status_badge,
                    reverse('admin:service_servicereport_change', args=[sr['id']])
                ))

        html.append('</table>')
        return format_html(''.join(html))
    
    service_history.short_description = 'Service History'

    fieldsets = (
        (None, {
            'fields': ('serial_number', 'customer', 'instrument_type', 'installation_date')
        }),
        ('Service History', {
            'fields': ('service_history',),
        }),
    )

    def work_order_actions(self, obj):
        return work_order_links(obj)
    work_order_actions.short_description = "Actions"
