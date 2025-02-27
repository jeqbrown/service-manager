from rest_framework import serializers
from ..models import WorkOrder, ServiceReport, Customer, Instrument

class DashboardWorkOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name')
    
    class Meta:
        model = WorkOrder
        fields = ['id', 'title', 'status', 'customer_name', 'created_at']

class DashboardUpcomingServiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name')
    
    class Meta:
        model = WorkOrder
        fields = ['id', 'scheduled_date', 'title', 'customer_name']
