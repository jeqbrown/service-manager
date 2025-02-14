from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from .customer import Customer

class ServiceAgreement(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_DRAFT = 'draft'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_DRAFT, 'Draft')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='agreements')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    def __str__(self):
        return f"SA-{self.id} ({self.customer.name})"

    def get_status_display(self):
        """Custom method to get display value for status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_admin_url(self):
        return reverse('admin:service_serviceagreement_change', args=[self.pk])

class EntitlementType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Entitlement(models.Model):
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='entitlements')
    entitlement_type = models.ForeignKey(EntitlementType, on_delete=models.PROTECT)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, related_name='entitlements')
    total_visits = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    @property
    def used_visits(self):
        """Calculate used visits based on completed work orders"""
        return self.instrument.workorder_set.filter(
            entitlement=self,
            status='completed'
        ).count()

    @property
    def remaining_visits(self):
        """Calculate remaining visits"""
        return self.total_visits - self.used_visits

    def __str__(self):
        return f"{self.entitlement_type.name} for {self.instrument}"

    def get_admin_url(self):
        return reverse('admin:service_entitlement_change', args=[self.pk])
