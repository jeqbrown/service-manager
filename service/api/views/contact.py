from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from service.models import Contact
from ..serializers.contact_serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing contact information.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally restricts the returned contacts by filtering against
        query parameters in the URL.
        """
        queryset = Contact.objects.all()
        customer = self.request.query_params.get('customer', None)
        if customer is not None:
            queryset = queryset.filter(customer_id=customer)
        return queryset.order_by('name')