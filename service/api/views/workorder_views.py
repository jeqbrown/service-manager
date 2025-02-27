from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from service.models import WorkOrder
from service.api.serializers import WorkOrderSerializer
from service.api.permissions import IsStaffOrReadOnly

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'instrument', 'status', 'assigned_to', 'created_by']
    search_fields = ['description', 'customer__name', 'instrument__serial_number']
    ordering_fields = ['created_at', 'status', 'customer__name']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)