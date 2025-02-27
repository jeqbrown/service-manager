from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from service.models import EntitlementType
from ..serializers.agreement_serializers import EntitlementTypeSerializer

class EntitlementTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing entitlement type information.
    """
    queryset = EntitlementType.objects.all()
    serializer_class = EntitlementTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns entitlement types ordered by name
        """
        return EntitlementType.objects.all().order_by('name')