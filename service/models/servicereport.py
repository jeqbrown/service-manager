from django.db import models

class ServiceReport(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    APPROVAL_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    work_order = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, related_name='service_reports')
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default=STATUS_PENDING
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)

    def __str__(self):
        return f"SR-{self.id} ({self.work_order})"

    def get_approval_status_display(self):
        """Custom method to get display value for approval status"""
        return dict(self.APPROVAL_STATUS_CHOICES).get(self.approval_status, self.approval_status)
