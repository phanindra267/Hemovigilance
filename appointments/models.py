import random
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel, BloodBank
from donors.models import Donor
from camps.models import BloodCamp

class Appointment(TimeStampedModel):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('CHECKED_IN', 'Checked-In'),
        ('COMPLETED', 'Donation Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No-Show'),
        ('RESCHEDULED', 'Rescheduled'),
    )

    APPOINTMENT_TYPE_CHOICES = (
        ('BLOOD_BANK', 'Blood Centre / Main Facility'),
        ('CAMP', 'Blood Donation Camp'),
        ('MOBILE_UNIT', 'Mobile Blood Collection Van'),
    )

    TIME_SLOT_CHOICES = (
        ('09:00 - 10:00 AM', '09:00 - 10:00 AM'),
        ('10:00 - 11:00 AM', '10:00 - 11:00 AM'),
        ('11:00 - 12:00 PM', '11:00 - 12:00 PM'),
        ('12:00 - 01:00 PM', '12:00 - 01:00 PM'),
        ('02:00 - 03:00 PM', '02:00 - 03:00 PM'),
        ('03:00 - 04:00 PM', '03:00 - 04:00 PM'),
        ('04:00 - 05:00 PM', '04:00 - 05:00 PM'),
    )

    appointment_id = models.CharField(max_length=50, unique=True, db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='appointments')
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    camp = models.ForeignKey(BloodCamp, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    
    appointment_type = models.CharField(max_length=30, choices=APPOINTMENT_TYPE_CHOICES, default='BLOOD_BANK')
    scheduled_date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SCHEDULED', db_index=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    cancellation_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-scheduled_date', 'time_slot']
        indexes = [
            models.Index(fields=['scheduled_date', 'status']),
        ]

    def __str__(self):
        return f"{self.appointment_id} - {self.donor.full_name} on {self.scheduled_date} ({self.time_slot})"

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.appointment_id = f"APT-{year}-{rand_int}"
            while Appointment.objects.filter(appointment_id=self.appointment_id).exists():
                rand_int = random.randint(100000, 999999)
                self.appointment_id = f"APT-{year}-{rand_int}"
        super().save(*args, **kwargs)
