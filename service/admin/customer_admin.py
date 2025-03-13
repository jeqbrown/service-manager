import logging
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q, OuterRef, Subquery
from django.db import models
from django import forms
from ..models import (
    Customer, 
    Contact, 
    Instrument, 
    ServiceAgreement, 
    ServiceReport,
    WorkOrder
)
from ..utils.status_colors import get_status_badge

logger = logging.getLogger(__name__)

class AgreementStatusFilter(admin.SimpleListFilter):
    title = 'Agreement Status'
    parameter_name = 'agreement_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active Agreement'),
            ('draft', 'Draft Agreement'),
            ('expired', 'Expired Agreement'),
            ('none', 'No Agreement'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(agreements__status='active').distinct()
        elif self.value() == 'draft':
            return queryset.filter(agreements__status='draft').distinct()
        elif self.value() == 'expired':
            return queryset.filter(agreements__status='expired').distinct()
        elif self.value() == 'none':
            return queryset.filter(agreements__isnull=True)
        return queryset

class InstrumentCountFilter(admin.SimpleListFilter):
    title = 'Instrument Count'
    parameter_name = 'instrument_count'

    def lookups(self, request, model_admin):
        return (
            ('0', 'No Instruments'),
            ('1-5', '1-5 Instruments'),
            ('6-10', '6-10 Instruments'),
            ('10+', 'More than 10'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(total_instruments=Count('instruments'))
        
        if self.value() == '0':
            return queryset.filter(total_instruments=0)
        elif self.value() == '1-5':
            return queryset.filter(total_instruments__gte=1, total_instruments__lte=5)
        elif self.value() == '6-10':
            return queryset.filter(total_instruments__gte=6, total_instruments__lte=10)
        elif self.value() == '10+':
            return queryset.filter(total_instruments__gt=10)
        return queryset

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ('is_primary', 'name', 'email', 'phone')
    ordering = ['-is_primary']

class InstrumentInline(admin.TabularInline):
    model = Instrument
    extra = 0
    fields = ('serial_number', 'instrument_type', 'installation_date', 'quick_actions')
    readonly_fields = ('quick_actions',)

    def quick_actions(self, obj):
        if obj.pk:  # Only show actions for saved instruments
            wo_url = reverse('admin:service_workorder_add') + f'?instrument={obj.pk}'
            sr_url = reverse('admin:service_servicereport_add') + f'?instrument={obj.pk}'
            return format_html(
                '<a href="{}" class="button" style="margin-right: 5px;">New WO</a>'
                '<a href="{}" class="button">New SR</a>',
                wo_url,
                sr_url
            )
        return ""
    quick_actions.short_description = "Actions"

class ServiceAgreementInline(admin.TabularInline):
    model = ServiceAgreement
    extra = 0
    fields = ('start_date', 'end_date', 'status', 'actions')
    readonly_fields = ('status', 'actions')

    def actions(self, obj):
        if obj.pk:  # Only show actions for saved agreements
            view_url = reverse('admin:service_serviceagreement_change', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button">View Details</a>',
                view_url
            )
        return ""
    actions.short_description = "Actions"

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'agreement_status', 'instrument_count', 'contact_count', 'recent_service')
    search_fields = ('name', 'website', 'address')
    list_filter = [
        AgreementStatusFilter,
        InstrumentCountFilter,
    ]
    readonly_fields = ('service_overview', 'created_by', 'updated_by', 'created_at', 'updated_at')
    inlines = [ContactInline, InstrumentInline, ServiceAgreementInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'website')
        }),
        ('Service Information', {
            'fields': ('service_overview',),
            'classes': ('wide',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # If creating new object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(
                    total_instruments=Count('instruments', distinct=True),
                    total_contacts=Count('contacts', distinct=True),
                    latest_workorder=Subquery(
                        WorkOrder.objects.filter(
                            customer=OuterRef('pk')
                        ).order_by('-created_at')
                        .values('created_at')[:1]
                    )
                )
                .select_related())

    def recent_service(self, obj):
        if obj.latest_workorder:
            return format_html(
                '<span style="color: {};">{}</span>',
                '#28a745',
                obj.latest_workorder.strftime('%Y-%m-%d')
            )
        return format_html(
            '<span style="color: #dc3545;">No service history</span>'
        )
    recent_service.short_description = "Last Service"
    recent_service.admin_order_field = 'latest_workorder'

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4})},
    }

    def service_overview(self, obj):
        logger.info(f"=== Starting service_overview for customer: {obj.name if obj else 'None'} ===")
        if not obj:
            return "Save the customer first to see service overview."
            
        try:
            html = [
                '<div style="margin-top: 20px;">',
                '<h2 style="background: #79aec8; color: white; padding: 8px 12px;">Service Overview</h2>'
            ]

            # Recent Work Orders
            recent_work_orders = (WorkOrder.objects
                                .filter(customer=obj)
                                .select_related('customer')
                                .order_by('-created_at')[:5])

            if recent_work_orders:
                html.append('<h3>Recent Work Orders</h3>')
                html.append('<ul>')
                for wo in recent_work_orders:
                    html.append(
                        f'<li>{wo.created_at.strftime("%Y-%m-%d")} - {wo.title} '
                        f'({wo.get_status_display()})</li>'
                    )
                html.append('</ul>')
            else:
                html.append('<p>No recent work orders found.</p>')

            # Active Service Agreements
            active_agreements = (ServiceAgreement.objects
                               .filter(customer=obj, status='active')
                               .select_related('customer')
                               .order_by('-created_at'))

            if active_agreements:
                html.append('<h3>Active Service Agreements</h3>')
                html.append('<ul>')
                for agreement in active_agreements:
                    html.append(
                        f'<li>{agreement.created_at.strftime("%Y-%m-%d")} - '
                        f'Valid until: {agreement.end_date}</li>'
                    )
                html.append('</ul>')
            else:
                html.append('<p>No active service agreements found.</p>')

            # Instrument Count
            instrument_count = obj.instruments.count()
            html.append(f'<h3>Equipment Summary</h3>')
            html.append(f'<p>Total Instruments: {instrument_count}</p>')

            html.append('</div>')
            return format_html(''.join(html))

        except Exception as e:
            logger.exception("Error in service_overview")
            return format_html(
                '<div style="color: #721c24; background-color: #f8d7da; padding: 10px; border: 1px solid #f5c6cb;">'
                f'Error loading service overview: {str(e)}'
                '</div>'
            )
    service_overview.short_description = 'Service Overview'  # Updated description

    def agreement_status(self, obj):
        active_agreement = obj.agreements.filter(status='active').first()
        if active_agreement:
            return get_status_badge('active', 'Active')
        return get_status_badge('expired', 'No Active Agreement')
    agreement_status.short_description = 'Agreement Status'

    def instrument_count(self, obj):
        return obj.total_instruments
    instrument_count.short_description = "Instruments"
    instrument_count.admin_order_field = 'total_instruments'

    def contact_count(self, obj):
        return obj.total_contacts
    contact_count.short_description = "Contacts"
    contact_count.admin_order_field = 'total_contacts'

    def get_search_results(self, request, queryset, search_term):
        """Enable autocomplete search."""
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        return queryset, may_have_duplicates
