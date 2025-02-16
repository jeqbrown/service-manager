from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from ..models.servicereport import ServiceReport
from ..models.workorder import WorkOrder
from ..utils.status_colors import get_status_badge
import logging
from django.forms import ModelForm, ModelChoiceField

logger = logging.getLogger(__name__)

class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username

class ServiceReportForm(ModelForm):
    created_by = UserModelChoiceField(
        queryset=User.objects.all().order_by('first_name', 'last_name'),
        required=True
    )

    class Meta:
        model = ServiceReport
        fields = '__all__'

class CreatedByFilter(SimpleListFilter):
    title = 'Created By'
    parameter_name = 'created_by'

    def lookups(self, request, model_admin):
        # Get all users who have created service reports
        users = (User.objects.filter(created_service_reports__isnull=False)
                .distinct()
                .order_by('first_name', 'last_name'))
        return [(user.id, user.get_full_name() or user.username) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by_id=self.value())
        return queryset

# Removed the @admin.register decorator
class ServiceReportAdmin(admin.ModelAdmin):
    form = ServiceReportForm
    
    class Media:
        css = {
            'all': [
                # Remove these as they're already included by Django admin
                # 'admin/css/base.css',
                # 'admin/css/forms.css',
                'service/css/service_history.css',  # Keep only your custom CSS
            ]
        }
        js = ['admin/js/jquery.init.js']

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            if isinstance(inline, admin.TabularInline):
                inline.template = 'admin/edit_inline/tabular.html'
        return inline_instances
    
    list_display = ('__str__', 'work_order_link', 'customer', 'status_badge', 'service_date', 'created_by_full_name')
    list_filter = ('approval_status', 'work_order__customer', 'service_date', CreatedByFilter)
    search_fields = ('work_order__instrument__serial_number', 'work_order__customer__name', 
                    'created_by__username', 'created_by__first_name', 'created_by__last_name')
    readonly_fields = ('approval_date', 'approved_by')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Only for new objects
            form.base_fields['created_by'].initial = request.user
        return form

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'work_order',
            'created_by',
            'approved_by',
            'work_order__customer'
        )
    
    def created_by_full_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "-"
    created_by_full_name.short_description = 'Created By'
    created_by_full_name.admin_order_field = 'created_by__first_name'

    def work_order_link(self, obj):
        url = reverse("admin:service_workorder_change", args=[obj.work_order.id])
        return format_html(
            '<a href="{}" class="related-widget-wrapper-link">{}</a>', 
            url, obj.work_order
        )
    work_order_link.short_description = 'Work Order'
    work_order_link.admin_order_field = 'work_order'

    def customer(self, obj):
        return obj.work_order.customer

    def status_badge(self, obj):
        return get_status_badge(obj.approval_status)
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'approval_status'

    fieldsets = (
        (None, {
            'fields': ('work_order', 'created_by', 'service_date')
        }),
        ('Service Details', {
            'fields': ('findings', 'actions_taken')
        }),
        ('Approval Information', {
            'fields': ('approval_status', 'approval_date', 'approval_notes', 'approved_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.approval_status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

    def service_history(self, obj):
        """Display detailed service history for the instrument."""
        work_orders = WorkOrder.objects.filter(
            entitlement__agreement=obj
        ).select_related(
            'assigned_to',
            'instrument',
            'entitlement__entitlement_type'
        ).prefetch_related(
            'service_reports',
            'service_reports__created_by'
        ).order_by('-created_at')

        if not work_orders:
            return "No service history available"

        html = ['<div class="service-history">']
        
        for wo in work_orders:
            status_badge = get_status_badge(wo.get_status_display())
            
            # Get service reports for this work order
            service_reports = wo.service_reports.all()
            sr_links = []
            for sr in service_reports:
                sr_url = reverse('admin:service_servicereport_change', args=[sr.pk])
                sr_links.append(
                    f'<a href="{sr_url}" class="button" style="padding: 5px 10px; margin: 2px;">'
                    f'SR-{sr.pk}</a>'
                )
            
            sr_html = ''.join(sr_links) if sr_links else 'No service reports'
            
            # Add new service report button
            new_sr_url = reverse('admin:service_servicereport_add') + f'?work_order={wo.pk}'
            sr_html += (
                f'<a href="{new_sr_url}" class="addlink" '
                f'style="padding: 5px 10px; margin: 2px; background-position: 0 center;">'
                f'Add SR</a>'
            )
            
            wo_url = reverse('admin:service_workorder_change', args=[wo.pk])
            html.append(f'''
                <div class="history-item module" style="margin-bottom: 15px;">
                    <div style="margin-bottom: 10px;">
                        <strong>
                            <a href="{wo_url}" class="changelink" 
                               style="padding: 5px 10px; background-position: 0 center;">
                                WO-{wo.pk}
                            </a>
                        </strong> - {status_badge}
                        <br>
                        <span style="color: #666;">{wo.description or "-"}</span>
                    </div>
                    <div class="action-buttons">
                        <strong>Service Reports:</strong> {sr_html}
                    </div>
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">
                        Assigned to: {wo.assigned_to.get_full_name() if wo.assigned_to else 'Unassigned'}
                        | Created: {wo.created_at.strftime('%Y-%m-%d')}
                    </div>
                </div>
            ''')

        html.append('</div>')
        return format_html(''.join(html))

    service_history.short_description = 'Service History'




