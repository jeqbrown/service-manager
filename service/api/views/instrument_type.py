from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from service.models import InstrumentType
from ..serializers.instrument_serializers import InstrumentTypeSerializer

class InstrumentTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing instrument type information.
    """
    queryset = InstrumentType.objects.all()
    serializer_class = InstrumentTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns instrument types ordered by name
        """
        return InstrumentType.objects.all().order_by('name')