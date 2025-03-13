from rest_framework import serializers
from ...models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id',
            'customer',
            'name',
            'email',
            'phone',
            'is_primary',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data.get('is_primary'):
            # Check if there's already a primary contact for this customer
            customer = data.get('customer')
            if customer and not self.instance:
                existing_primary = Contact.objects.filter(
                    customer=customer,
                    is_primary=True
                ).exists()
                if existing_primary:
                    raise serializers.ValidationError(
                        "This customer already has a primary contact"
                    )
        return data
