from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from service.models import Instrument, InstrumentType
from service.api.serializers import InstrumentSerializer, InstrumentTypeSerializer
from service.api.permissions import IsStaffOrReadOnly

class InstrumentTypeViewSet(viewsets.ModelViewSet):
    queryset = InstrumentType.objects.all()
    serializer_class = InstrumentTypeSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'instrument_type', 'assigned_to']
    search_fields = ['serial_number', 'customer__name', 'instrument_type__name']
    ordering_fields = ['serial_number', 'installation_date', 'customer__name']
    ordering = ['serial_number']