from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from .models import Instrument, Entitlement

class LandingPageView(TemplateView):
    template_name = 'service/landing.html'

@staff_member_required
def filter_instruments(request):
    customer_id = request.GET.get('customer')
    if customer_id:
        instruments = (Instrument.objects
                      .filter(customer_id=customer_id)
                      .values('id', 'serial_number'))
        return JsonResponse(list(instruments), safe=False)
    return JsonResponse([], safe=False)

@staff_member_required
def filter_entitlements(request):
    instrument_id = request.GET.get('instrument')
    if instrument_id:
        entitlements = (Entitlement.objects
                       .filter(
                           instrument_id=instrument_id,
                           is_active=True
                       )
                       .select_related('entitlement_type')
                       .annotate(
                           remaining=F('total_visits') - F('used_visits')
                       )
                       .values('id', 'entitlement_type__name', 'remaining'))
        
        return JsonResponse([{
            'id': e['id'],
            'entitlement_type': e['entitlement_type__name'],
            'remaining': e['remaining']
        } for e in entitlements], safe=False)
    return JsonResponse([], safe=False)
