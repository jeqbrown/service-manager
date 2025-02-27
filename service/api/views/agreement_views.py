from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from service.models import ServiceAgreement, EntitlementType, Entitlement
from service.api.serializers import ServiceAgreementSerializer, EntitlementTypeSerializer, EntitlementSerializer
from service.api.permissions import IsStaffOrReadOnly

class EntitlementTypeViewSet(viewsets.ModelViewSet):
    queryset = EntitlementType.objects.all()
    serializer_class = EntitlementTypeSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

class EntitlementViewSet(viewsets.ModelViewSet):
    queryset = Entitlement.objects.all()
    serializer_class = EntitlementSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['service_agreement', 'instrument', 'is_active']
    search_fields = ['instrument__serial_number', 'entitlement_type__name']
    ordering_fields = ['is_active', 'instrument__serial_number']
    ordering = ['-is_active']

class ServiceAgreementViewSet(viewsets.ModelViewSet):
    queryset = ServiceAgreement.objects.all()
    serializer_class = ServiceAgreementSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'status']
    search_fields = ['customer__name', 'po_number']
    ordering_fields = ['start_date', 'end_date', 'status']
    ordering = ['-start_date']