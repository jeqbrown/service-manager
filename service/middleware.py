from django.db.models import signals
from django.utils.deprecation import MiddlewareMixin
from threading import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)

def set_created_by(sender, instance, **kwargs):
    if not instance.created_by_id:
        instance.created_by = get_current_user()
    instance.updated_by = get_current_user()

def connect_tracking_signals():
    from .models import (
        Customer, Contact, Instrument, InstrumentType,
        ServiceAgreement, EntitlementType, Entitlement
    )
    
    tracked_models = [
        Customer, Contact, Instrument, InstrumentType,
        ServiceAgreement, EntitlementType, Entitlement
    ]
    
    for model in tracked_models:
        signals.pre_save.connect(set_created_by, sender=model, weak=False)
