from django.db import models
from django.utils import timezone
from .base import TrackingModel
from .customer import Customer

class ServiceAgreement(TrackingModel):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='agreements')
    po_number = models.CharField(max_length=50, blank=True, verbose_name='PO/CC Number')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

class EntitlementType(TrackingModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Entitlement(TrackingModel):
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='entitlements')
    entitlement_type = models.ForeignKey(EntitlementType, on_delete=models.PROTECT)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
    total_visits = models.PositiveIntegerField(default=0)
    used_visits = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
