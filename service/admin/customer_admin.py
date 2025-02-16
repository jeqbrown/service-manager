import logging
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
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
    fields = ('primary_contact', 'name', 'email', 'phone', 'role')
    ordering = ['-primary_contact']

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

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'agreement_status', 'instrument_count', 'contact_count', 'recent_service')
    search_fields = ('name', 'website', 'address')
    list_filter = [
        AgreementStatusFilter,
        InstrumentCountFilter,
    ]
    readonly_fields = ('service_overview',)
    inlines = [ContactInline, InstrumentInline, ServiceAgreementInline]

    def get_list_filter(self, request):
        """Explicitly define allowed filters"""
        return self.list_filter

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_instruments=Count('instruments', distinct=True),
            total_contacts=Count('contacts', distinct=True),
            latest_workorder=models.Max('instruments__workorders__created_at')
        ).select_related()

    def recent_service(self, obj):
        if obj.latest_workorder:
            return format_html(
                '<span style="color: {};">{}</span>',
                '#28a745' if obj.latest_workorder else '#dc3545',
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

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'website')
        }),
        ('Service Information', {
            'fields': ('service_overview',),
            'classes': ('wide',)
        }),
    )

    def service_overview(self, obj):
        logger.info(f"=== Starting service_overview for customer: {obj.name if obj else 'None'} ===")
        if not obj:
            return "Save the customer first to see service overview."
            
        try:
            html = [
                '<div style="margin-top: 20px;">',
                '<h2 style="background: #79aec8; color: white; padding: 8px 12px;">Service Overview</h2>'
            ]

            # Get agreements count and related data
            agreements = obj.agreements.all().prefetch_related(
                'entitlements', 
                'entitlements__entitlement_type', 
                'entitlements__instrument'
            )
            agreements_count = len(agreements)
            logger.info(f"Found {agreements_count} agreements")
            
            # Recent Work Orders section
            recent_work_orders = WorkOrder.objects.filter(
                customer=obj
            ).select_related('instrument').prefetch_related('service_reports').order_by('-created_at')[:5]

            html.append('<div style="padding: 20px;">')
            
            # Work Orders Quick View
            html.extend([
                '<div style="margin-bottom: 20px;">',
                '<h3 style="color: #666;">Recent Work Orders</h3>',
                '<table style="width: 100%; border-collapse: collapse;">',
                '<thead>',
                '<tr style="background-color: #f5f5f5;">',
                '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">WO #</th>',
                '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Status</th>',
                '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Instrument</th>',
                '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Description</th>',
                '<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Actions</th>',
                '</tr>',
                '</thead>',
                '<tbody>'
            ])

            for wo in recent_work_orders:
                status_badge = get_status_badge(wo.status)
                wo_url = reverse('admin:service_workorder_change', args=[wo.pk])
                new_sr_url = reverse('admin:service_servicereport_add')
                
                # Get related service reports
                service_reports = wo.service_reports.all()
                sr_links = []
                for sr in service_reports:
                    sr_url = reverse('admin:service_servicereport_change', args=[sr.pk])
                    sr_links.append(
                        f'<a href="{sr_url}" class="button" '
                        f'style="margin-right: 5px; font-size: 0.8em;">SR-{sr.pk}</a>'
                    )
                
                sr_html = ''.join(sr_links) if sr_links else ''
                
                # Truncate description if it's too long
                description = wo.description or "-"
                if len(description) > 50:
                    description = description[:47] + "..."
                
                html.append(
                    f'<tr style="border: 1px solid #ddd;">'
                    f'<td style="padding: 8px;">WO-{wo.pk}</td>'
                    f'<td style="padding: 8px;">{status_badge}</td>'
                    f'<td style="padding: 8px;">{wo.instrument}</td>'
                    f'<td style="padding: 8px;">{description}</td>'
                    f'<td style="padding: 8px;">'
                    f'<a href="{wo_url}" class="button" style="margin-right: 5px;" target="_blank">View WO</a>'
                    f'<a href="{new_sr_url}?work_order={wo.pk}" class="button" style="margin-right: 5px;" target="_blank">New SR</a>'
                    f'{sr_html}'
                    f'</td>'
                    f'</tr>'
                )

            html.extend([
                '</tbody>',
                '</table>',
                '</div>'
            ])

            # Service Agreements section
            if agreements_count == 0:
                html.append('<p style="padding: 20px;">No service agreements found for this customer.</p>')
            else:
                html.append(f'<p><strong>Total Agreements:</strong> {agreements_count}</p>')
                
                for agreement in agreements:
                    status_badge = get_status_badge(agreement.status)
                    agreement_url = reverse('admin:service_serviceagreement_change', args=[agreement.pk])
                    
                    html.extend([
                        '<div style="margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 4px;">',
                        f'<h3 style="margin: 0 0 10px 0;">'
                        f'<a href="{agreement_url}" style="text-decoration: none;">Agreement #{agreement.id}</a></h3>',
                        f'<p><strong>Status:</strong> {status_badge}</p>',
                        f'<p><strong>Period:</strong> {agreement.start_date} to {agreement.end_date}</p>',
                    ])

                    # Add entitlements section
                    entitlements = agreement.entitlements.all()
                    if entitlements:
                        html.append('<div style="margin-top: 10px;">')
                        html.append('<h4 style="margin: 5px 0;">Entitlements:</h4>')
                        html.append('<ul style="list-style-type: none; padding-left: 0;">')
                        for ent in entitlements:
                            remaining = ent.remaining
                            used = ent.used
                            html.append(
                                f'<li style="margin: 5px 0;">'
                                f'• {ent.entitlement_type.name} ({ent.instrument}): '
                                f'<strong>{remaining}</strong> remaining '
                                f'(<span style="color: #666;">{used}/{ent.total} used</span>)'
                                f'</li>'
                            )
                        html.append('</ul>')
                        html.append('</div>')

                    html.append('</div>')
            
            html.append('</div>')
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
