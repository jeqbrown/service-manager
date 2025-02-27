from django.db import models
from .base import TrackingModel
from .customer import Customer

class InstrumentType(TrackingModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Instrument(TrackingModel):
    instrument_type = models.ForeignKey(
        InstrumentType,
        on_delete=models.PROTECT,
        related_name='instruments'
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='instruments')
    serial_number = models.CharField(max_length=50, unique=True)
    installation_date = models.DateField()
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_instruments'
    )

    def __str__(self):
        return f"{self.instrument_type.name} - {self.serial_number}"
