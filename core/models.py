from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class BloodBank(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=100, unique=True)
    registration_number = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    emergency_helpline = models.CharField(max_length=50, blank=True)
    operating_hours = models.CharField(max_length=100, default="24x7 Operations")

    class Meta:
        ordering = ['name']
        verbose_name = "Blood Bank"
        verbose_name_plural = "Blood Banks"

    def __str__(self):
        return f"{self.name} ({self.code})"


class SystemConfiguration(TimeStampedModel):
    CATEGORY_CHOICES = (
        ('CLINICAL', 'Clinical & Eligibility'),
        ('STORAGE', 'Storage & Cold Chain'),
        ('EXPIRY', 'Component Expiration'),
        ('OPERATIONAL', 'Operational & Policy'),
    )

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OPERATIONAL')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_val(cls, key_name, default=None):
        try:
            return cls.objects.get(key=key_name).value
        except cls.DoesNotExist:
            return default
