from django.contrib import admin
from django import forms
from django.db.models import F, Count, Q
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from ..models.workorder import WorkOrder
from ..models.servicereport import ServiceReport
from ..models.agreement import Entitlement
from ..models.instrument import Instrument
from django.contrib.auth.models import User
from ..utils.status_colors import get_status_badge
from django.core.exceptions import PermissionDenied
from ..forms import ServiceReportForm

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the instrument either from initial data (new WO) or existing instance (edit WO)
        instrument = None
        if 'initial' in kwargs and 'instrument' in kwargs['initial']:
            try:
                instrument = Instrument.objects.get(id=kwargs['initial']['instrument'])
            except Instrument.DoesNotExist:
                pass
        elif self.instance and self.instance.instrument_id:
            instrument = self.instance.instrument

        if instrument:
            # Filter entitlements for this instrument
            self.fields['entitlement'].queryset = (
                Entitlement.objects
                .filter(instrument=instrument)
                .annotate(used_count=Count('workorders'))
                .filter(total__gt=F('used_count'))
            )

    def clean(self):
        cleaned_data = super().clean()
        instrument = cleaned_data.get('instrument')
        entitlement = cleaned_data.get('entitlement')
        status = cleaned_data.get('status')

        if entitlement and entitlement.instrument != instrument:
            raise forms.ValidationError({
                'entitlement': 'Selected entitlement does not belong to this instrument.'
            })

        if not entitlement and status != WorkOrder.STATUS_DRAFT:
            raise forms.ValidationError({
                'status': 'Work Order must remain in Draft status until an entitlement is assigned.'
            })

        return cleaned_data

class ServiceReportInline(admin.TabularInline):
    model = ServiceReport
    extra = 1
    fields = ('service_date', 'technician', 'approval_status', 'view_report')
    readonly_fields = ('view_report',)

    def view_report(self, obj):
        if obj.pk:
            url = reverse('admin:service_servicereport_change', args=[obj.pk])
            return format_html('<a href="{}">View Details</a>', url)
        return "-"
    view_report.short_description = "Details"

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    form = WorkOrderForm
    list_display = ('edit_link', 'instrument', 'description_display', 'colored_status', 'assigned_to_display', 'created_at')
    list_filter = ('status', 'instrument__customer', 'assigned_to')
    search_fields = ('id', 'instrument__serial_number', 'description', 'assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name')
    readonly_fields = ('created_at', 'created_by')
    inlines = [ServiceReportInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def description_display(self, obj):
        """Truncate description if it's too long"""
        if obj.description:
            return (obj.description[:50] + '...') if len(obj.description) > 50 else obj.description
        return "-"
    description_display.short_description = "Description"
    description_display.admin_order_field = 'description'

    def colored_status(self, obj):
        return get_status_badge(obj.get_status_display())
    colored_status.short_description = "Status"
    colored_status.admin_order_field = 'status'
    colored_status.allow_tags = True

    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.get_full_name() or obj.assigned_to.username}"
        return "-"
    assigned_to_display.short_description = "Assigned To"
    assigned_to_display.admin_order_field = 'assigned_to'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and hasattr(obj, 'entitlement') and obj.entitlement:
            # Use the 'remaining' property instead of 'remaining_visits'
            remaining = obj.entitlement.remaining
            # Add remaining visits info to the form
            form.base_fields['entitlement'].help_text = f'Remaining visits: {remaining}'
        return form

    def edit_link(self, obj):
        return format_html(
            '<a href="{}" class="changelink" title="Edit Work Order">'
            '<img src="/static/admin/img/icon-changelink.svg" alt="Edit"> WO-{}</a>',
            reverse('admin:service_workorder_change', args=[obj.pk]),
            obj.pk
        )
    edit_link.short_description = 'WO#'
    edit_link.admin_order_field = 'id'

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_order', 'service_date', 'technician', 'colored_approval_status')
    list_filter = ('approval_status', 'work_order__instrument__customer', 'technician')
    search_fields = ('work_order__id', 'work_order__instrument__serial_number', 
                    'technician__username', 'technician__first_name', 'technician__last_name')
    readonly_fields = ('approval_date', 'approved_by')

    def colored_approval_status(self, obj):
        return get_status_badge(obj.approval_status, obj.get_approval_status_display())
    colored_approval_status.short_description = 'Approval Status'
    colored_approval_status.admin_order_field = 'approval_status'
    colored_approval_status.allow_tags = True

    def save_model(self, request, obj, form, change):
        if obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
            obj.approval_date = timezone.now()
        super().save_model(request, obj, form, change)
