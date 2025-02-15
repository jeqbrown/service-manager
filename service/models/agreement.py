from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
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

    customer = models.ForeignKey(
        'Customer',
        related_name='agreements',
        on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    def update_status(self):
        """Update agreement status based on dates"""
        today = timezone.now().date()
        
        if self.status == self.STATUS_DRAFT:
            return  # Don't auto-update draft agreements
            
        if today > self.end_date:
            self.status = self.STATUS_EXPIRED
        elif today >= self.start_date:
            self.status = self.STATUS_ACTIVE

    def __str__(self):
        return f"SA-{self.id} ({self.customer.name})"

    def get_status_display(self):
        """Custom method to get display value for status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_admin_url(self):
        return reverse('admin:service_serviceagreement_change', args=[self.pk])

@receiver(pre_save, sender=ServiceAgreement)
def auto_update_agreement_status(sender, instance, **kwargs):
    """Signal to automatically update agreement status before saving"""
    instance.update_status()

class EntitlementType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Entitlement(models.Model):
    agreement = models.ForeignKey(
        ServiceAgreement,
        on_delete=models.CASCADE,
        related_name='entitlements'
    )
    entitlement_type = models.ForeignKey(
        EntitlementType,
        on_delete=models.PROTECT
    )
    instrument = models.ForeignKey(
        'Instrument',
        on_delete=models.CASCADE,
        related_name='entitlements'
    )
    total = models.PositiveIntegerField(
        help_text="Total number of visits/services allowed"
    )
    is_active = models.BooleanField(default=True)

    @property
    def used(self):
        """Calculate number of used visits"""
        return self.workorders.filter(status='completed').count()

    @property
    def remaining(self):
        """Calculate number of remaining visits"""
        return max(0, self.total - self.used)

    def __str__(self):
        return f"{self.entitlement_type} ({self.remaining}/{self.total} remaining) - {self.instrument}"
