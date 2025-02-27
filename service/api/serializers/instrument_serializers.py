from rest_framework import serializers
from service.models import Instrument, InstrumentType

class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = [
            'id',
            'name',
            'description',
            'manufacturer',
            'created_at',
            'updated_at'
        ]

class InstrumentSerializer(serializers.ModelSerializer):
    instrument_type_details = InstrumentTypeSerializer(source='instrument_type', read_only=True)
    
    class Meta:
        model = Instrument
        fields = [
            'id',
            'customer',
            'instrument_type',
            'instrument_type_details',
            'serial_number',
            'asset_number',
            'location',
            'status',
            'assigned_to',
            'installation_date',
            'warranty_expiry',
            'created_at',
            'updated_at'
        ]
