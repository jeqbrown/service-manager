from rest_framework import serializers
from service.models import WorkOrder, Service

class DashboardWorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = ['id', 'title', 'status', 'priority', 'due_date', 'customer']

class DashboardUpcomingServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'scheduled_date', 'status', 'customer']