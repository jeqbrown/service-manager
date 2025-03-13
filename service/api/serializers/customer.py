from rest_framework import serializers
from ...models import Customer
from .contact import ContactSerializer

class CustomerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    primary_contact = ContactSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'address',
            'city',
            'state',
            'zip_code',
            'website',
            'contacts',
            'primary_contact',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
