from django.db import models
from django.contrib.auth.models import User
from .customer import Customer
from .instrument import Instrument
from .agreement import Entitlement
from django.core.exceptions import ValidationError

class WorkOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, related_name='workorders')
    entitlement = models.ForeignKey(
        Entitlement, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='workorders'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='created_workorders'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_workorders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def has_approved_reports(self):
        """Check if all submitted reports are approved"""
        reports = self.service_reports.all()
        return reports.exists() and not reports.exclude(approval_status='approved').exists()

    def clean(self):
        cleaned_data = super().clean()
        
        if self.status == 'completed':
            # Check if there are any service reports
            if not self.service_reports.exists():
                raise ValidationError({
                    'status': 'Cannot complete work order without at least one service report.'
                })
            
            # Check if all service reports are approved
            if not self.has_approved_reports():
                raise ValidationError({
                    'status': 'Cannot complete work order until all service reports are approved.'
                })

            # Check entitlement availability (existing logic)
            if self.entitlement and self.entitlement.remaining <= 0:
                raise ValidationError({
                    'status': 'Cannot complete work order. No remaining entitlements available.'
                })

        return cleaned_data

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer = self.instrument.customer
        
        self.clean()
        super().save(*args, **kwargs)

    def get_service_reports_display(self):
        reports = self.service_reports.all().order_by('-service_date')
        if not reports:
            return "No service reports"
        return reports

    def __str__(self):
        return f"WO-{self.id} ({self.instrument})"

class ServiceReport(models.Model):
    work_order = models.ForeignKey(
        WorkOrder, 
        on_delete=models.CASCADE, 
        related_name='service_reports'
    )
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
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_reports'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer = self.work_order.customer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SR-{self.id} ({self.work_order})"
