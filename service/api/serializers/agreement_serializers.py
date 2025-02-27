from rest_framework import serializers
from service.models import ServiceAgreement, EntitlementType

class EntitlementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntitlementType
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at'
        ]

class ServiceAgreementSerializer(serializers.ModelSerializer):
    entitlement_type_details = EntitlementTypeSerializer(source='entitlement_type', read_only=True)
    
    class Meta:
        model = ServiceAgreement
        fields = [
            'id',
            'customer',
            'agreement_number',
            'po_number',
            'start_date',
            'end_date',
            'entitlement_type',
            'entitlement_type_details',
            'total_value',
            'status',
            'notes',
            'created_at',
            'updated_at'
        ]
