from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel

class Notification(TimeStampedModel):
    NOTIFICATION_TYPE_CHOICES = (
        ('APPOINTMENT_REMINDER', 'Appointment Reminder'),
        ('EMERGENCY_REQUEST', 'Emergency Blood Request (STAT)'),
        ('PENDING_SCREENING', 'Pending Laboratory Screening'),
        ('EXPIRING_INVENTORY', 'Expiring Inventory Alert'),
        ('EXPIRED_INVENTORY', 'Expired Inventory Alert'),
        ('REQUEST_STATUS_CHANGE', 'Request Status Updated'),
        ('DONATION_COMPLETED', 'Donation Completed'),
        ('QUARANTINE_EVENT', 'Quarantine Event Action'),
        ('TEMPERATURE_ALERT', 'Cold Chain Temperature Alert'),
        ('GENERAL', 'General System Notification'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=40, choices=NOTIFICATION_TYPE_CHOICES, default='GENERAL', db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} -> {self.recipient.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
