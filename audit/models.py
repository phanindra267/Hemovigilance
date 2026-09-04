from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete/Deactivate'),
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('APPROVE', 'Medical/Supervisor Approval'),
        ('REJECT', 'Rejection/Disapproval'),
        ('RESERVE', 'Inventory Reservation'),
        ('CANCEL_RESERVATION', 'Cancel Reservation'),
        ('ISSUE', 'Blood Issue to Patient/Hospital'),
        ('RETURN', 'Blood Return & Triage'),
        ('QUARANTINE', 'Quarantine Unit'),
        ('RELEASE', 'Release from Quarantine'),
        ('DISCARD', 'Biohazard Discard/Wastage'),
        ('VERIFY', 'Laboratory Verification'),
        ('CHECK_IN', 'Appointment Check-In'),
    )

    action = models.CharField(max_length=30, choices=ACTION_CHOICES, db_index=True)
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=100, db_index=True)
    object_repr = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    details = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.action} on {self.model_name} #{self.object_id} by {user_str}"
