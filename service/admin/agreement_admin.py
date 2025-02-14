from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from ..models.agreement import ServiceAgreement, EntitlementType, Entitlement
from ..models.instrument import Instrument

class EntitlementInline(admin.TabularInline):
    model = Entitlement
    extra = 1
    fields = ('entitlement_type', 'instrument', 'total_visits', 'used_visits', 'remaining_visits', 'is_active')
    readonly_fields = ('used_visits', 'remaining_visits')

    def used_visits(self, obj):
        if obj.pk:
            return obj.used_visits
        return 0
    used_visits.short_description = 'Used Visits'

    def remaining_visits(self, obj):
        if obj.pk:
            return obj.remaining_visits
        return 0
    remaining_visits.short_description = 'Remaining Visits'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('entitlement_type', 'instrument')

@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'start_date', 'end_date', 'status', 'entitlements_summary')
    list_filter = ('status', 'start_date', 'customer')
    search_fields = ('customer__name',)
    inlines = [EntitlementInline]
    autocomplete_fields = ['customer']

    def entitlements_summary(self, obj):
        entitlements = obj.entitlements.all()
        if not entitlements:
            return '-'
        summary = []
        for ent in entitlements:
            summary.append(
                f"{ent.entitlement_type.name}: {ent.used_visits}/{ent.total_visits}"
            )
        return format_html("<br>".join(summary))
    entitlements_summary.short_description = 'Entitlements'

@admin.register(EntitlementType)
class EntitlementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'entitlement_count')
    search_fields = ('name',)

    def entitlement_count(self, obj):
        return obj.entitlement_set.count()
    entitlement_count.short_description = "Usage Count"

@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'agreement', 'total_visits', 'used_visits', 'remaining_visits', 'is_active')
    list_filter = ('is_active', 'entitlement_type', 'agreement__customer')
    search_fields = ('instrument__serial_number', 'agreement__customer__name')
    readonly_fields = ('used_visits', 'remaining_visits')
    autocomplete_fields = ['agreement', 'instrument']
