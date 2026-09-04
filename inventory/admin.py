from django.contrib import admin
from inventory.models import StorageArea, StorageDevice, StoragePosition, TemperatureLog, InventoryItem, QuarantineRecord

@admin.register(StorageArea)
class StorageAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'blood_bank', 'is_active')
    search_fields = ('name', 'code')

@admin.register(StorageDevice)
class StorageDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'area', 'device_type', 'target_temp_c', 'min_temp_c', 'max_temp_c')
    list_filter = ('device_type', 'area')
    search_fields = ('name', 'code')

@admin.register(TemperatureLog)
class TemperatureLogAdmin(admin.ModelAdmin):
    list_display = ('storage_device', 'temperature_celsius', 'threshold_status', 'recorded_by', 'timestamp')
    list_filter = ('threshold_status', 'storage_device', 'timestamp')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'unit_identifier', 'component_type', 'blood_group', 'volume_ml', 'expiry_date', 'status')
    list_filter = ('status', 'component_type', 'blood_group', 'expiry_date')
    search_fields = ('inventory_id', 'blood_bag__bag_id', 'component__component_id')

@admin.register(QuarantineRecord)
class QuarantineRecordAdmin(admin.ModelAdmin):
    list_display = ('quarantine_id', 'inventory_item', 'reason', 'quarantined_by', 'is_released', 'quarantine_date')
    list_filter = ('reason', 'is_released', 'quarantine_date')
