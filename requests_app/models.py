import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel, BloodBank
from hospitals.models import Hospital
from patients.models import Patient
from inventory.models import InventoryItem
from donors.models import Donor
from blood_components.models import BloodComponent

class BloodRequest(TimeStampedModel):
    URGENCY_CHOICES = (
        ('NORMAL', 'Routine / Elective (Within 24 Hours)'),
        ('URGENT', 'Urgent (Within 2-4 Hours)'),
        ('EMERGENCY', 'Immediate Life Threat / Emergency (STAT)'),
    )

    STATUS_CHOICES = (
        ('DRAFT', 'Draft Request'),
        ('SUBMITTED', 'Submitted to Blood Bank'),
        ('UNDER_REVIEW', 'Under Medical Officer Review'),
        ('APPROVED', 'Approved by Medical Officer'),
        ('PARTIALLY_FULFILLED', 'Partially Fulfilled'),
        ('RESERVED', 'Inventory Units Reserved'),
        ('READY_FOR_ISSUE', 'Crossmatched & Ready for Issue'),
        ('ISSUED', 'Issued to Hospital/Patient'),
        ('COMPLETED', 'Completed & Transfused'),
        ('REJECTED', 'Rejected by Blood Bank'),
        ('CANCELLED', 'Cancelled by Requestor'),
    )

    request_id = models.CharField(max_length=50, unique=True, db_index=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='blood_requests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_requests')
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='received_requests')
    
    requesting_doctor = models.CharField(max_length=150)
    requested_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requests_submitted')
    
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='NORMAL', db_index=True)
    required_date_time = models.DateTimeField()
    
    clinical_diagnosis = models.TextField()
    transfusion_indication = models.TextField(blank=True)
    special_requirements = models.CharField(max_length=200, blank=True, help_text='e.g. Leukoreduced, Irradiated, CMV Negative')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED', db_index=True)
    
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_reviewed')
    review_timestamp = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['status', 'urgency']),
            models.Index(fields=['hospital', 'created_at']),
        ]

    def __str__(self):
        return f'{self.request_id} - {self.hospital.name} for {self.patient.full_name} [{self.urgency}]'

    def save(self, *args, **kwargs):
        if not self.request_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.request_id = f'REQ-{year}-{rand_int}'
            while BloodRequest.objects.filter(request_id=self.request_id).exists():
                rand_int = random.randint(100000, 999999)
                self.request_id = f'REQ-{year}-{rand_int}'
        super().save(*args, **kwargs)


class BloodRequestItem(TimeStampedModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Fulfillment'),
        ('RESERVED', 'Reserved'),
        ('ISSUED', 'Issued'),
        ('CANCELLED', 'Cancelled'),
    )

    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='items')
    component_type = models.CharField(max_length=40, choices=BloodComponent.COMPONENT_TYPE_CHOICES, default='PRBC')
    blood_group = models.CharField(max_length=10, choices=Donor.BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=15, choices=Donor.RH_FACTOR_CHOICES, default='UNKNOWN')
    
    units_requested = models.PositiveIntegerField(default=1)
    units_reserved = models.PositiveIntegerField(default=0)
    units_issued = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.units_requested}x {self.get_component_type_display()} [{self.blood_group}] for {self.request.request_id}'


class InventoryReservation(TimeStampedModel):
    reservation_id = models.CharField(max_length=50, unique=True, db_index=True)
    request_item = models.ForeignKey(BloodRequestItem, on_delete=models.CASCADE, related_name='reservations')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='reservations')
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reservations_made')
    reserved_at = models.DateTimeField(default=timezone.now)
    
    is_active = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-reserved_at']

    def __str__(self):
        return f'Reservation {self.reservation_id} of Unit {self.inventory_item.unit_identifier} for {self.request_item.request.request_id}'

    def save(self, *args, **kwargs):
        if not self.reservation_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.reservation_id = f'RSV-{year}-{rand_int}'
            while InventoryReservation.objects.filter(reservation_id=self.reservation_id).exists():
                rand_int = random.randint(100000, 999999)
                self.reservation_id = f'RSV-{year}-{rand_int}'
        super().save(*args, **kwargs)


