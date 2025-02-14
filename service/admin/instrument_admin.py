from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from ..models.instrument import InstrumentType, Instrument
from ..utils.admin_links import work_order_links

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'instrument_count')
    search_fields = ('name',)

    def instrument_count(self, obj):
        return obj.instrument_set.count()
    instrument_count.short_description = "Instruments"

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'customer', 'instrument_type', 'work_order_actions')
    list_filter = ('customer', 'instrument_type')
    search_fields = ('serial_number', 'instrument_type__name')

    def work_order_actions(self, obj):
        return work_order_links(obj)
    work_order_actions.short_description = "Actions"
