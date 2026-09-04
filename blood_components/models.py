import random
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel
from laboratory.models import BloodBag
from donors.models import Donor

class BloodComponent(TimeStampedModel):
    COMPONENT_TYPE_CHOICES = (
        ('WHOLE_BLOOD', 'Whole Blood (WB)'),
        ('PRBC', 'Packed Red Blood Cells (PRBC / RBC)'),
        ('PLATELET', 'Random / Single Donor Platelet (RDP/SDP)'),
        ('FFP', 'Fresh Frozen Plasma (FFP)'),
        ('CRYOPRECIPITATE', 'Cryoprecipitate Anti-Hemophilic Factor'),
        ('CRYOSUPERNATANT', 'Cryo-Poor Plasma (Cryosupernatant)'),
        ('PLASMA_FRACTION', 'Plasma for Fractionation'),
    )

    STATUS_CHOICES = (
        ('AVAILABLE', 'Available for Transfusion'),
        ('RESERVED', 'Reserved for Patient'),
        ('QUARANTINED', 'Quarantined'),
        ('ISSUED', 'Issued to Patient/Hospital'),
        ('RETURNED', 'Returned from Clinical Ward'),
        ('EXPIRED', 'Expired / Shelf Life Exceeded'),
        ('DISCARDED', 'Discarded / Biohazard Waste'),
    )

    # Standard Shelf Life in Days
    DEFAULT_SHELF_LIFE = {
        'WHOLE_BLOOD': 35,
        'PRBC': 42,
        'PLATELET': 5,
        'FFP': 365,
        'CRYOPRECIPITATE': 365,
        'CRYOSUPERNATANT': 365,
        'PLASMA_FRACTION': 365,
    }

    component_id = models.CharField(max_length=50, unique=True, db_index=True)
    parent_bag = models.ForeignKey(BloodBag, on_delete=models.CASCADE, related_name='components')
    component_type = models.CharField(max_length=40, choices=COMPONENT_TYPE_CHOICES, db_index=True)
    
    blood_group = models.CharField(max_length=10, choices=Donor.BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=15, choices=Donor.RH_FACTOR_CHOICES, default='UNKNOWN')
    
    prepared_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(db_index=True)
    volume_ml = models.PositiveIntegerField(help_text="Volume in mL")
    
    prepared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='components_prepared')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    storage_location = models.CharField(max_length=100, default='Cold Storage Shelf A')
    
    leukoreduced = models.BooleanField(default=False)
    irradiated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-prepared_date']
        indexes = [
            models.Index(fields=['component_id']),
            models.Index(fields=['component_type', 'blood_group', 'status']),
            models.Index(fields=['expiry_date', 'status']),
        ]

    def __str__(self):
        return f"{self.component_id} ({self.get_component_type_display()} [{self.blood_group}])"

    def save(self, *args, **kwargs):
        if not self.component_id:
            year = timezone.now().year
            rand_int = random.randint(100000, 999999)
            self.component_id = f"CMPNT-{year}-{rand_int}"
            while BloodComponent.objects.filter(component_id=self.component_id).exists():
                rand_int = random.randint(100000, 999999)
                self.component_id = f"CMPNT-{year}-{rand_int}"
        if not self.expiry_date:
            shelf_days = self.DEFAULT_SHELF_LIFE.get(self.component_type, 35)
            self.expiry_date = self.prepared_date + timedelta(days=shelf_days)
        super().save(*args, **kwargs)
