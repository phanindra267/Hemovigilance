import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel, BloodBank
from laboratory.models import BloodBag
from blood_components.models import BloodComponent
from donors.models import Donor

class StorageArea(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='storage_areas')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.code}]"


class StorageDevice(TimeStampedModel):
    DEVICE_TYPE_CHOICES = (
        ('REFRIGERATOR_2_6C', 'Blood Bank Refrigerator (+2?C to +6?C)'),
        ('FREEZER_MINUS_20C', 'Standard Plasma Freezer (-20?C to -30?C)'),
        ('FREEZER_MINUS_80C', 'Ultra-Low Temperature Freezer (-40?C to -80?C)'),
        ('PLATELET_AGITATOR_20_24C', 'Platelet Agitator & Incubator (+20?C to +24?C)'),
        ('ROOM_TEMPERATURE', 'Controlled Room Temperature (+18?C to +25?C)'),
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    area = models.ForeignKey(StorageArea, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=40, choices=DEVICE_TYPE_CHOICES)
    
    target_temp_c = models.DecimalField(max_digits=4, decimal_places=1, default=4.0)
    min_temp_c = models.DecimalField(max_digits=4, decimal_places=1, default=2.0)
    max_temp_c = models.DecimalField(max_digits=4, decimal_places=1, default=6.0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"


class StoragePosition(TimeStampedModel):
    device = models.ForeignKey(StorageDevice, on_delete=models.CASCADE, related_name='positions')
    rack_identifier = models.CharField(max_length=50, default='Rack 1')
    shelf_identifier = models.CharField(max_length=50, default='Shelf 1')
    position_identifier = models.CharField(max_length=50, default='Pos 1')
    is_occupied = models.BooleanField(default=False)

    class Meta:
        ordering = ['device', 'rack_identifier', 'shelf_identifier', 'position_identifier']
        unique_together = ('device', 'rack_identifier', 'shelf_identifier', 'position_identifier')

    def __str__(self):
        return f"{self.device.code} -> {self.rack_identifier} / {self.shelf_identifier} / {self.position_identifier}"


class TemperatureLog(TimeStampedModel):
    THRESHOLD_CHOICES = (
        ('NORMAL', 'Within Acceptable Range (Normal)'),
        ('HIGH_EXCURSION', 'High Temperature Excursion (> Max)'),
        ('LOW_EXCURSION', 'Low Temperature Excursion (< Min)'),
        ('CRITICAL', 'Critical Cold-Chain Failure'),
    )

    storage_device = models.ForeignKey(StorageDevice, on_delete=models.CASCADE, related_name='temperature_logs')
    timestamp = models.DateTimeField(default=timezone.now)
    temperature_celsius = models.DecimalField(max_digits=4, decimal_places=1)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='temp_logs_recorded')
    threshold_status = models.CharField(max_length=30, choices=THRESHOLD_CHOICES, default='NORMAL')
    corrective_action_taken = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.storage_device.name}: {self.temperature_celsius}?C [{self.threshold_status}] on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        dev = self.storage_device
        temp = float(self.temperature_celsius)
        if temp > float(dev.max_temp_c) + 4.0 or temp < float(dev.min_temp_c) - 4.0:
            self.threshold_status = 'CRITICAL'
        elif temp > float(dev.max_temp_c):
            self.threshold_status = 'HIGH_EXCURSION'
        elif temp < float(dev.min_temp_c):
            self.threshold_status = 'LOW_EXCURSION'
        else:
            self.threshold_status = 'NORMAL'
        super().save(*args, **kwargs)


