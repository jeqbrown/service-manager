from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import F
from .models import (
    Customer, Contact, InstrumentType, Instrument,
    ServiceAgreement, EntitlementType, Entitlement,
    WorkOrder, ServiceReport
)

# ======================
# Inlines
# ======================

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ('primary_contact', 'name', 'email', 'phone', 'role')
    ordering = ['-primary_contact']

class InstrumentInline(admin.TabularInline):
    model = Instrument
    extra = 0
    fields = ('serial_number', 'instrument_type', 'installation_date', 'work_order_links')
    readonly_fields = ('work_order_links',)

    def work_order_links(self, obj):
        return format_html(
            '<a class="button" href="{}?instrument={}">New WO</a>&nbsp;'
            '<a class="button" href="{}?instrument={}">New SR</a>',
            reverse('admin:service_workorder_add'),
            obj.id,
            reverse('admin:service_servicereport_add'),
            obj.id
        )
    work_order_links.short_description = "Quick Actions"

class EntitlementInline(admin.TabularInline):
    model = Entitlement
    extra = 1
    fields = ('entitlement_type', 'instrument', 'total_visits', 'remaining')
    readonly_fields = ('remaining',)

    def remaining(self, obj):
        return obj.total_visits - obj.used_visits
    remaining.short_description = 'Remaining'

class ServiceAgreementInline(admin.TabularInline):
    model = ServiceAgreement
    extra = 1
    fields = ('edit_link', 'start_date', 'end_date', 'status')
    readonly_fields = ('edit_link',)

    def edit_link(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="{}" target="_blank">Edit Agreement</a>',
                reverse('admin:service_serviceagreement_change', args=[obj.pk])
            )
        return "Save first to edit"
    edit_link.short_description = "Actions"

# ======================
# Model Admins
# ======================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'instrument_count', 'contact_count')
    inlines = [InstrumentInline, ContactInline, ServiceAgreementInline]
    search_fields = ('name', 'website')

    def instrument_count(self, obj):
        return obj.instruments.count()
    instrument_count.short_description = "Instruments"

    def contact_count(self, obj):
        return obj.contacts.count()
    contact_count.short_description = "Contacts"

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'instrument_count')
    search_fields = ('name',)

    def instrument_count(self, obj):
        return obj.instrument_set.count()
    instrument_count.short_description = "Instruments"

@admin.register(EntitlementType)
class EntitlementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'entitlement_count')
    search_fields = ('name',)

    def entitlement_count(self, obj):
        return obj.entitlement_set.count()
    entitlement_count.short_description = "Usage Count"

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'customer', 'instrument_type', 'work_order_actions')
    list_filter = ('customer', 'instrument_type')
    search_fields = ('serial_number', 'instrument_type__name')
    actions = ['create_work_order', 'create_service_report']

    def work_order_actions(self, obj):
        return format_html(
            '<a class="button" href="{}?instrument={}">Create WO</a>&nbsp;'
            '<a class="button" href="{}?instrument={}">Create SR</a>',
            reverse('admin:service_workorder_add'),
            obj.id,
            reverse('admin:service_servicereport_add'),
            obj.id
        )
    work_order_actions.short_description = "Actions"

    def create_work_order(self, request, queryset):
        instrument = queryset.first()
        return redirect(f'{reverse("admin:service_workorder_add")}?instrument={instrument.id}')
    create_work_order.short_description = "Create Work Order"

    def create_service_report(self, request, queryset):
        instrument = queryset.first()
        return redirect(f'{reverse("admin:service_servicereport_add")}?instrument={instrument.id}')
    create_service_report.short_description = "Create Service Report"

@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = ('customer', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    inlines = [EntitlementInline]
    autocomplete_fields = ['customer']

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'instrument' in kwargs['initial']:
            instrument = Instrument.objects.get(id=kwargs['initial']['instrument'])
            self.fields['entitlement'].queryset = Entitlement.objects.filter(
                instrument=instrument,
                is_active=True,
                total_visits__gt=F('used_visits')
            )
            self.fields['instrument'].initial = instrument
            self.fields['instrument'].disabled = True

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    form = WorkOrderForm
    list_display = ('id', 'instrument', 'entitlement', 'status')
    list_filter = ('status', 'instrument__customer')
    search_fields = ('id', 'instrument__serial_number')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only for new objects
            instrument_id = request.GET.get('instrument')
            if instrument_id:
                obj.instrument = Instrument.objects.get(id=instrument_id)
        super().save_model(request, obj, form, change)

@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('work_order', 'customer', 'get_approval_status')
    list_filter = ('customer', 'approval_status')
    autocomplete_fields = ['work_order']
    readonly_fields = ('approved_by', 'approval_date')

    def get_approval_status(self, obj):
        return obj.get_approval_status_display()
    get_approval_status.short_description = 'Approval Status'
    get_approval_status.admin_order_field = 'approval_status'

    def save_model(self, request, obj, form, change):
        if obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }
