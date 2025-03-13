from django.contrib import admin
from django import forms
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

class EntitlementInlineForm(forms.ModelForm):
    class Meta:
        model = Entitlement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the parent ServiceAgreement instance
        if self.instance:
            parent_obj = self.instance.agreement if self.instance.pk else kwargs.get('initial', {}).get('agreement')
        else:
            parent_obj = kwargs.get('initial', {}).get('agreement')

        # If we're in a formset, try to get the parent object from there
        if hasattr(self, 'parent_instance'):
            parent_obj = self.parent_instance

        if parent_obj and hasattr(parent_obj, 'customer'):
            # Filter instruments by the agreement's customer
            self.fields['instrument'].queryset = Instrument.objects.filter(
                customer=parent_obj.customer
            ).select_related('instrument_type')

class EntitlementInline(admin.TabularInline):
    model = Entitlement
    form = EntitlementInlineForm
    extra = 1
    fields = ('entitlement_type', 'instrument', 'total', 'remaining')
    readonly_fields = ('remaining',)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Pass the parent instance to the form
        formset.form.parent_instance = obj
        return formset

    def remaining(self, obj):
        if obj.pk:
            return obj.remaining
        return "-"
    remaining.short_description = 'Remaining'

# Remove @admin.register decorators
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'po_number', 'start_date', 'end_date', 'status_badge')
    list_filter = ('status', 'customer')
    search_fields = ('customer__name', 'po_number')
    inlines = [EntitlementInline]
    autocomplete_fields = ['customer']
    change_list_template = 'admin/service/serviceagreement/change_list.html'
    readonly_fields = ('service_summary', 'service_history')

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .select_related('customer'))

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

    def status_badge(self, obj):
        """Display the status with color coding."""
        return get_status_badge(obj.status)
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    status_badge.allow_tags = True

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
        """Display summary of services for this agreement."""
        if not obj.customer:
            return "No customer associated with this agreement"

        try:
            # Get entitlements for this agreement
            entitlements = obj.entitlements.all().select_related('entitlement_type')
            
            html = ['<div class="service-summary" style="margin-bottom: 20px;">']
            
            # Agreement details
            html.append('<h3 style="margin-bottom: 10px;">Agreement Details</h3>')
            html.append(f'<p><strong>Status:</strong> {obj.get_status_display()}</p>')
            html.append(f'<p><strong>Valid Period:</strong> {obj.start_date} to {obj.end_date}</p>')
            
            # Entitlements summary
            if entitlements:
                html.append('<h3 style="margin-top: 15px;">Entitlements</h3>')
                html.append('<ul>')
                for ent in entitlements:
                    used = ent.used_count if hasattr(ent, 'used_count') else 0
                    remaining = ent.total - used
                    html.append(
                        f'<li>{ent.entitlement_type.name}: {used}/{ent.total} used '
                        f'({remaining} remaining)</li>'
                    )
                html.append('</ul>')
            else:
                html.append('<p>No entitlements defined for this agreement</p>')
            
            html.append('</div>')
            return format_html(''.join(html))
            
        except Exception as e:
            return format_html(
                '<div style="color: #721c24; background-color: #f8d7da; '
                'padding: 10px; border: 1px solid #f5c6cb;">'
                f'Error generating summary: {str(e)}</div>'
            )

    service_summary.short_description = 'Service Summary'

    def service_history(self, obj):
        """Display service history for the agreement's customer."""
        if not obj.customer:
            return "No customer associated with this agreement"

        work_orders = WorkOrder.objects.filter(
            customer=obj.customer
        ).select_related(
            'customer'
        ).prefetch_related(
            'service_reports',
            'service_reports__created_by'
        ).order_by('-created_at')

        if not work_orders:
            return "No service history available"

        html = ['<div class="service-history">']
        
        for wo in work_orders:
            status_badge = get_status_badge(wo.status)
            
            # Get service reports for this work order
            service_reports = wo.service_reports.all()
            sr_links = []
            for sr in service_reports:
                sr_url = reverse('admin:service_servicereport_change', args=[sr.pk])
                sr_links.append(
                    f'<a href="{sr_url}">'
                    f'Report {sr.pk} by {sr.created_by.get_full_name() or sr.created_by.username}'
                    f'</a>'
                )

            wo_url = reverse('admin:service_workorder_change', args=[wo.pk])
            html.append(
                f'<div class="work-order-entry" style="margin-bottom: 15px;">'
                f'<strong>Work Order:</strong> <a href="{wo_url}">{wo.title}</a> {status_badge}<br>'
                f'<strong>Created:</strong> {wo.created_at.strftime("%Y-%m-%d %H:%M")}<br>'
                f'<strong>Service Reports:</strong> {"<br>".join(sr_links) if sr_links else "None"}'
                f'</div>'
            )

        html.append('</div>')
        return format_html(''.join(html))

    service_history.short_description = 'Service History'

    fieldsets = (
        (None, {
            'fields': ('customer', 'po_number', 'start_date', 'end_date', 'status', 'notes')
        }),
        ('Service Details', {
            'fields': ('service_summary', 'service_history'),
            'classes': ('collapse',)
        }),
    )

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
