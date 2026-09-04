import random
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel
from hospitals.models import Hospital

class Patient(TimeStampedModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A Positive (A+)'),
        ('A-', 'A Negative (A-)'),
        ('B+', 'B Positive (B+)'),
        ('B-', 'B Negative (B-)'),
        ('AB+', 'AB Positive (AB+)'),
        ('AB-', 'AB Negative (AB-)'),
        ('O+', 'O Positive (O+)'),
        ('O-', 'O Negative (O-)'),
        ('UNKNOWN', 'Unknown / Grouping Required'),
    )

    patient_id = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')
    hospital_mrn = models.CharField(max_length=100, blank=True, verbose_name="Hospital MRN/IPD No")
    attending_physician = models.CharField(max_length=150, blank=True)
    ward_or_room = models.CharField(max_length=100, blank=True)
    
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    medical_history = models.TextField(blank=True)
    transfusion_history = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['blood_group']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id}) [{self.blood_group}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.patient_id = f"PAT-{year}-{rand_int}"
            while Patient.objects.filter(patient_id=self.patient_id).exists():
                rand_int = random.randint(100000, 999999)
                self.patient_id = f"PAT-{year}-{rand_int}"
        super().save(*args, **kwargs)
