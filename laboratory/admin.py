from django.contrib import admin
from laboratory.models import BloodBag, LabSample, ScreeningResult

@admin.register(BloodBag)
class BloodBagAdmin(admin.ModelAdmin):
    list_display = ('bag_id', 'blood_group', 'bag_type', 'volume_ml', 'collection_date', 'expiry_date', 'status', 'storage_location')
    list_filter = ('blood_group', 'status', 'bag_type', 'expiry_date')
    search_fields = ('bag_id', 'barcode', 'donation__donor__first_name', 'donation__donor__last_name')

@admin.register(LabSample)
class LabSampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'blood_bag', 'collected_at', 'status', 'verified_by', 'verified_at')
    list_filter = ('status', 'collected_at')
    search_fields = ('sample_id', 'blood_bag__bag_id')

@admin.register(ScreeningResult)
class ScreeningResultAdmin(admin.ModelAdmin):
    list_display = ('sample', 'test_category', 'result', 'tested_by', 'test_date')
    list_filter = ('test_category', 'result', 'test_date')
    search_fields = ('sample__sample_id', 'kit_lot_number')