class InventoryItem(TimeStampedModel):
    ITEM_TYPE_CHOICES = (
        ('WHOLE_BLOOD_BAG', 'Whole Blood Bag Unit'),
        ('COMPONENT', 'Blood Component Unit'),
    )

    STATUS_CHOICES = (
        ('AVAILABLE', 'Available for Transfusion'),
        ('RESERVED', 'Reserved (Locked for Request)'),
        ('QUARANTINED', 'Quarantined (Non-Issuable)'),
        ('ISSUED', 'Issued to Patient/Hospital'),
        ('RETURNED', 'Returned from Ward'),
        ('EXPIRED', 'Expired'),
        ('DISCARDED', 'Discarded'),
    )

    inventory_id = models.CharField(max_length=50, unique=True, db_index=True)
    item_type = models.CharField(max_length=30, choices=ITEM_TYPE_CHOICES, default='COMPONENT')
    
    blood_bag = models.OneToOneField(BloodBag, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_entry')
    component = models.OneToOneField(BloodComponent, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_entry')
    
    blood_group = models.CharField(max_length=10, choices=Donor.BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=15, choices=Donor.RH_FACTOR_CHOICES, default='UNKNOWN')
    component_type = models.CharField(max_length=40, default='WHOLE_BLOOD')
    volume_ml = models.PositiveIntegerField(default=450)
    
    collection_date = models.DateTimeField()
    expiry_date = models.DateTimeField(db_index=True)
    
    storage_position = models.ForeignKey(StoragePosition, on_delete=models.SET_NULL, null=True, blank=True, related_name='stored_items')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['expiry_date']
        indexes = [
            models.Index(fields=['inventory_id']),
            models.Index(fields=['status', 'component_type', 'blood_group']),
            models.Index(fields=['expiry_date', 'status']),
        ]

    def __str__(self):
        return f"{self.inventory_id} - {self.component_type} [{self.blood_group}] ({self.get_status_display()})"

    @property
    def unit_identifier(self):
        if self.component:
            return self.component.component_id
        if self.blood_bag:
            return self.blood_bag.bag_id
        return self.inventory_id

    @property
    def is_issuable(self):
        if self.status != 'AVAILABLE':
            return False
        if self.expiry_date <= timezone.now():
            return False
        if self.is_locked:
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.inventory_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.inventory_id = f"INV-{year}-{rand_int}"
            while InventoryItem.objects.filter(inventory_id=self.inventory_id).exists():
                rand_int = random.randint(100000, 999999)
                self.inventory_id = f"INV-{year}-{rand_int}"
        
        # Check auto expiry
        if self.status in ['AVAILABLE', 'RESERVED', 'QUARANTINED'] and self.expiry_date <= timezone.now():
            self.status = 'EXPIRED'

        super().save(*args, **kwargs)


class QuarantineRecord(TimeStampedModel):
    REASON_CHOICES = (
        ('PENDING_SCREENING', 'Pending Laboratory Screening & Verification'),
        ('REACTIVE_RESULT', 'Reactive / Infectious Disease Finding'),
        ('TEMPERATURE_EXCURSION', 'Cold Chain Temperature Excursion'),
        ('DAMAGED_BAG', 'Compromised / Damaged Container / Leakage'),
        ('LABELING_ISSUE', 'Defective / Missing Identification Label'),
        ('QUALITY_INVESTIGATION', 'Adverse Event / Quality Investigation'),
        ('OTHER', 'Other Regulatory / SOP Quarantine'),
    )

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='quarantine_records')
    quarantine_id = models.CharField(max_length=50, unique=True, db_index=True)
    reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    
    quarantined_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quarantines_initiated')
    quarantine_date = models.DateTimeField(default=timezone.now)
    
    is_released = models.BooleanField(default=False)
    released_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quarantines_released')
    release_date = models.DateTimeField(null=True, blank=True)
    release_reason = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-quarantine_date']

    def __str__(self):
        return f"Quarantine {self.quarantine_id} on {self.inventory_item.unit_identifier} ({self.get_reason_display()})"

    def save(self, *args, **kwargs):
        if not self.quarantine_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.quarantine_id = f"QRN-{year}-{rand_int}"
            while QuarantineRecord.objects.filter(quarantine_id=self.quarantine_id).exists():
                rand_int = random.randint(100000, 999999)
                self.quarantine_id = f"QRN-{year}-{rand_int}"
        super().save(*args, **kwargs)
