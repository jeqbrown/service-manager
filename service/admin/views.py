from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.apps import apps
from ..models import InstrumentType

@staff_member_required
def instrument_type_options(request):
    """Return JSON data for instrument type options."""
    instrument_types = InstrumentType.objects.all()
    options = [{"value": it.pk, "label": str(it)} for it in instrument_types]
    return JsonResponse(options, safe=False)

@staff_member_required
def get_model_option(request, model_name, object_id):
    """Return JSON data for popup form object selection."""
    try:
        # Get the model class dynamically
        model = apps.get_model('service', model_name)
        obj = get_object_or_404(model, pk=object_id)
        
        # Get the display value based on model
        if hasattr(obj, 'name'):
            label = obj.name
        elif hasattr(obj, 'get_full_name'):
            label = obj.get_full_name() or str(obj)
        else:
            label = str(obj)

        return JsonResponse({
            "value": str(obj.pk),
            "label": label
        })
    except LookupError:
        return JsonResponse({"error": "Model not found"}, status=404)
