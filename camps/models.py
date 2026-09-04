import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel, BloodBank
from donors.models import Donor

class BloodCamp(TimeStampedModel):
    STATUS_CHOICES = (
        ('PLANNED', 'Planned / Upcoming'),
        ('ACTIVE', 'Active / In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    camp_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    organizer_name = models.CharField(max_length=150)
    organizer_phone = models.CharField(max_length=30)
    organizer_email = models.EmailField(blank=True)
    
    venue = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='17:00:00')
    
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_camps')
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='camps')
    
    expected_donors = models.PositiveIntegerField(default=50)
    actual_donors = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', db_index=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.camp_id}) - {self.start_date}"

    def save(self, *args, **kwargs):
        if not self.camp_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.camp_id = f"CMP-{year}-{rand_int}"
            while BloodCamp.objects.filter(camp_id=self.camp_id).exists():
                rand_int = random.randint(100000, 999999)
                self.camp_id = f"CMP-{year}-{rand_int}"
        super().save(*args, **kwargs)


class CampRegistration(TimeStampedModel):
    camp = models.ForeignKey(BloodCamp, on_delete=models.CASCADE, related_name='registrations')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='camp_registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('camp', 'donor')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.donor.full_name} -> {self.camp.name}"
