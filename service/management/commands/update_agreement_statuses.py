from django.core.management.base import BaseCommand
from django.utils import timezone
from service.models import ServiceAgreement

class Command(BaseCommand):
    help = 'Updates the status of all service agreements based on their dates'

    def handle(self, *args, **options):
        agreements = ServiceAgreement.objects.exclude(status=ServiceAgreement.STATUS_DRAFT)
        updated_count = 0

        for agreement in agreements:
            old_status = agreement.status
            agreement.update_status()
            if old_status != agreement.status:
                agreement.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} agreements')
        )