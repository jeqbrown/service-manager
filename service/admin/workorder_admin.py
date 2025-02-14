from django.contrib import admin
from django import forms
from django.db.models import F, Count, Q
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from ..models.workorder import WorkOrder, ServiceReport
from ..models.agreement import Entitlement
from ..models.instrument import Instrument
from django.contrib.auth.models import User
from ..utils.status_colors import get_status_badge

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'instrument' in kwargs['initial']:
            instrument = Instrument.objects.get(id=kwargs['initial']['instrument'])
            
            # Set instrument field
            self.fields['instrument'].initial = instrument
            self.fields['instrument'].widget.attrs['readonly'] = True
            
            # Set customer field
            self.fields['customer'].initial = instrument.customer
            self.fields['customer'].widget.attrs['readonly'] = True
            
            # Filter entitlements for this instrument that have remaining visits
            self.fields['entitlement'].queryset = Entitlement.objects.filter(
                instrument=instrument,
                is_active=True
            ).annotate(
                completed_workorders=Count('workorders', filter=Q(workorders__status='completed'))
            ).filter(
                total_visits__gt=F('completed_workorders')
            )

        # Order users by name in the assigned_to dropdown
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].queryset = User.objects.filter(
                is_active=True
            ).order_by('first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        
        if status == 'completed':
            # Get the instance if this is an existing work order
            instance = self.instance if self.instance.pk else None
            
            # Check if there are any service reports
            if instance and not instance.service_reports.exists():
                raise forms.ValidationError({
                    'status': 'Cannot complete work order without at least one service report.'
                })
            
            # Check if all service reports are approved
            if instance and not instance.has_approved_reports():
                raise forms.ValidationError({
                    'status': 'Cannot complete work order until all service reports are approved.'
                })

            # Check entitlement availability
            entitlement = cleaned_data.get('entitlement')
            if entitlement:
                if not self.instance.pk or self.instance.status != 'completed':
                    if entitlement.remaining <= 0:
                        raise forms.ValidationError({
                            'status': 'Cannot complete work order. No remaining entitlements available.'
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
    list_display = ('id', 'instrument', 'colored_status', 'assigned_to', 'created_at')
    list_filter = ('status', 'assigned_to', 'instrument__customer', 'created_at')
    search_fields = ('id', 'instrument__serial_number')
    readonly_fields = ('created_at', 'created_by', 'entitlement_info', 'service_reports_detail')
    inlines = [ServiceReportInline]

    def colored_status(self, obj):
        return get_status_badge(obj.status)
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'instrument', 'entitlement', 'created_by', 'assigned_to'
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def entitlement_info(self, obj):
        if obj.entitlement:
            return f"Used: {obj.entitlement.used_visits}/{obj.entitlement.total_visits}"
        return "-"
    entitlement_info.short_description = "Entitlement Usage"

    def service_reports_detail(self, obj):
        reports = obj.service_reports.all().order_by('-service_date')
        if not reports:
            return "No service reports"
        
        html = ['<table style="width: 100%;">']
        html.append('<tr><th>ID</th><th>Date</th><th>Technician</th><th>Status</th><th>Actions</th></tr>')
        
        for report in reports:
            html.append(format_html(
                '<tr>'
                '<td>SR-{}</td>'
                '<td>{}</td>'
                '<td>{}</td>'
                '<td>{}</td>'
                '<td><a href="{}">View Details</a></td>'
                '</tr>',
                report.pk,
                report.service_date,
                report.technician.get_full_name() or report.technician.username,
                report.get_approval_status_display(),
                reverse("admin:service_servicereport_change", args=[report.pk])
            ))
        
        html.append('</table>')
        return format_html(''.join(html))
    service_reports_detail.short_description = "Service Reports Detail"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'customer', 'colored_approval_status')
    list_filter = ('approval_status', 'customer')
    autocomplete_fields = ['work_order']
    readonly_fields = ('approved_by', 'approval_date')

    def colored_approval_status(self, obj):
        return get_status_badge(obj.approval_status)
    colored_approval_status.short_description = 'Approval Status'
    colored_approval_status.admin_order_field = 'approval_status'
