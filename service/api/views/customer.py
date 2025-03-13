from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from service.models import Customer, Contact
from ..serializers import CustomerSerializer, ContactSerializer
from ..permissions import CustomerPermissions

class CustomerFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    city = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Customer
        fields = ['name', 'city', 'state']

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing customer information.
    Supports CRUD operations, filtering, searching, and sorting.
    """
    queryset = Customer.objects.all().order_by('-created_at', 'name')
    serializer_class = CustomerSerializer
    permission_classes = [CustomerPermissions]
    filter_class = CustomerFilter
    filterset_class = CustomerFilter  # For newer DRF versions
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at', 'name']  # Default ordering

    def perform_create(self, serializer):
        customer = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
        # Handle nested contacts
        contacts_data = self.request.data.get('contacts', [])
        for contact_data in contacts_data:
            Contact.objects.create(
                customer=customer,
                created_by=self.request.user,
                updated_by=self.request.user,
                **contact_data
            )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """List all contacts for a specific customer"""
        customer = self.get_object()
        contacts = Contact.objects.filter(customer=customer)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """Add a new contact to a specific customer"""
        customer = self.get_object()
        serializer = ContactSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                customer=customer,
                created_by=request.user,
                updated_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
