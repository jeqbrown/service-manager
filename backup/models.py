from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=100, blank=True)
    primary_contact = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.customer.name}"

    class Meta:
        ordering = ['-primary_contact', 'name']

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

    def __str__(self):
        return f"{self.instrument_type.name} - {self.serial_number}"

class ServiceAgreement(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='agreements')
    start_date = models.DateField()
    end_date = models.DateField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('draft', 'Draft')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"SA-{self.id} ({self.customer.name})"

class EntitlementType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Entitlement(models.Model):
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='entitlements')
    entitlement_type = models.ForeignKey(EntitlementType, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    total_visits = models.PositiveIntegerField(default=0)
    used_visits = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def remaining(self):
        return self.total_visits - self.used_visits

    def __str__(self):
        return f"{self.entitlement_type.name} for {self.instrument}"

class WorkOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    entitlement = models.ForeignKey(Entitlement, on_delete=models.PROTECT, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def save(self, *args, **kwargs):
        # Auto-set customer from instrument
        if not self.customer_id:
            self.customer = self.instrument.customer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WO-{self.id} ({self.instrument})"

class ServiceReport(models.Model):
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='service_report')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.PROTECT)
    service_date = models.DateField()
    findings = models.TextField()
    actions_taken = models.TextField()
    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports')
    approval_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-set customer from work order
        if not self.customer_id:
            self.customer = self.work_order.customer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SR-{self.id} ({self.work_order})"

# Signal to handle entitlement consumption
@receiver(post_save, sender=WorkOrder)
def update_entitlement(sender, instance, **kwargs):
    if instance.status == 'completed' and instance.entitlement and not kwargs.get('raw', False):
        if instance.entitlement.used_visits < instance.entitlement.total_visits:
            instance.entitlement.used_visits += 1
            instance.entitlement.save()