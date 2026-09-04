import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel

class Donor(TimeStampedModel):
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
        ('UNKNOWN', 'Unknown / Typing Required'),
    )

    RH_FACTOR_CHOICES = (
        ('POSITIVE', 'Rh Positive (+)'),
        ('NEGATIVE', 'Rh Negative (-)'),
        ('UNKNOWN', 'Unknown'),
    )

    DONOR_TYPE_CHOICES = (
        ('VOLUNTARY', 'Voluntary Non-Remunerated Donor'),
        ('REPLACEMENT', 'Replacement / Family Donor'),
        ('DIRECTED', 'Directed Donor'),
        ('AUTOLOGOUS', 'Autologous Donor'),
        ('FAMILY', 'Family Donor'),
    )

    DONOR_STATUS_CHOICES = (
        ('ACTIVE', 'Active & Eligible'),
        ('TEMPORARILY_DEFERRED', 'Temporarily Deferred'),
        ('PERMANENTLY_DEFERRED', 'Permanently Deferred'),
        ('BLOCKED', 'Blocked / Medically Ineligible'),
        ('INACTIVE', 'Inactive'),
    )

    donor_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donor_record')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    rh_factor = models.CharField(max_length=15, choices=RH_FACTOR_CHOICES, default='UNKNOWN')
    
    donor_type = models.CharField(max_length=30, choices=DONOR_TYPE_CHOICES, default='VOLUNTARY')
    donor_status = models.CharField(max_length=30, choices=DONOR_STATUS_CHOICES, default='ACTIVE', db_index=True)
    
    phone = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True)
    national_id = models.CharField(max_length=50, blank=True, verbose_name="National ID / Passport")
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    registration_date = models.DateField(default=timezone.now)
    last_donation_date = models.DateField(null=True, blank=True)
    next_eligible_date = models.DateField(null=True, blank=True)
    total_donations_count = models.PositiveIntegerField(default=0)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['donor_id']),
            models.Index(fields=['blood_group']),
            models.Index(fields=['donor_status']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.donor_id}) [{self.blood_group}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_currently_eligible(self):
        if self.donor_status != 'ACTIVE':
            return False
        if self.next_eligible_date and self.next_eligible_date > timezone.now().date():
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.donor_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.donor_id = f"DNR-{year}-{rand_int}"
            while Donor.objects.filter(donor_id=self.donor_id).exists():
                rand_int = random.randint(100000, 999999)
                self.donor_id = f"DNR-{year}-{rand_int}"
        # Sync Rh factor from blood group if needed
        if '+' in self.blood_group:
            self.rh_factor = 'POSITIVE'
        elif '-' in self.blood_group:
            self.rh_factor = 'NEGATIVE'
        super().save(*args, **kwargs)


class EligibilityAssessment(TimeStampedModel):
    STATUS_CHOICES = (
        ('ELIGIBLE', 'Eligible for Donation'),
        ('TEMPORARILY_DEFERRED', 'Temporarily Deferred'),
        ('PERMANENTLY_DEFERRED', 'Permanently Deferred'),
        ('REJECTED', 'Medically Unfit / Rejected'),
    )

    DEFERRAL_CHOICES = (
        ('NONE', 'None / Fit for Donation'),
        ('LOW_HEMOGLOBIN', 'Low Hemoglobin (< 12.5 g/dL)'),
        ('RECENT_TATTOO_OR_PIERCING', 'Recent Tattoo or Body Piercing (< 6-12 Months)'),
        ('MEDICATION', 'Contraindicated Medication (Antibiotics/Anticoagulants)'),
        ('TRAVEL_HISTORY', 'Endemic Malaria / Travel Deferral'),
        ('RECENT_ILLNESS', 'Recent Infection / Fever / Cold (< 14 Days)'),
        ('HIGH_RISK_BEHAVIOR', 'High Risk Behavior / Exposure'),
        ('UNDERWEIGHT', 'Underweight (< 45/50 kg)'),
        ('HYPERTENSION_OR_HYPOTENSION', 'Blood Pressure out of Safe Range'),
        ('PREGNANCY_OR_LACTATION', 'Pregnancy or Lactation (< 12 Months)'),
        ('RECENT_SURGERY', 'Major Surgery within 6 Months'),
        ('OTHER', 'Other Clinical Reason'),
    )

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='eligibility_assessments')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assessments_conducted')
    assessment_date = models.DateTimeField(default=timezone.now)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, db_index=True)
    
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kilograms")
    hemoglobin_g_dl = models.DecimalField(max_digits=4, decimal_places=1, help_text="Hemoglobin level in g/dL")
    systolic_bp = models.PositiveIntegerField(help_text="Systolic Blood Pressure (mmHg)")
    diastolic_bp = models.PositiveIntegerField(help_text="Diastolic Blood Pressure (mmHg)")
    pulse_bpm = models.PositiveIntegerField(help_text="Pulse rate (beats per minute)")
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, default=36.6, help_text="Body Temperature (?C)")
    
    deferral_type = models.CharField(max_length=40, choices=DEFERRAL_CHOICES, default='NONE')
    deferral_reason = models.TextField(blank=True)
    deferral_start_date = models.DateField(null=True, blank=True)
    deferral_end_date = models.DateField(null=True, blank=True)
    
    medical_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return f"Assessment for {self.donor.full_name} on {self.assessment_date.strftime('%Y-%m-%d')} - {self.get_status_display()}"
