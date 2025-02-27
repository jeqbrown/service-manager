from rest_framework import serializers
from service.models import ServiceReport

class ServiceReportSerializer(serializers.ModelSerializer):
    work_order_id = serializers.ReadOnlyField(source='work_order.id')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.get_full_name')
    customer_name = serializers.ReadOnlyField(source='customer.name')
    instrument_serial = serializers.ReadOnlyField(source='instrument.serial_number')
    approval_status_display = serializers.ReadOnlyField(source='get_approval_status_display')
    
    class Meta:
        model = ServiceReport
        fields = [
            'id', 'work_order', 'work_order_id', 'created_by', 'created_by_name',
            'service_date', 'findings', 'actions_taken', 'approval_status',
            'approval_status_display', 'approval_date', 'approval_notes',
            'approved_by', 'approved_by_name', 'customer_name', 'instrument_serial'
        ]
        read_only_fields = ['approval_date', 'approved_by']