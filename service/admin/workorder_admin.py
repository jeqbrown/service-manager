from django.contrib import admin
from django.forms import ModelForm, ModelChoiceField
from django.db.models import F, Count
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.shortcuts import redirect
from ..models.workorder import WorkOrder
from ..models.servicereport import ServiceReport
from ..models.agreement import Entitlement
from ..models.instrument import Instrument
from ..utils.status_colors import get_status_badge

class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'instrument', 'status_badge', 'assigned_to', 'created_at')
    list_filter = ('status', 'customer', 'assigned_to', 'created_at')
    search_fields = ('customer__name', 'instrument__serial_number', 'description')
    readonly_fields = ('created_at',)
    
    def status_badge(self, obj):
        return get_status_badge(obj.status)
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def description_truncated(self, obj):
        """Truncate description to 30 characters"""
        if obj.description and len(obj.description) > 30:
            return f"{obj.description[:30]}..."
        return obj.description or "-"
    description_truncated.short_description = "Description"
    description_truncated.admin_order_field = 'description'

    def colored_status(self, obj):
        return get_status_badge(obj.get_status_display())
    colored_status.short_description = "Status"
    colored_status.admin_order_field = 'status'
    colored_status.allow_tags = True

    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return "-"
    assigned_to_display.short_description = 'Assigned To'
    assigned_to_display.admin_order_field = 'assigned_to__first_name'

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if 'instrument' in request.GET:
            try:
                instrument = Instrument.objects.get(id=request.GET['instrument'])
                initial.update({
                    'customer': instrument.customer.pk,
                    'instrument': instrument.pk,
                    'created_by': request.user.pk,
                })
            except Instrument.DoesNotExist:
                pass
        return initial

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.all().order_by('first_name', 'last_name')
            kwargs["label_from_instance"] = lambda obj: obj.get_full_name() or obj.username
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('js/workorder_admin.js',)

    def edit_link(self, obj):
        return format_html(
            '<a href="{}" class="changelink" title="Edit Work Order">'
            '<img src="/static/admin/img/icon-changelink.svg" alt="Edit"> WO-{}</a>',
            reverse('admin:service_workorder_change', args=[obj.pk]),
            obj.pk
        )
    edit_link.short_description = 'WO#'
    edit_link.admin_order_field = 'id'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'instrument',
            'instrument__customer',
            'assigned_to',
            'created_by'
        )

    def service_report_actions(self, obj):
        """Add buttons to view existing SRs and create new ones"""
        # Get all related service reports
        service_reports = obj.service_reports.all()
        
        # Create the "New SR" button
        new_sr_url = f"{reverse('admin:service_servicereport_add')}?work_order={obj.pk}"
        buttons = [
            f'<a href="{new_sr_url}" class="button" style="margin-right: 5px;" target="_blank">New SR</a>'
        ]
        
        # Add buttons for existing service reports
        for sr in service_reports:
            sr_url = reverse('admin:service_servicereport_change', args=[sr.pk])
            buttons.append(
                f'<a href="{sr_url}" class="button" '
                f'style="margin-right: 5px; background: var(--secondary);" '
                f'target="_blank">SR-{sr.pk}</a>'
            )
        
        return format_html(''.join(buttons))
    service_report_actions.short_description = "Actions"

    def create_service_report(self, request, queryset):
        """Action to create a new service report for selected work orders"""
        if queryset.count() == 1:
            work_order = queryset.first()
            return redirect(f"{reverse('admin:service_servicereport_add')}?work_order={work_order.pk}")
        else:
            self.message_user(request, "Please select only one work order to create a service report.")
    create_service_report.short_description = "Create Service Report"

    def customer_link(self, obj):
        url = reverse("admin:service_customer_change", args=[obj.customer.id])
        return format_html(
            '<a href="{}" onclick="return showRelatedObjectPopup(this);" '
            'data-popup="yes" class="related-widget-wrapper-link">{}</a>', 
            url, obj.customer.name
        )
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'customer'

    def instrument_link(self, obj):
        if obj.instrument:
            url = reverse("admin:service_instrument_change", args=[obj.instrument.id])
            return format_html(
                '<a href="{}" onclick="return showRelatedObjectPopup(this);" '
                'data-popup="yes" class="related-widget-wrapper-link">{}</a>', 
                url, obj.instrument.serial_number
            )
        return "-"
    instrument_link.short_description = 'Instrument'
    instrument_link.admin_order_field = 'instrument'

class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_order', 'service_date', 'created_by_full_name', 'colored_approval_status')
    list_filter = ('approval_status', 'work_order__instrument__customer', 'created_by')
    search_fields = ('work_order__id', 'work_order__instrument__serial_number', 
                    'created_by__username', 'created_by__first_name', 'created_by__last_name')
    readonly_fields = ('approval_date', 'approved_by')

    def created_by_full_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "-"
    created_by_full_name.short_description = 'Created By'
    created_by_full_name.admin_order_field = 'created_by__first_name'

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
