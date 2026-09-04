from django.db import models
from core.models import TimeStampedModel

class Hospital(TimeStampedModel):
    CATEGORY_CHOICES = (
        ('GOVERNMENT', 'Government / Public Hospital'),
        ('PRIVATE', 'Private Hospital / Medical Center'),
        ('TRUST', 'Charitable / Trust Hospital'),
        ('MILITARY', 'Military / Defense Hospital'),
        ('CLINIC', 'Specialized Clinic / Day Care'),
    )

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    license_number = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='PRIVATE')
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    contact_person = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    emergency_contact = models.CharField(max_length=50, blank=True)
    
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"

    def __str__(self):
        return f"{self.name} [{self.code}]"
