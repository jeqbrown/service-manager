from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from service.models import Instrument
from ..serializers.instrument_serializers import InstrumentSerializer

class InstrumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing instrument information.
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally restricts the returned instruments by filtering against
        query parameters in the URL.
        """
        queryset = Instrument.objects.all()
        customer = self.request.query_params.get('customer', None)
        if customer is not None:
            queryset = queryset.filter(customer_id=customer)
        return queryset.order_by('serial_number')