from rest_framework import serializers
from service.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'is_primary',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'updated_by'
        ]
