from rest_framework import viewsets, permissions
from service.models import Customer
from ..serializers import CustomerSerializer
from ..permissions import IsStaffOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'city', 'state']
    search_fields = ['name', 'address', 'city', 'state', 'zip_code', 'website']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        return Customer.objects.all().select_related('created_by', 'updated_by')
