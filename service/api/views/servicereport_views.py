from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from service.models import ServiceReport
from service.api.serializers import ServiceReportSerializer
from service.api.permissions import IsStaffOrReadOnly

class ServiceReportViewSet(viewsets.ModelViewSet):
    queryset = ServiceReport.objects.all()
    serializer_class = ServiceReportSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['work_order', 'created_by', 'approval_status', 'approved_by']
    search_fields = ['findings', 'actions_taken', 'work_order__customer__name']
    ordering_fields = ['service_date', 'approval_status']
    ordering = ['-service_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)