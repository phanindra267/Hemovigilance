from django.contrib import admin
from blood_components.models import BloodComponent

@admin.register(BloodComponent)
class BloodComponentAdmin(admin.ModelAdmin):
    list_display = ('component_id', 'component_type', 'blood_group', 'volume_ml', 'prepared_date', 'expiry_date', 'status', 'storage_location')
    list_filter = ('component_type', 'blood_group', 'status', 'prepared_date')
    search_fields = ('component_id', 'parent_bag__bag_id')
