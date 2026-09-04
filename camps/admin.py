from django.contrib import admin
from camps.models import BloodCamp, CampRegistration

@admin.register(BloodCamp)
class BloodCampAdmin(admin.ModelAdmin):
    list_display = ('camp_id', 'name', 'city', 'start_date', 'status', 'expected_donors', 'actual_donors')
    list_filter = ('status', 'start_date', 'blood_bank')
    search_fields = ('camp_id', 'name', 'organizer_name', 'city')

@admin.register(CampRegistration)
class CampRegistrationAdmin(admin.ModelAdmin):
    list_display = ('camp', 'donor', 'registered_at', 'attended')
    list_filter = ('attended', 'registered_at')
