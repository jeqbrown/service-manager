from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ServiceReport(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_AWAITING = 'awaiting'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    APPROVAL_STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_AWAITING, 'Awaiting Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    work_order = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, related_name='service_reports')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='created_service_reports'
    )
    service_date = models.DateField()
    findings = models.TextField()
    actions_taken = models.TextField()
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports'
    )

    class Meta:
        ordering = ['-service_date']

    def __str__(self):
        return f"SR-{self.id} ({self.work_order})"

    @property
    def customer(self):
        return self.work_order.customer if self.work_order else None

    def get_approval_status_display(self):
        return dict(self.APPROVAL_STATUS_CHOICES).get(self.approval_status, self.approval_status)

    def save(self, *args, **kwargs):
        if self.approval_status == self.STATUS_APPROVED and not self.approval_date:
            self.approval_date = timezone.now()
        super().save(*args, **kwargs)
