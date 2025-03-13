from django.db import models
from django.conf import settings
from .base import TrackingModel

class InstrumentType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Instrument Type'
        verbose_name_plural = 'Instrument Types'

    def __str__(self):
        return self.name

class Instrument(TrackingModel):
    serial_number = models.CharField(max_length=200, unique=True)
    instrument_type = models.ForeignKey(
        InstrumentType, 
        on_delete=models.PROTECT, 
        related_name='instruments'
    )
    customer = models.ForeignKey(
        'Customer', 
        on_delete=models.CASCADE, 
        related_name='instruments'
    )
    installation_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('maintenance', 'Under Maintenance'),
            ('retired', 'Retired')
        ],
        default='active'
    )
    location = models.CharField(max_length=200, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_instruments'
    )

    class Meta:
        ordering = ['serial_number']
        verbose_name = 'Instrument'
        verbose_name_plural = 'Instruments'
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.instrument_type} - {self.serial_number}"

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def service_history(self):
        return self.workorders.all().order_by('-created_at')

    @property
    def current_entitlements(self):
        return self.entitlements.filter(
            agreement__status='active',
            is_active=True
        )
