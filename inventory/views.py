from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from inventory.models import InventoryItem, StorageArea, StorageDevice, TemperatureLog, QuarantineRecord
from inventory.forms import TemperatureLogForm, QuarantineForm, QuarantineReleaseForm
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def inventory_stock_view(request):
    search = request.GET.get('search', '')
    component_type = request.GET.get('component_type', '')
    blood_group = request.GET.get('blood_group', '')
    status = request.GET.get('status', 'AVAILABLE')

    queryset = InventoryItem.objects.select_related('blood_bag', 'component').all()
    if search:
        queryset = queryset.filter(inventory_id__icontains=search) | queryset.filter(blood_bag__bag_id__icontains=search) | queryset.filter(component__component_id__icontains=search)
    if component_type:
        queryset = queryset.filter(component_type=component_type)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if status and status != 'ALL':
        queryset = queryset.filter(status=status)

    # Aggregate summaries for stock matrix
    stock_matrix = InventoryItem.objects.filter(status='AVAILABLE').values('blood_group', 'component_type').annotate(total_units=Count('id'))

    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/inventory_list.html', {
        'page_obj': page_obj,
        'search': search,
        'component_type': component_type,
        'blood_group': blood_group,
        'status': status,
        'stock_matrix': stock_matrix,
        'statuses': InventoryItem.STATUS_CHOICES,
        'available_count': InventoryItem.objects.filter(status='AVAILABLE').count(),
        'reserved_count': InventoryItem.objects.filter(status='RESERVED').count(),
        'quarantined_count': InventoryItem.objects.filter(status='QUARANTINED').count(),
        'expired_count': InventoryItem.objects.filter(status='EXPIRED').count(),
    })

@login_required
def inventory_detail_view(request, pk):
    item = get_object_or_404(InventoryItem.objects.select_related('blood_bag', 'component', 'storage_position'), pk=pk)
    quarantine_records = item.quarantine_records.select_related('quarantined_by', 'released_by').all()
    return render(request, 'inventory/inventory_detail.html', {
        'item': item,
        'quarantine_records': quarantine_records,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH', 'LAB_TECHNICIAN')
def quarantine_item_view(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if item.status == 'QUARANTINED':
        messages.warning(request, "This item is already quarantined.")
        return redirect('inventory:detail', pk=item.pk)

    if request.method == 'POST':
        form = QuarantineForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                record = form.save(commit=False)
                record.inventory_item = item
                record.quarantined_by = request.user
                record.save()

                item.status = 'QUARANTINED'
                item.save()

                log_audit(request.user, 'QUARANTINE', item, f"Quarantined unit {item.unit_identifier}: {record.get_reason_display()}", request=request)
                messages.warning(request, f"Unit {item.unit_identifier} has been placed in quarantine.")
                return redirect('inventory:detail', pk=item.pk)
    else:
        form = QuarantineForm()

    return render(request, 'inventory/quarantine_form.html', {'form': form, 'item': item})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def release_quarantine_view(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    active_quarantine = item.quarantine_records.filter(is_released=False).first()
    
    if not active_quarantine and item.status != 'QUARANTINED':
        messages.info(request, "This item is not currently quarantined.")
        return redirect('inventory:detail', pk=item.pk)

    if request.method == 'POST':
        form = QuarantineReleaseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                reason = form.cleaned_data['release_reason']
                if active_quarantine:
                    active_quarantine.is_released = True
                    active_quarantine.released_by = request.user
                    active_quarantine.release_date = timezone.now()
                    active_quarantine.release_reason = reason
                    active_quarantine.save()

                item.status = 'AVAILABLE'
                item.save()

                log_audit(request.user, 'RELEASE', item, f"Released unit {item.unit_identifier} from quarantine: {reason}", request=request)
                messages.success(request, f"Unit {item.unit_identifier} released from quarantine and is now AVAILABLE.")
                return redirect('inventory:detail', pk=item.pk)
    else:
        form = QuarantineReleaseForm()

    return render(request, 'inventory/release_quarantine_form.html', {
        'form': form,
        'item': item,
        'quarantine': active_quarantine,
    })

@login_required
def temperature_log_list_view(request):
    logs = TemperatureLog.objects.select_related('storage_device', 'recorded_by').all()[:50]
    devices = StorageDevice.objects.filter(is_active=True)
    return render(request, 'inventory/temperature_list.html', {
        'logs': logs,
        'devices': devices,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'BLOOD_BANK_TECH', 'LAB_TECHNICIAN')
def temperature_log_create_view(request):
    if request.method == 'POST':
        form = TemperatureLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.recorded_by = request.user
            log.save()
            log_audit(request.user, 'CREATE', log, f"Logged temperature {log.temperature_celsius}?C for {log.storage_device.name}", request=request)
            if log.threshold_status in ['HIGH_EXCURSION', 'LOW_EXCURSION', 'CRITICAL']:
                messages.warning(request, f"WARNING: Temperature excursion detected ({log.temperature_celsius}?C) on {log.storage_device.name}!")
            else:
                messages.success(request, "Temperature log recorded.")
            return redirect('inventory:temperature_list')
    else:
        form = TemperatureLogForm()
    return render(request, 'inventory/temperature_form.html', {'form': form})
