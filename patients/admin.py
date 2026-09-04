from django.contrib import admin
from patients.models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'full_name', 'blood_group', 'gender', 'hospital', 'phone', 'is_active', 'created_at')
    search_fields = ('patient_id', 'first_name', 'last_name', 'hospital_mrn', 'phone')
    list_filter = ('blood_group', 'gender', 'hospital', 'is_active')
