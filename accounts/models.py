from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import TimeStampedModel, BloodBank
from hospitals.models import Hospital
from donors.models import Donor
from patients.models import Patient


class Role(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Administrator'
    BLOOD_BANK_ADMIN = 'BLOOD_BANK_ADMIN', 'Blood Bank Administrator'
    MEDICAL_OFFICER = 'MEDICAL_OFFICER', 'Medical Officer'
    LAB_TECHNICIAN = 'LAB_TECHNICIAN', 'Laboratory Technician'
    BLOOD_BANK_TECH = 'BLOOD_BANK_TECH', 'Blood Bank Technician'
    RECEPTIONIST = 'RECEPTIONIST', 'Receptionist / Front Desk'
    HOSPITAL_USER = 'HOSPITAL_USER', 'Hospital / Transfusion Officer'
    DONOR = 'DONOR', 'Donor'
    PATIENT = 'PATIENT', 'Patient / Recipient'


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.DONOR, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='authorized_users')
    donor_profile = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_accounts')
    patient_profile = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_accounts')
    
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__username']
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} [{self.get_role_display()}]"

    @property
    def is_staff_role(self):
        return self.role in [
            Role.SUPER_ADMIN,
            Role.BLOOD_BANK_ADMIN,
            Role.MEDICAL_OFFICER,
            Role.LAB_TECHNICIAN,
            Role.BLOOD_BANK_TECH,
            Role.RECEPTIONIST
        ]

    @property
    def is_medical_or_admin(self):
        return self.role in [Role.SUPER_ADMIN, Role.BLOOD_BANK_ADMIN, Role.MEDICAL_OFFICER]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = Role.SUPER_ADMIN if instance.is_superuser else Role.DONOR
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
