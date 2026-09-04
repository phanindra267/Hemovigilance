from django.contrib import admin
from donors.models import Donor, EligibilityAssessment

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('donor_id', 'full_name', 'blood_group', 'donor_status', 'phone', 'last_donation_date', 'next_eligible_date', 'total_donations_count')
    search_fields = ('donor_id', 'first_name', 'last_name', 'phone', 'email', 'national_id')
    list_filter = ('blood_group', 'donor_status', 'donor_type', 'gender', 'state')

@admin.register(EligibilityAssessment)
class EligibilityAssessmentAdmin(admin.ModelAdmin):
    list_display = ('donor', 'status', 'assessed_by', 'assessment_date', 'hemoglobin_g_dl', 'weight_kg', 'deferral_type')
    list_filter = ('status', 'deferral_type', 'assessment_date')
    search_fields = ('donor__donor_id', 'donor__first_name', 'donor__last_name', 'deferral_reason')