class BloodIssue(TimeStampedModel):
    STATUS_CHOICES = (
        ('ISSUED', 'Issued to Courier/Hospital'),
        ('ACKNOWLEDGED', 'Received & Acknowledged at Ward'),
        ('CANCELLED', 'Issue Cancelled Prior to Dispatch'),
        ('RETURNED', 'Returned to Blood Centre'),
    )

    issue_id = models.CharField(max_length=50, unique=True, db_index=True)
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='issues')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='issue_records')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='transfused_units')
    
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='units_issued')
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issues_authorized')
    
    recipient_name = models.CharField(max_length=150, help_text='Name of hospital personnel receiving the unit')
    recipient_id_proof = models.CharField(max_length=100, blank=True, help_text='Staff ID or badge number')
    
    issued_at = models.DateTimeField(default=timezone.now)
    crossmatch_compatible = models.BooleanField(default=True)
    crossmatch_details = models.CharField(max_length=200, default='Crossmatch Compatible (Major & Minor Tube Technique)')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ISSUED')
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f'Issue {self.issue_id} -> Unit {self.inventory_item.unit_identifier} to {self.patient.full_name}'

    def save(self, *args, **kwargs):
        if not self.issue_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.issue_id = f'ISS-{year}-{rand_int}'
            while BloodIssue.objects.filter(issue_id=self.issue_id).exists():
                rand_int = random.randint(100000, 999999)
                self.issue_id = f'ISS-{year}-{rand_int}'
        super().save(*args, **kwargs)


class BloodReturn(TimeStampedModel):
    DISPOSITION_CHOICES = (
        ('RE_ENTRY_APPROVED', 'Approved for Inventory Re-Entry (Cold Chain Intact)'),
        ('QUARANTINE_FOR_INVESTIGATION', 'Quarantine for Serological / Hemolysis Investigation'),
        ('DISCARD_ORDERED', 'Discard Ordered (Cold Chain Violated / Seal Damaged)'),
    )

    return_id = models.CharField(max_length=50, unique=True, db_index=True)
    blood_issue = models.OneToOneField(BloodIssue, on_delete=models.CASCADE, related_name='return_record')
    
    returned_by_name = models.CharField(max_length=150)
    returned_at = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='returns_received')
    
    cold_chain_maintained = models.BooleanField(default=True)
    visual_inspection_passed = models.BooleanField(default=True)
    bag_seal_intact = models.BooleanField(default=True)
    
    condition_notes = models.TextField(blank=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='return_assessments')
    
    disposition = models.CharField(max_length=40, choices=DISPOSITION_CHOICES, default='QUARANTINE_FOR_INVESTIGATION')
    disposition_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-returned_at']

    def __str__(self):
        return f'Return {self.return_id} for Issue {self.blood_issue.issue_id} ({self.get_disposition_display()})'

    def save(self, *args, **kwargs):
        if not self.return_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.return_id = f'RET-{year}-{rand_int}'
            while BloodReturn.objects.filter(return_id=self.return_id).exists():
                rand_int = random.randint(100000, 999999)
                self.return_id = f'RET-{year}-{rand_int}'
        super().save(*args, **kwargs)


class DiscardRecord(TimeStampedModel):
    REASON_CHOICES = (
        ('EXPIRED', 'Shelf Life Expired'),
        ('REACTIVE_TTI', 'Transfusion-Transmissible Infection Reactive (HIV/HBV/HCV/Syphilis/Malaria)'),
        ('TEMPERATURE_EXCURSION', 'Cold Chain Failure / Temperature Excursion'),
        ('DAMAGED_BAG', 'Container Integrity Compromised / Leaking'),
        ('QUALITY_FAILURE', 'Clots / Hemolysis / Turbidity / Visual Quality Defect'),
        ('UNSUITABLE_RETURN', 'Returned Blood Unfit for Re-Issue'),
        ('HEMOLYZED_OR_LIPEMIC', 'Severely Hemolyzed, Icteric, or Lipemic Sample/Unit'),
        ('OTHER', 'Other Regulatory or Quality Failure'),
    )

    DISPOSAL_METHOD_CHOICES = (
        ('AUTOCLAVING_INCINERATION', 'Autoclaving Followed by High-Temperature Incineration'),
        ('CHEMICAL_TREATMENT', 'Chemical Disinfection (1% Sodium Hypochlorite)'),
        ('BIOHAZARD_WASTE_VENDOR', 'Authorized Biohazard Waste Management Contractor'),
    )

    discard_id = models.CharField(max_length=50, unique=True, db_index=True)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='discard_records')
    
    discard_reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    reason_details = models.TextField()
    
    discarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='discards_executed')
    authorized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='discards_authorized')
    
    discard_date = models.DateTimeField(default=timezone.now)
    biohazard_disposal_method = models.CharField(max_length=40, choices=DISPOSAL_METHOD_CHOICES, default='AUTOCLAVING_INCINERATION')
    disposal_manifest_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-discard_date']

    def __str__(self):
        return f'Discard {self.discard_id} - Unit {self.inventory_item.unit_identifier} ({self.get_discard_reason_display()})'

    def save(self, *args, **kwargs):
        if not self.discard_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.discard_id = f'DIS-{year}-{rand_int}'
            while DiscardRecord.objects.filter(discard_id=self.discard_id).exists():
                rand_int = random.randint(100000, 999999)
                self.discard_id = f'DIS-{year}-{rand_int}'
        super().save(*args, **kwargs)
