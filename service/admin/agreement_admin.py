from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.contrib import messages
from django.shortcuts import redirect
from django.core.management import call_command
from django.db.models import Count, Q
from django.template.response import TemplateResponse
from ..models.agreement import ServiceAgreement, EntitlementType, Entitlement
from ..models.instrument import Instrument
from ..utils.status_colors import get_status_badge
from ..models.workorder import WorkOrder
from ..models.servicereport import ServiceReport

class EntitlementInline(admin.TabularInline):
    model = Entitlement
    extra = 1
    fields = ('entitlement_type', 'instrument', 'total', 'remaining')
    readonly_fields = ('remaining',)
    autocomplete_fields = ['instrument']

    def remaining(self, obj):
        if not obj or not obj.pk:
            return 0
        return obj.remaining
    remaining.short_description = 'Remaining'

@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'start_date', 'end_date', 'colored_status', 'entitlements_summary')
    list_filter = ('status', 'start_date', 'customer')
    search_fields = ('customer__name',)
    inlines = [EntitlementInline]
    autocomplete_fields = ['customer']
    change_list_template = 'admin/service/serviceagreement/change_list.html'
    readonly_fields = ('service_summary',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer').prefetch_related(
            'entitlements',
            'entitlements__workorders',
            'entitlements__entitlement_type'
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['update_status_button'] = {
            'url': 'update_sa_statuses/',
            'label': 'Update SA Statuses',
            'class': 'refresh-button'
        }
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-statuses/', 
                 self.admin_site.admin_view(self.update_statuses), 
                 name='service_agreement_update_statuses'),
            path('update_sa_statuses/',
                 self.admin_site.admin_view(self.update_sa_statuses),
                 name='service_serviceagreement_update_statuses'),
        ]
        return custom_urls + urls

    def update_statuses(self, request):
        try:
            call_command('update_agreement_statuses')
            self.message_user(request, 
                            "Successfully updated agreement statuses.", 
                            messages.SUCCESS)
        except Exception as e:
            self.message_user(request,
                            f"Error updating agreement statuses: {str(e)}", 
                            messages.ERROR)
        
        return redirect('..')

    def update_sa_statuses(self, request):
        try:
            call_command('update_agreement_statuses')
            self.message_user(request, 
                            "Successfully updated agreement statuses.", 
                            messages.SUCCESS)
        except Exception as e:
            self.message_user(request,
                            f"Error updating agreement statuses: {str(e)}", 
                            messages.ERROR)
        
        return redirect('..')

    def colored_status(self, obj):
        """Display the status with color coding."""
        return get_status_badge(obj.status)
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'
    colored_status.allow_tags = True

    def entitlements_summary(self, obj):
        entitlements = obj.entitlements.all()
        if not entitlements:
            return '-'
        
        summary = []
        for ent in entitlements:
            completed_count = ent.workorders.filter(status='completed').count()
            summary.append(
                format_html(
                    '<div style="margin-bottom: 5px;">'
                    '<strong>{}</strong>: {}/{} '
                    '<span style="color: {};">({} remaining)</span>'
                    '</div>',
                    ent.entitlement_type.name,
                    completed_count,
                    ent.total,
                    '#28a745' if (ent.total - completed_count) > 0 else '#dc3545',
                    ent.total - completed_count
                )
            )
        return format_html("".join(summary))
    entitlements_summary.short_description = 'Entitlements'

    update_sa_statuses.short_description = 'Update SA Statuses'
    # Add custom attributes for styling
    update_sa_statuses.allow_tags = True
    update_sa_statuses.css_class = 'refresh-button'

    def service_summary(self, obj):
        """Display summary of Work Orders and Service Reports."""
        html = ['<div class="service-summary">']
        
        # Work Orders Summary
        work_orders = WorkOrder.objects.filter(
            entitlement__agreement=obj
        ).select_related('assigned_to', 'instrument')
        
        html.append('<div class="summary-section"><h3>Work Orders</h3>')
        html.append('<table style="width: 100%; border-collapse: collapse;">')
        html.append('''
            <tr style="background: #f5f5f5;">
                <th style="padding: 8px; border: 1px solid #ddd;">WO #</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Status</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Instrument</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Assigned To</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Created</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Actions</th>
            </tr>
        ''')

        for wo in work_orders:
            status_colors = {
                'open': '#ffc107',      # yellow
                'in_progress': '#17a2b8',  # blue
                'completed': '#28a745',    # green
                'cancelled': '#dc3545'     # red
            }
            status_color = status_colors.get(wo.status, '#6c757d')
            
            html.append(format_html('''
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; border: 1px solid #ddd;">WO-{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">
                            {}
                        </span>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <a href="{}" class="button">View</a>
                    </td>
                </tr>
            ''',
                wo.id,
                status_color,
                wo.get_status_display(),
                wo.instrument,
                wo.assigned_to.get_full_name() if wo.assigned_to else '-',
                wo.created_at.strftime('%Y-%m-%d'),
                reverse('admin:service_workorder_change', args=[wo.id])
            ))
        
        html.append('</table></div>')

        # Service Reports Summary
        service_reports = ServiceReport.objects.filter(
            work_order__entitlement__agreement=obj
        ).select_related('work_order', 'technician')
        
        html.append('<div class="summary-section"><h3>Service Reports</h3>')
        html.append('<table style="width: 100%; border-collapse: collapse;">')
        html.append('''
            <tr style="background: #f5f5f5;">
                <th style="padding: 8px; border: 1px solid #ddd;">SR #</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Status</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Work Order</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Technician</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Date</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Actions</th>
            </tr>
        ''')

        for sr in service_reports:
            status_colors = {
                'pending': '#ffc107',    # yellow
                'approved': '#28a745',    # green
                'rejected': '#dc3545'     # red
            }
            status_color = status_colors.get(sr.approval_status, '#6c757d')
            
            html.append(format_html('''
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 8px; border: 1px solid #ddd;">SR-{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">
                            {}
                        </span>
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">WO-{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">
                        <a href="{}" class="button">View</a>
                    </td>
                </tr>
            ''',
                sr.id,
                status_color,
                sr.get_approval_status_display(),
                sr.work_order.id,
                sr.technician.get_full_name() if sr.technician else '-',
                sr.service_date.strftime('%Y-%m-%d'),
                reverse('admin:service_servicereport_change', args=[sr.id])
            ))

        html.append('</table></div>')
        html.append('</div>')
        
        return format_html(''.join(html))
    
    service_summary.short_description = 'Service Summary'

    fieldsets = (
        (None, {
            'fields': ('customer', 'start_date', 'end_date', 'status')
        }),
        ('Service Summary', {
            'fields': ('service_summary',),
        }),
    )

@admin.register(EntitlementType)
class EntitlementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'entitlement_count')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            entitlement_count=Count('entitlement')
        )

    def entitlement_count(self, obj):
        return getattr(obj, 'entitlement_count', obj.entitlement_set.count())
    entitlement_count.short_description = "Usage Count"
    entitlement_count.admin_order_field = 'entitlement_count'

@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('entitlement_type', 'agreement', 'instrument', 'total', 'get_used', 'get_remaining')
    list_filter = ('entitlement_type', 'agreement', 'instrument')
    search_fields = ('entitlement_type__name', 'agreement__customer__name', 'instrument__serial_number')
    readonly_fields = ('get_used', 'get_remaining')
    autocomplete_fields = ['agreement', 'instrument']

    def get_used(self, obj):
        return obj.used
    get_used.short_description = 'Used'

    def get_remaining(self, obj):
        return obj.remaining
    get_remaining.short_description = 'Remaining'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'agreement',
            'entitlement_type',
            'instrument'
        ).prefetch_related('workorders')
