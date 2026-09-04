from django.core.management.base import BaseCommand
from django.db.models import Count
from inventory.models import InventoryItem
from notifications.models import Notification
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Audits inventory levels, evaluates safe thresholds, and prints stock health report'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Auditing blood bank stock levels..."))
        
        counts = InventoryItem.objects.values('component_type', 'blood_group', 'status').annotate(total=Count('id'))
        available_counts = InventoryItem.objects.filter(status='AVAILABLE').values('component_type', 'blood_group').annotate(total=Count('id'))

        self.stdout.write("------------------------------------------------------------")
        self.stdout.write(f"{'Component':<20} | {'Blood Group':<12} | {'Available Units':<15}")
        self.stdout.write("------------------------------------------------------------")
        
        low_stock_alerts = []
        for entry in available_counts:
            comp = entry['component_type']
            grp = entry['blood_group']
            tot = entry['total']
            self.stdout.write(f"{comp:<20} | {grp:<12} | {tot:<15}")
            
            # Threshold checks: e.g. rare negative groups or general low stock
            if tot < 3:
                low_stock_alerts.append((comp, grp, tot))

        self.stdout.write("------------------------------------------------------------")
        
        if low_stock_alerts:
            staff_users = User.objects.filter(profile__role__in=['SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER'])
            for comp, grp, tot in low_stock_alerts:
                self.stdout.write(self.style.WARNING(f"LOW STOCK WARNING: {comp} [{grp}] has only {tot} units!"))
                for user in staff_users:
                    Notification.objects.create(
                        recipient=user,
                        notification_type='GENERAL',
                        title=f"?? Low Inventory Alert: {comp} [{grp}]",
                        message=f"Critical stock warning: Only {tot} unit(s) of {comp} [{grp}] remaining in available inventory.",
                        link_url="/inventory/"
                    )
        else:
            self.stdout.write(self.style.SUCCESS("Inventory levels are healthy across standard thresholds."))
