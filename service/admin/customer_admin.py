from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.urls import reverse
from ..models.customer import Customer, Contact
from ..models.agreement import ServiceAgreement
from ..models.instrument import Instrument
from ..utils.admin_links import work_order_links

class InstrumentInline(admin.TabularInline):
    model = Instrument
    extra = 0
    fields = ('serial_number', 'instrument_type', 'installation_date', 'work_order_actions')
    readonly_fields = ('work_order_actions',)

    def work_order_actions(self, obj):
        if obj.pk:  # Only show actions if instrument is saved
            return work_order_links(obj)
        return "-"
    work_order_actions.short_description = "Quick Actions"

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ('primary_contact', 'name', 'email', 'phone', 'role')
    ordering = ['-primary_contact']

class ServiceAgreementInline(admin.TabularInline):
    model = ServiceAgreement
    extra = 1
    fields = ('agreement_link', 'start_date', 'end_date', 'status')
    readonly_fields = ('agreement_link',)

    def agreement_link(self, obj):
        if obj.pk:  # Only show link if agreement is saved
            url = reverse('admin:service_serviceagreement_change', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button">SA-{}</a>',
                url,
                obj.pk
            )
        return "-"
    agreement_link.short_description = "Agreement"

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'agreement_status', 'instrument_count', 'contact_count')
    inlines = [InstrumentInline, ContactInline, ServiceAgreementInline]
    search_fields = ('name', 'website')
    readonly_fields = ('entitlements_overview',)

    def entitlements_overview(self, obj):
        agreements = obj.agreements.all()
        if not agreements:
            return "No service agreements"
        
        summary = []
        for agreement in agreements:
            entitlements = agreement.entitlements.all()
            if not entitlements:
                continue
                
            summary.append(
                format_html(
                    '<div style="margin-bottom: 20px;">'
                    '<h3>Agreement SA-{} ({} to {})</h3>',
                    agreement.pk,
                    agreement.start_date,
                    agreement.end_date
                )
            )
            
            for ent in entitlements:
                work_orders = ent.workorders.all().order_by('-created_at')
                wo_table = []
                
                if work_orders:
                    wo_table.append('<table style="margin-left: 20px; margin-bottom: 10px;">')
                    wo_table.append('<tr><th>Work Order</th><th>Status</th><th>Created</th><th>Service Reports</th></tr>')
                    
                    for wo in work_orders:
                        sr_links = format_html_join(
                            ' ',
                            '<a href="{}" style="margin-right: 5px;">'
                            '<span style="color: {};">SR-{}</span></a>',
                            ((
                                reverse("admin:service_servicereport_change", args=[sr.pk]),
                                '#28a745' if sr.approval_status == 'approved' else 
                                '#dc3545' if sr.approval_status == 'rejected' else '#ffc107',
                                sr.pk
                            ) for sr in wo.service_reports.all())
                        )
                        
                        wo_table.append(format_html(
                            '<tr>'
                            '<td><a href="{}">{}</a></td>'
                            '<td>{}</td>'
                            '<td>{}</td>'
                            '<td>{}</td>'
                            '</tr>',
                            reverse("admin:service_workorder_change", args=[wo.pk]),
                            f'WO-{wo.pk}',
                            wo.get_status_display(),
                            wo.created_at.strftime("%Y-%m-%d"),
                            sr_links if sr_links else '-'
                        ))
                    wo_table.append('</table>')
                
                summary.append(
                    format_html(
                        '<div style="margin-left: 20px; margin-bottom: 10px;">'
                        '<strong>{}</strong> for <strong>{}</strong>: {}/{} visits'
                        '{}'
                        '</div>',
                        ent.entitlement_type,
                        ent.instrument.serial_number,
                        ent.used_visits,
                        ent.total_visits,
                        format_html(''.join(wo_table)) if wo_table else ' (No work orders)'
                    )
                )
            
            summary.append(format_html('</div>'))
        
        return format_html(''.join(summary))
    entitlements_overview.short_description = 'Entitlements & Work Orders'

    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'website')
        }),
        ('Service Overview', {
            'fields': ('entitlements_overview',),
            'classes': ('collapse',)
        }),
    )

    def agreement_status(self, obj):
        agreements = obj.agreements.all()
        if not agreements.exists():
            return format_html(
                '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 3px;">No Agreement</span>'
            )
        
        # Check for active agreements first
        if obj.agreements.filter(status='active').exists():
            return format_html(
                '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 3px;">Active</span>'
            )
        
        # Then check for drafts
        if obj.agreements.filter(status='draft').exists():
            return format_html(
                '<span style="color: black; background-color: #ffc107; padding: 3px 8px; border-radius: 3px;">Draft</span>'
            )
        
        # If neither active nor draft, must be expired
        return format_html(
            '<span style="color: white; background-color: #fd7e14; padding: 3px 8px; border-radius: 3px;">Expired</span>'
        )
    agreement_status.short_description = "Agreement Status"

    def instrument_count(self, obj):
        return obj.instruments.count()
    instrument_count.short_description = "Instruments"

    def contact_count(self, obj):
        return obj.contacts.count()
    contact_count.short_description = "Contacts"
