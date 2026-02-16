from django.core.management.base import BaseCommand
from messaging.models import Message
from products.models import Advert

class Command(BaseCommand):
    help = "Auto-fix messages that have no advert_id by detecting correct advert"

    def handle(self, *args, **kwargs):
        orphan_messages = Message.objects.filter(advert__isnull=True)

        if not orphan_messages.exists():
            self.stdout.write(self.style.SUCCESS("No orphan messages found."))
            return

        fixed = 0
        marked_read = 0

        for msg in orphan_messages:
            # find conversations between the same sender/receiver that DO have adverts
            related = Message.objects.filter(
                sender__in=[msg.sender, msg.receiver],
                receiver__in=[msg.sender, msg.receiver],
                advert__isnull=False
            ).order_by('-timestamp')

            if related.exists():
                # assign the most recently used advert between the two users
                msg.advert = related.first().advert
                msg.save()
                fixed += 1
            else:
                # No advert exists AT ALL, so mark it read so it never blocks badge counts
                msg.is_read = True
                msg.save()
                marked_read += 1

        self.stdout.write(self.style.SUCCESS(
            f"Fixed adverts for {fixed} messages."
        ))
        self.stdout.write(self.style.WARNING(
            f"Marked {marked_read} messages as read (no advert match found)."
        ))

        self.stdout.write(self.style.SUCCESS("Done."))
