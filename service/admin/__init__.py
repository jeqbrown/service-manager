from django.contrib import admin
from .instrument_admin import InstrumentAdmin, InstrumentTypeAdmin
from .customer_admin import CustomerAdmin
from ..models import Instrument, InstrumentType, Customer

# These registrations are handled by the @admin.register decorator
# in each admin class, but we'll make sure they're all registered
if not admin.site.is_registered(Customer):
    admin.site.register(Customer, CustomerAdmin)
if not admin.site.is_registered(Instrument):
    admin.site.register(Instrument, InstrumentAdmin)
if not admin.site.is_registered(InstrumentType):
    admin.site.register(InstrumentType, InstrumentTypeAdmin)
