from django.contrib import admin
from requests_app.models import BloodRequest, BloodRequestItem, InventoryReservation, BloodIssue, BloodReturn, DiscardRecord

class BloodRequestItemInline(admin.TabularInline):
    model = BloodRequestItem
    extra = 1

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'hospital', 'patient', 'urgency', 'status', 'required_date_time', 'created_at')
    list_filter = ('status', 'urgency', 'hospital', 'created_at')
    search_fields = ('request_id', 'hospital__name', 'patient__first_name', 'patient__last_name', 'requesting_doctor')
    inlines = [BloodRequestItemInline]

@admin.register(BloodRequestItem)
class BloodRequestItemAdmin(admin.ModelAdmin):
    list_display = ('request', 'component_type', 'blood_group', 'units_requested', 'units_reserved', 'units_issued', 'status')
    list_filter = ('component_type', 'blood_group', 'status')

@admin.register(InventoryReservation)
class InventoryReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'request_item', 'inventory_item', 'reserved_by', 'is_active', 'reserved_at')
    list_filter = ('is_active', 'reserved_at')

@admin.register(BloodIssue)
class BloodIssueAdmin(admin.ModelAdmin):
    list_display = ('issue_id', 'request', 'inventory_item', 'patient', 'recipient_name', 'issued_at', 'status')
    list_filter = ('status', 'issued_at')
    search_fields = ('issue_id', 'recipient_name', 'patient__first_name', 'patient__last_name')

@admin.register(BloodReturn)
class BloodReturnAdmin(admin.ModelAdmin):
    list_display = ('return_id', 'blood_issue', 'returned_by_name', 'disposition', 'cold_chain_maintained', 'returned_at')
    list_filter = ('disposition', 'cold_chain_maintained', 'returned_at')

@admin.register(DiscardRecord)
class DiscardRecordAdmin(admin.ModelAdmin):
    list_display = ('discard_id', 'inventory_item', 'discard_reason', 'discarded_by', 'authorized_by', 'discard_date')
    list_filter = ('discard_reason', 'biohazard_disposal_method', 'discard_date')
