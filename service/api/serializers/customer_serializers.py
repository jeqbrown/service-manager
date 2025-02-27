from rest_framework import serializers
from service.models import Customer, Contact
from .contact_serializers import ContactSerializer

class CustomerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, required=False)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)

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
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username'
        ]

    def validate_contacts(self, contacts_data):
        if not contacts_data:
            return contacts_data

        # Validate that there's only one primary contact
        primary_count = sum(1 for contact in contacts_data if contact.get('is_primary', False))
        if primary_count > 1:
            raise serializers.ValidationError("Only one contact can be primary")
        
        return contacts_data

    def create(self, validated_data):
        contacts_data = validated_data.pop('contacts', [])
        user = self.context['request'].user
        
        # Create customer
        customer = Customer.objects.create(
            created_by=user,
            updated_by=user,
            **validated_data
        )
        
        # Create contacts
        for contact_data in contacts_data:
            Contact.objects.create(
                customer=customer,
                created_by=user,
                updated_by=user,
                **contact_data
            )
        
        return customer

    def update(self, instance, validated_data):
        contacts_data = validated_data.pop('contacts', None)
        user = self.context['request'].user
        
        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()
        
        # Update contacts if provided
        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                Contact.objects.create(
                    customer=instance,
                    created_by=user,
                    updated_by=user,
                    **contact_data
                )
        
        return instance
