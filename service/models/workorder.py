from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, PermissionDenied
from .customer import Customer
from .instrument import Instrument
from .agreement import Entitlement
from .servicereport import ServiceReport

def is_manager(user):
    """Check if user belongs to manager group"""
    return user.groups.filter(name='Manager').exists()

class WorkOrder(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed')
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    instrument = models.ForeignKey(
        'Instrument',
        on_delete=models.CASCADE,
        related_name='workorders'
    )
    description = models.TextField(blank=True, help_text="Description of the work to be performed")
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    def has_approved_reports(self):
        """Check if all submitted reports are approved"""
        reports = self.service_reports.all()
        return reports.exists() and not reports.exclude(approval_status='approved').exists()
    
    def has_reports(self):
        """Check if work order has any service reports"""
        return self.service_reports.exists()
    
    def get_pending_reports(self):
        """Get service reports that are not yet approved"""
        return self.service_reports.exclude(approval_status='approved')
    
    def get_latest_report(self):
        """Get the most recent service report"""
        return self.service_reports.order_by('-service_date').first()

    def clean(self):
        cleaned_data = super().clean()
        
        # Get the current user from the thread local storage
        from django.db import connection
        current_user = getattr(connection, '_current_user', None)
        
        # Ensure work order has entitlement before leaving draft status
        if self.status != self.STATUS_DRAFT and not self.entitlement:
            raise ValidationError({
                'status': 'Work Order must have an entitlement before leaving Draft status.'
            })
        
        # Check manager permission when status is being set to completed
        if self.status == self.STATUS_COMPLETED:
            if current_user and not is_manager(current_user):
                raise ValidationError({
                    'status': 'Only managers can mark work orders as completed.'
                })
            
            if not self.has_reports():
                raise ValidationError({
                    'status': 'Cannot complete work order without at least one service report.'
                })
            
            if not self.has_approved_reports():
                raise ValidationError({
                    'status': 'Cannot complete work order until all service reports are approved.'
                })

            if self.entitlement and self.entitlement.remaining_visits <= 0:
                raise ValidationError({
                    'status': 'Cannot complete work order. No remaining entitlements available.'
                })

        return cleaned_data

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer = self.instrument.customer
        
        # Force draft status if no entitlement
        if not self.entitlement:
            self.status = self.STATUS_DRAFT
            
        self.clean()
        super().save(*args, **kwargs)

    def get_service_reports_display(self):
        reports = self.service_reports.all().order_by('-service_date')
        if not reports:
            return "No service reports"
        return reports

    def __str__(self):
        return f"WO-{self.id} ({self.instrument})"
