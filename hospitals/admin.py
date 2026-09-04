from django.contrib import admin
from hospitals.models import Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'city', 'phone', 'is_verified', 'is_active')
    search_fields = ('name', 'code', 'license_number', 'city', 'contact_person')
    list_filter = ('category', 'is_verified', 'is_active', 'state')
