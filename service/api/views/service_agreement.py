from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from service.models import ServiceAgreement
from ..serializers.agreement_serializers import ServiceAgreementSerializer

class ServiceAgreementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing service agreement information.
    """
    queryset = ServiceAgreement.objects.all()
    serializer_class = ServiceAgreementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns service agreements ordered by start date
        """
        return ServiceAgreement.objects.all().order_by('-start_date')