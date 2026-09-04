from django.contrib import admin
from donations.models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_id', 'donor', 'donation_type', 'volume_ml', 'collection_date', 'status', 'collected_by')
    list_filter = ('status', 'donation_type', 'bag_type', 'collection_date')
    search_fields = ('donation_id', 'donor__first_name', 'donor__last_name', 'donor__donor_id')
