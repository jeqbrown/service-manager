from django.contrib import admin
from ..models import Instrument, InstrumentType

class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'instrument_type', 'customer', 'installation_date', 'assigned_to')
    list_filter = ('instrument_type', 'customer', 'assigned_to')
    search_fields = ('serial_number', 'customer__name', 'instrument_type__name')
    autocomplete_fields = ['instrument_type']
    date_hierarchy = 'installation_date'
