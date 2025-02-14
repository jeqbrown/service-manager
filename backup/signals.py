from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceReport
from .models import WorkOrder


@receiver(post_save, sender=ServiceReport)
def update_entitlement(sender, instance, **kwargs):
    if instance.approval_status == 'approved' and not instance.approval_date:
        # Get associated entitlement
        entitlement = instance.work_order.instrument.entitlements.filter(
            entitlement_type=instance.work_order.service_type
        ).first()
        
        if entitlement and entitlement.remaining_visits > 0:
            entitlement.used_visits += 1
            entitlement.save()
            instance.approval_date = timezone.now()
            instance.save(update_fields=['approval_date'])

@receiver(post_save, sender=WorkOrder)
def update_entitlement(sender, instance, **kwargs):
    if instance.status == 'completed' and instance.entitlement:
        instance.entitlement.used_visits += 1
        instance.entitlement.save()
