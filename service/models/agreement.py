from django.db import models
from django.utils import timezone

class EntitlementType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class ServiceAgreement(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_DRAFT = 'draft'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_DRAFT, 'Draft'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='agreements')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    po_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.get_status_display()}"

    def update_status(self):
        today = timezone.now().date()
        if self.status == self.STATUS_DRAFT:
            return
        elif today < self.start_date:
            self.status = self.STATUS_DRAFT
        elif today > self.end_date:
            self.status = self.STATUS_EXPIRED
        else:
            self.status = self.STATUS_ACTIVE

class Entitlement(models.Model):
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='entitlements')
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, related_name='entitlements')
    entitlement_type = models.ForeignKey(EntitlementType, on_delete=models.PROTECT)
    total = models.PositiveIntegerField(help_text='Total number of visits/services allowed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.instrument} - {self.entitlement_type}"

    @property
    def remaining(self):
        used = self.workorder_set.filter(status='completed').count()
        return max(0, self.total - used)
