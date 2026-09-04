import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel
from donations.models import Donation
from donors.models import Donor

class BloodBag(TimeStampedModel):
    STATUS_CHOICES = (
        ('QUARANTINED', 'Quarantined (Pending Testing)'),
        ('TESTING_PENDING', 'Testing in Progress'),
        ('TESTED_SAFE', 'Tested Safe / Released for Use'),
        ('REACTIVE_UNSAFE', 'Reactive / Unsafe for Transfusion'),
        ('PROCESSED_TO_COMPONENTS', 'Processed to Components'),
        ('ISSUED', 'Issued to Patient/Hospital'),
        ('EXPIRED', 'Expired'),
        ('DISCARDED', 'Discarded'),
    )

    bag_id = models.CharField(max_length=50, unique=True, db_index=True)
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='blood_bag')
    blood_group = models.CharField(max_length=10, choices=Donor.BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=15, choices=Donor.RH_FACTOR_CHOICES, default='UNKNOWN')
    
    collection_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    bag_type = models.CharField(max_length=30, choices=Donation.BAG_TYPE_CHOICES, default='TRIPLE_450ML')
    volume_ml = models.PositiveIntegerField(default=450)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='QUARANTINED', db_index=True)
    barcode = models.CharField(max_length=100, blank=True)
    storage_location = models.CharField(max_length=100, default='Quarantine Shelf #1')
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-collection_date']
        indexes = [
            models.Index(fields=['bag_id']),
            models.Index(fields=['blood_group', 'status']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.bag_id} [{self.blood_group}] - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.bag_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.bag_id = f"BB-{year}-{rand_int}"
            while BloodBag.objects.filter(bag_id=self.bag_id).exists():
                rand_int = random.randint(100000, 999999)
                self.bag_id = f"BB-{year}-{rand_int}"
        if not self.barcode:
            self.barcode = self.bag_id
        super().save(*args, **kwargs)


class LabSample(TimeStampedModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Testing'),
        ('IN_TESTING', 'Testing in Progress'),
        ('COMPLETED', 'Testing Completed (Pending Verification)'),
        ('VERIFIED', 'Verified & Approved by Medical Officer'),
        ('REJECTED', 'Rejected / Reactive Unit'),
    )

    sample_id = models.CharField(max_length=50, unique=True, db_index=True)
    blood_bag = models.ForeignKey(BloodBag, on_delete=models.CASCADE, related_name='samples')
    collected_at = models.DateTimeField(default=timezone.now)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='samples_collected')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='samples_verified')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-collected_at']

    def __str__(self):
        return f"{self.sample_id} (Bag: {self.blood_bag.bag_id}) - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.sample_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.sample_id = f"SMP-{year}-{rand_int}"
            while LabSample.objects.filter(sample_id=self.sample_id).exists():
                rand_int = random.randint(100000, 999999)
                self.sample_id = f"SMP-{year}-{rand_int}"
        super().save(*args, **kwargs)


class ScreeningResult(TimeStampedModel):
    TEST_CATEGORY_CHOICES = (
        ('ABO_RH_CONFIRMATION', 'ABO & Rh Grouping Confirmation'),
        ('HIV_1_2_ANTIBODY', 'HIV-1 & HIV-2 Antibody / Antigen (4th Gen)'),
        ('HBSAG_HEPATITIS_B', 'Hepatitis B Surface Antigen (HBsAg)'),
        ('HCV_ANTIBODY_HEPATITIS_C', 'Hepatitis C Virus Antibody (Anti-HCV)'),
        ('SYPHILIS_VDRL_TPHA', 'Syphilis Screening (VDRL / TPHA / Treponemal)'),
        ('MALARIA_ANTIGEN', 'Malaria Parasite / Antigen (Rapid / Smear)'),
        ('ANTIBODY_SCREENING', 'Irregular Red Cell Antibody Screening'),
        ('NAT_PCR', 'Nucleic Acid Testing (NAT-PCR) for HIV/HBV/HCV'),
        ('OTHER', 'Other Confirmatory Test'),
    )

    RESULT_CHOICES = (
        ('PENDING', 'Pending Analysis'),
        ('NON_REACTIVE', 'Non-Reactive (Negative / Safe)'),
        ('REACTIVE', 'Reactive (Positive / Unsafe)'),
        ('INVALID', 'Invalid Assay / Retest Required'),
        ('INCONCLUSIVE', 'Inconclusive / Gray Zone'),
        ('CONFIRMED_REACTIVE', 'Confirmed Reactive (Western Blot/Confirmatory)'),
    )

    sample = models.ForeignKey(LabSample, on_delete=models.CASCADE, related_name='screening_results')
    test_category = models.CharField(max_length=40, choices=TEST_CATEGORY_CHOICES)
    test_name = models.CharField(max_length=150)
    result = models.CharField(max_length=30, choices=RESULT_CHOICES, default='PENDING', db_index=True)
    
    tested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tests_conducted')
    test_date = models.DateTimeField(default=timezone.now)
    
    kit_lot_number = models.CharField(max_length=100, default='LOT-2026-DEFAULT')
    kit_expiry = models.DateField(null=True, blank=True)
    quantitative_value = models.CharField(max_length=100, blank=True, help_text="e.g. S/CO ratio or OD value")
    interpretation_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['test_date']

    def __str__(self):
        return f"{self.get_test_category_display()}: {self.get_result_display()}"
