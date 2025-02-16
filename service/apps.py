from django.apps import AppConfig

class ServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service'

    def ready(self):
        # Import the custom admin site
        from .admin.site import admin_site
        
        # Import all necessary models and admin classes
        from django.contrib.auth.models import User, Group
        from django.contrib.auth.admin import UserAdmin, GroupAdmin
        from .models import (
            Customer, Instrument, InstrumentType,
            ServiceAgreement, EntitlementType,
            WorkOrder, ServiceReport
        )
        from .admin.customer_admin import CustomerAdmin
        from .admin.instrument_admin import InstrumentAdmin, InstrumentTypeAdmin
        from .admin.agreement_admin import ServiceAgreementAdmin, EntitlementTypeAdmin
        from .admin.workorder_admin import WorkOrderAdmin
        from .admin.servicereport_admin import ServiceReportAdmin

        # First unregister User and Group if they're already registered
        try:
            admin_site.unregister(User)
        except:
            pass
            
        try:
            admin_site.unregister(Group)
        except:
            pass

        # Register User with the default UserAdmin
        admin_site.register(User, UserAdmin)
        # Register Group with the default GroupAdmin
        admin_site.register(Group, GroupAdmin)

        # Register all other models
        admin_site.register(Customer, CustomerAdmin)
        admin_site.register(Instrument, InstrumentAdmin)
        admin_site.register(InstrumentType, InstrumentTypeAdmin)
        admin_site.register(ServiceAgreement, ServiceAgreementAdmin)
        admin_site.register(EntitlementType, EntitlementTypeAdmin)
        admin_site.register(WorkOrder, WorkOrderAdmin)
        admin_site.register(ServiceReport, ServiceReportAdmin)
