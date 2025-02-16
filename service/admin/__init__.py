# Import all admin classes
from .customer_admin import CustomerAdmin
from .instrument_admin import InstrumentAdmin, InstrumentTypeAdmin
from .agreement_admin import ServiceAgreementAdmin, EntitlementTypeAdmin
from .workorder_admin import WorkOrderAdmin
from .servicereport_admin import ServiceReportAdmin

# No registrations here - we'll handle them in apps.py
