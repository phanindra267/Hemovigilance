from django.contrib import admin
from core.models import BloodBank, SystemConfiguration

@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'license_number', 'city', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'license_number', 'city')
    list_filter = ('is_active', 'state')

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'category', 'updated_at')
    search_fields = ('key', 'description')
    list_filter = ('category', 'is_active')
