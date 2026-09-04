from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import InventoryItem
from notifications.models import Notification
from django.contrib.auth.models import User
from audit.utils import log_audit

class Command(BaseCommand):
    help = 'Scans inventory for expired units and units nearing expiration, updates statuses and generates notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(self.style.NOTICE(f"Checking inventory expiry at {now.strftime('%Y-%m-%d %H:%M:%S')}..."))

        # 1. Update expired units
        expired_items = InventoryItem.objects.filter(
            status__in=['AVAILABLE', 'RESERVED', 'QUARANTINED'],
            expiry_date__lte=now
        )
        expired_count = expired_items.count()

        staff_recipients = User.objects.filter(profile__role__in=['SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH'])

        for item in expired_items:
            old_status = item.status
            item.status = 'EXPIRED'
            item.save()
            log_audit(None, 'UPDATE', item, f"Automated system check marked unit {item.unit_identifier} as EXPIRED (was {old_status})")

            for user in staff_recipients:
                Notification.objects.create(
                    recipient=user,
                    notification_type='EXPIRED_INVENTORY',
                    title=f"?? Inventory Unit Expired: {item.unit_identifier}",
                    message=f"{item.component_type} [{item.blood_group}] unit {item.unit_identifier} reached expiry on {item.expiry_date.strftime('%Y-%m-%d %H:%M')}. Quarantine/discard required.",
                    link_url=f"/inventory/{item.pk}/"
                )

        # 2. Units expiring within 48 hours
        threshold_48h = now + timedelta(hours=48)
        expiring_soon = InventoryItem.objects.filter(
            status='AVAILABLE',
            expiry_date__gt=now,
            expiry_date__lte=threshold_48h
        )
        expiring_count = expiring_soon.count()

        for item in expiring_soon:
            for user in staff_recipients:
                # Avoid duplicate notifications for same item today
                already_notified = Notification.objects.filter(
                    recipient=user,
                    notification_type='EXPIRING_INVENTORY',
                    title__contains=item.unit_identifier,
                    created_at__date=now.date()
                ).exists()
                if not already_notified:
                    Notification.objects.create(
                        recipient=user,
                        notification_type='EXPIRING_INVENTORY',
                        title=f"? Stock Expiring Soon: {item.unit_identifier}",
                        message=f"{item.component_type} [{item.blood_group}] unit {item.unit_identifier} will expire within 48h ({item.expiry_date.strftime('%Y-%m-%d %H:%M')}).",
                        link_url=f"/inventory/{item.pk}/"
                    )

        self.stdout.write(self.style.SUCCESS(f"Done! {expired_count} units marked EXPIRED. {expiring_count} units alerted as expiring soon."))
