from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from requests_app.models import BloodRequest
from laboratory.models import LabSample
from notifications.models import Notification
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Generates routine system notifications (appointment reminders, pending lab samples, urgent requests)'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        self.stdout.write("Generating scheduled system notifications...")
        count = 0

        # 1. Appointment reminders for tomorrow
        upcoming_appointments = Appointment.objects.filter(
            scheduled_date=tomorrow,
            status='SCHEDULED'
        ).select_related('donor', 'donor__user')

        for appt in upcoming_appointments:
            user = appt.donor.user
            if user:
                already = Notification.objects.filter(recipient=user, notification_type='APPOINTMENT_REMINDER', created_at__date=today).exists()
                if not already:
                    Notification.objects.create(
                        recipient=user,
                        notification_type='APPOINTMENT_REMINDER',
                        title="Reminder: Tomorrow's Blood Donation Appointment",
                        message=f"Dear {appt.donor.full_name}, your blood donation appointment ({appt.appointment_id}) is scheduled for tomorrow at {appt.time_slot}. Thank you for saving lives!",
                        link_url="/appointments/"
                    )
                    count += 1

        # 2. Pending lab samples alert for lab technicians
        pending_samples = LabSample.objects.filter(status='PENDING').count()
        if pending_samples > 0:
            lab_techs = User.objects.filter(profile__role__in=['LAB_TECHNICIAN', 'MEDICAL_OFFICER'])
            for tech in lab_techs:
                Notification.objects.create(
                    recipient=tech,
                    notification_type='PENDING_SCREENING',
                    title=f"?? {pending_samples} Pending Blood Sample(s) in Laboratory",
                    message=f"There are {pending_samples} blood bag sample(s) awaiting serological screening and verification.",
                    link_url="/laboratory/samples/"
                )
                count += 1

        # 3. Urgent or Emergency requests under review
        urgent_requests = BloodRequest.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW'], urgency__in=['URGENT', 'EMERGENCY']).count()
        if urgent_requests > 0:
            officers = User.objects.filter(profile__role__in=['SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER'])
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    notification_type='EMERGENCY_REQUEST',
                    title=f"?? {urgent_requests} High-Priority Blood Request(s) Pending Review",
                    message=f"{urgent_requests} urgent/emergency blood requisition(s) require immediate medical review and reservation.",
                    link_url="/requests/"
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} notifications."))
