from rest_framework import serializers
from service.models import WorkOrder, Customer, ServiceAgreement

class DashboardWorkOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'title', 'status', 'scheduled_date',
            'customer_name', 'instrument_name', 'assigned_to_name'
        ]

class DashboardUpcomingServiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    next_service_date = serializers.DateField(read_only=True)

    class Meta:
        model = ServiceAgreement
        fields = [
            'id', 'customer_name', 'instrument_name',
            'next_service_date', 'service_frequency'
        ]
