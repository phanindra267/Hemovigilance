from django.contrib import admin
from appointments.models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'donor', 'scheduled_date', 'time_slot', 'appointment_type', 'status')
    list_filter = ('status', 'scheduled_date', 'appointment_type', 'blood_bank')
    search_fields = ('appointment_id', 'donor__first_name', 'donor__last_name', 'donor__donor_id')
