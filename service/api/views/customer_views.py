from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from service.models import Customer
from service.api.serializers import CustomerSerializer
from service.api.permissions import IsStaffOrReadOnly
from rest_framework.response import Response

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing customer information.
    """
    queryset = Customer.objects.all().select_related('created_by', 'updated_by')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'city', 'state']
    search_fields = ['name', 'address', 'city', 'state', 'website']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
