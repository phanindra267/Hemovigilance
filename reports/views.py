from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from accounts.decorators import role_required
from donors.models import Donor
from donations.models import Donation
from inventory.models import InventoryItem
from requests_app.models import BloodRequest, BloodIssue, DiscardRecord
from reports.exporters import export_to_csv, export_to_pdf

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def reports_index_view(request):
    return render(request, 'reports/reports_index.html')

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def donor_report_view(request):
    blood_group = request.GET.get('blood_group', '')
    donor_status = request.GET.get('donor_status', '')
    export = request.GET.get('export', '')

    queryset = Donor.objects.all().order_by('-registration_date')
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if donor_status:
        queryset = queryset.filter(donor_status=donor_status)

    if export == 'csv':
        headers = ['Donor ID', 'Name', 'Blood Group', 'Gender', 'Phone', 'Status', 'Total Donations', 'Last Donation']
        rows = [[d.donor_id, d.full_name, d.blood_group, d.get_gender_display(), d.phone, d.get_donor_status_display(), d.total_donations_count, str(d.last_donation_date or '')] for d in queryset]
        return export_to_csv('donor_report', headers, rows)
    elif export == 'pdf':
        headers = ['Donor ID', 'Name', 'Blood Group', 'Phone', 'Status', 'Donations', 'Last Date']
        rows = [[d.donor_id, d.full_name, d.blood_group, d.phone, d.donor_status, str(d.total_donations_count), str(d.last_donation_date or 'N/A')] for d in queryset]
        return export_to_pdf('Donor Registry Report', headers, rows, f'Filtered: Group={blood_group or "All"}, Status={donor_status or "All"}')

    return render(request, 'reports/donor_report.html', {
        'donors': queryset[:100],
        'total_count': queryset.count(),
        'blood_groups': Donor.BLOOD_GROUP_CHOICES,
        'statuses': Donor.DONOR_STATUS_CHOICES,
        'selected_group': blood_group,
        'selected_status': donor_status,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def donation_report_view(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    status = request.GET.get('status', '')
    export = request.GET.get('export', '')

    queryset = Donation.objects.select_related('donor', 'blood_bank', 'collected_by').all().order_by('-collection_date')
    if start_date:
        queryset = queryset.filter(collection_date__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(collection_date__date__lte=end_date)
    if status:
        queryset = queryset.filter(status=status)

    if export == 'csv':
        headers = ['Donation ID', 'Donor ID', 'Donor Name', 'Type', 'Volume (mL)', 'Date', 'Status', 'Collected By']
        rows = [[d.donation_id, d.donor.donor_id, d.donor.full_name, d.get_donation_type_display(), d.volume_ml, d.collection_date.strftime('%Y-%m-%d %H:%M'), d.get_status_display(), str(d.collected_by or '')] for d in queryset]
        return export_to_csv('donation_report', headers, rows)
    elif export == 'pdf':
        headers = ['Donation ID', 'Donor Name', 'Type', 'Vol', 'Date', 'Status']
        rows = [[d.donation_id, d.donor.full_name, d.donation_type, f'{d.volume_ml}mL', d.collection_date.strftime('%Y-%m-%d'), d.status] for d in queryset]
        return export_to_pdf('Blood Donation Collections Report', headers, rows, f'Date Range: {start_date or "Start"} to {end_date or "Present"}')

    return render(request, 'reports/donation_report.html', {
        'donations': queryset[:100],
        'total_count': queryset.count(),
        'total_volume': queryset.aggregate(Sum('volume_ml'))['volume_ml__sum'] or 0,
        'statuses': Donation.STATUS_CHOICES,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def inventory_report_view(request):
    component_type = request.GET.get('component_type', '')
    blood_group = request.GET.get('blood_group', '')
    status = request.GET.get('status', 'AVAILABLE')
    export = request.GET.get('export', '')

    queryset = InventoryItem.objects.all().order_by('expiry_date')
    if component_type:
        queryset = queryset.filter(component_type=component_type)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if status and status != 'ALL':
        queryset = queryset.filter(status=status)

    if export == 'csv':
        headers = ['Inventory ID', 'Unit ID', 'Component', 'Blood Group', 'Volume (mL)', 'Expiry Date', 'Status']
        rows = [[i.inventory_id, i.unit_identifier, i.component_type, i.blood_group, i.volume_ml, i.expiry_date.strftime('%Y-%m-%d %H:%M'), i.get_status_display()] for d, i in enumerate(queryset)]
        return export_to_csv('inventory_report', headers, rows)
    elif export == 'pdf':
        headers = ['Unit ID', 'Component', 'Group', 'Vol', 'Expiry Date', 'Status']
        rows = [[i.unit_identifier, i.component_type, i.blood_group, f'{i.volume_ml}mL', i.expiry_date.strftime('%Y-%m-%d'), i.status] for i in queryset]
        return export_to_pdf('Inventory Stock and Expiry Report', headers, rows, f'Status: {status}')

    stock_by_group = queryset.values('blood_group', 'component_type').annotate(count=Count('id'))

    return render(request, 'reports/inventory_report.html', {
        'items': queryset[:100],
        'total_count': queryset.count(),
        'stock_by_group': stock_by_group,
        'selected_comp': component_type,
        'selected_group': blood_group,
        'selected_status': status,
        'statuses': InventoryItem.STATUS_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def issue_report_view(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    status = request.GET.get('status', '')
    export = request.GET.get('export', '')

    queryset = BloodIssue.objects.select_related('request__hospital', 'patient', 'inventory_item', 'issued_by').all().order_by('-issued_at')
    if start_date:
        queryset = queryset.filter(issued_at__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(issued_at__date__lte=end_date)
    if status:
        queryset = queryset.filter(status=status)

    if export == 'csv':
        headers = ['Issue ID', 'Request ID', 'Hospital', 'Patient', 'Unit ID', 'Component', 'Group', 'Issued At', 'Issued By', 'Status']
        rows = [[i.issue_id, i.request.request_id, i.request.hospital.name, i.patient.full_name, i.inventory_item.unit_identifier, i.inventory_item.component_type, i.inventory_item.blood_group, i.issued_at.strftime('%Y-%m-%d %H:%M'), str(i.issued_by or ''), i.get_status_display()] for i in queryset]
        return export_to_csv('issue_report', headers, rows)
    elif export == 'pdf':
        headers = ['Issue ID', 'Hospital', 'Patient', 'Unit', 'Group', 'Issued At', 'Status']
        rows = [[i.issue_id, i.request.hospital.name[:15], i.patient.full_name, i.inventory_item.unit_identifier, i.inventory_item.blood_group, i.issued_at.strftime('%Y-%m-%d'), i.status] for i in queryset]
        return export_to_pdf('Blood Crossmatch & Issue Report', headers, rows, 'Patient Hemovigilance Distribution')

    return render(request, 'reports/issue_report.html', {
        'issues': queryset[:100],
        'total_count': queryset.count(),
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'statuses': BloodIssue.STATUS_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def discard_report_view(request):
    reason = request.GET.get('reason', '')
    export = request.GET.get('export', '')

    queryset = DiscardRecord.objects.select_related('inventory_item', 'discarded_by', 'authorized_by').all().order_by('-discard_date')
    if reason:
        queryset = queryset.filter(discard_reason=reason)

    if export == 'csv':
        headers = ['Discard ID', 'Unit ID', 'Component', 'Blood Group', 'Reason', 'Discard Date', 'Executed By', 'Authorized By', 'Disposal Method']
        rows = [[d.discard_id, d.inventory_item.unit_identifier, d.inventory_item.component_type, d.inventory_item.blood_group, d.get_discard_reason_display(), d.discard_date.strftime('%Y-%m-%d %H:%M'), str(d.discarded_by or ''), str(d.authorized_by or ''), d.get_biohazard_disposal_method_display()] for d in queryset]
        return export_to_csv('discard_wastage_report', headers, rows)
    elif export == 'pdf':
        headers = ['Discard ID', 'Unit', 'Group', 'Reason', 'Date', 'Authorized By']
        rows = [[d.discard_id, d.inventory_item.unit_identifier, d.inventory_item.blood_group, d.get_discard_reason_display()[:25], d.discard_date.strftime('%Y-%m-%d'), str(d.authorized_by or '')] for d in queryset]
        return export_to_pdf('Hemovigilance Discard & Wastage Audit Report', headers, rows, 'Confidential Safety Record')

    return render(request, 'reports/discard_report.html', {
        'discards': queryset[:100],
        'total_count': queryset.count(),
        'reasons': DiscardRecord.REASON_CHOICES,
        'selected_reason': reason,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def rare_donor_report_view(request):
    # Rare Blood Groups: AB-, B-, A-, O-
    rare_groups = ['AB-', 'B-', 'A-', 'O-']
    queryset = Donor.objects.filter(blood_group__in=rare_groups).order_by('blood_group', '-last_donation_date')
    
    export = request.GET.get('export', '')
    if export == 'csv':
        headers = ['Donor ID', 'Name', 'Blood Group', 'Phone', 'City', 'Last Donated', 'Next Eligible', 'Status']
        rows = [[d.donor_id, d.full_name, d.blood_group, d.phone, d.city, str(d.last_donation_date or 'Never'), str(d.next_eligible_date or 'Immediate'), d.get_donor_status_display()] for d in queryset]
        return export_to_csv('rare_donors_report', headers, rows)
    elif export == 'pdf':
        headers = ['Donor ID', 'Name', 'Rare Group', 'Phone', 'City', 'Last Date', 'Status']
        rows = [[d.donor_id, d.full_name, d.blood_group, d.phone, d.city, str(d.last_donation_date or 'N/A'), d.donor_status] for d in queryset]
        return export_to_pdf('Rare Blood Group Donor Registry Report', headers, rows, 'Critical Emergency Donor Registry')

    return render(request, 'reports/rare_donor_report.html', {
        'donors': queryset,
        'total_count': queryset.count(),
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def monthly_summary_view(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)
    
    donations_this_month = Donation.objects.filter(collection_date__gte=month_start).count()
    requests_this_month = BloodRequest.objects.filter(created_at__gte=month_start).count()
    issues_this_month = BloodIssue.objects.filter(issued_at__gte=month_start).count()
    discards_this_month = DiscardRecord.objects.filter(discard_date__gte=month_start).count()

    total_active_stock = InventoryItem.objects.filter(status='AVAILABLE').count()
    quarantined_stock = InventoryItem.objects.filter(status='QUARANTINED').count()

    return render(request, 'reports/monthly_summary.html', {
        'current_month': now.strftime('%B %Y'),
        'donations_this_month': donations_this_month,
        'requests_this_month': requests_this_month,
        'issues_this_month': issues_this_month,
        'discards_this_month': discards_this_month,
        'total_active_stock': total_active_stock,
        'quarantined_stock': quarantined_stock,
    })
