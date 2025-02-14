from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ..models.workorder import WorkOrder, ServiceReport

# Remove the old signal handlers as they're no longer needed
