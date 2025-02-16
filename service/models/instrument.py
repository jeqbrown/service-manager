from django.db import models
from django.contrib.auth.models import User
from .customer import Customer

class InstrumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Instrument(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='instruments')
    instrument_type = models.ForeignKey(InstrumentType, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=50, unique=True)
    installation_date = models.DateField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_instruments'
    )

    def __str__(self):
        return f"{self.instrument_type.name} - {self.serial_number}"
