from rest_framework import serializers
from service.models import WorkOrder

class WorkOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    instrument_serial = serializers.ReadOnlyField(source='instrument.serial_number')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    has_reports = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = WorkOrder
        fields = [
            'id', 'customer', 'customer_name', 'instrument', 'instrument_serial',
            'description', 'entitlement', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'created_at', 'status',
            'status_display', 'has_reports'
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['has_reports'] = instance.has_reports()
        return representation