import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel, BloodBank
from donors.models import Donor, EligibilityAssessment
from appointments.models import Appointment
from camps.models import BloodCamp

class Donation(TimeStampedModel):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('ARRIVED', 'Arrived at Facility'),
        ('ELIGIBILITY_PENDING', 'Eligibility Assessment Pending'),
        ('ELIGIBLE', 'Eligible for Donation'),
        ('COLLECTION_STARTED', 'Collection In Progress'),
        ('COLLECTED', 'Collection Completed (Pending Lab)'),
        ('REJECTED', 'Rejected Medically'),
        ('DEFERRED', 'Deferred'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed & Processed'),
    )

    DONATION_TYPE_CHOICES = (
        ('WHOLE_BLOOD', 'Whole Blood Donation'),
        ('APHERESIS_PLATELET', 'Apheresis Platelet (SDP)'),
        ('APHERESIS_PLASMA', 'Apheresis Plasma / Plasmapheresis'),
        ('AUTOLOGOUS', 'Autologous Pre-Deposit'),
    )

    BAG_TYPE_CHOICES = (
        ('SINGLE_350ML', 'Single Bag (350 mL - CPDA-1)'),
        ('SINGLE_450ML', 'Single Bag (450 mL - CPDA-1)'),
        ('DOUBLE_350ML', 'Double Bag (350 mL - SAGM)'),
        ('DOUBLE_450ML', 'Double Bag (450 mL - SAGM)'),
        ('TRIPLE_450ML', 'Triple Bag (450 mL - SAGM / Platelet)'),
        ('QUADRUPLE_450ML', 'Quadruple Bag (450 mL - Top and Bottom SAGM)'),
        ('APHERESIS_KIT', 'Apheresis Kit Set'),
    )

    VEIN_CHOICES = (
        ('LEFT_ARM', 'Left Antecubital Vein'),
        ('RIGHT_ARM', 'Right Antecubital Vein'),
    )

    donation_id = models.CharField(max_length=50, unique=True, db_index=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='donation_record')
    camp = models.ForeignKey(BloodCamp, on_delete=models.SET_NULL, null=True, blank=True, related_name='camp_donations')
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='donations')
    assessment = models.ForeignKey(EligibilityAssessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_donations')
    
    collection_date = models.DateTimeField(default=timezone.now)
    donation_type = models.CharField(max_length=30, choices=DONATION_TYPE_CHOICES, default='WHOLE_BLOOD')
    bag_type = models.CharField(max_length=30, choices=BAG_TYPE_CHOICES, default='TRIPLE_450ML')
    volume_ml = models.PositiveIntegerField(default=450, help_text="Volume collected in mL")
    
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections_performed')
    vein_used = models.CharField(max_length=20, choices=VEIN_CHOICES, default='LEFT_ARM')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ARRIVED', db_index=True)
    adverse_reaction = models.BooleanField(default=False)
    adverse_reaction_notes = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-collection_date']
        indexes = [
            models.Index(fields=['donation_id']),
            models.Index(fields=['collection_date', 'status']),
        ]

    def __str__(self):
        return f"{self.donation_id} - {self.donor.full_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.donation_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.donation_id = f"DON-{year}-{rand_int}"
            while Donation.objects.filter(donation_id=self.donation_id).exists():
                rand_int = random.randint(100000, 999999)
                self.donation_id = f"DON-{year}-{rand_int}"
        super().save(*args, **kwargs)
