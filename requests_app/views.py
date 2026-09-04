from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from requests_app.models import BloodRequest, BloodRequestItem, InventoryReservation, BloodIssue, BloodReturn, DiscardRecord
from requests_app.forms import BloodRequestForm, BloodRequestItemForm, BloodIssueForm, BloodReturnForm, DiscardForm
from inventory.models import InventoryItem
from accounts.decorators import role_required
from audit.utils import log_audit
from notifications.models import Notification

@login_required
def request_list_view(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    urgency = request.GET.get('urgency', '')

    queryset = BloodRequest.objects.select_related('hospital', 'patient', 'requested_by_user').all()

    # Hospital users only see their hospital requests
    if hasattr(request.user, 'profile') and request.user.profile.role == 'HOSPITAL_USER':
        if request.user.profile.hospital:
            queryset = queryset.filter(hospital=request.user.profile.hospital)
        else:
            queryset = queryset.none()

    if search:
        queryset = queryset.filter(request_id__icontains=search) | queryset.filter(patient__first_name__icontains=search) | queryset.filter(patient__last_name__icontains=search) | queryset.filter(hospital__name__icontains=search)
    if status:
        queryset = queryset.filter(status=status)
    if urgency:
        queryset = queryset.filter(urgency=urgency)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'requests_app/request_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'urgency': urgency,
        'statuses': BloodRequest.STATUS_CHOICES,
        'urgency_choices': BloodRequest.URGENCY_CHOICES,
    })

@login_required
def request_create_view(request):
    is_hospital_user = hasattr(request.user, 'profile') and request.user.profile.role == 'HOSPITAL_USER'
    initial = {
        'required_date_time': timezone.now() + timedelta(hours=4),
        'urgency': 'NORMAL',
    }
    if is_hospital_user and request.user.profile.hospital:
        initial['hospital'] = request.user.profile.hospital

    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        item_form = BloodRequestItemForm(request.POST)
        if form.is_valid() and item_form.is_valid():
            with transaction.atomic():
                blood_request = form.save(commit=False)
                blood_request.requested_by_user = request.user
                blood_request.status = 'SUBMITTED'
                blood_request.save()

                item = item_form.save(commit=False)
                item.request = blood_request
                item.status = 'PENDING'
                item.save()

                log_audit(request.user, 'CREATE', blood_request, f"Submitted blood request {blood_request.request_id} ({blood_request.urgency})", request=request)
                
                # If EMERGENCY request, trigger emergency alert
                if blood_request.urgency == 'EMERGENCY':
                    from django.contrib.auth.models import User
                    staff_users = User.objects.filter(profile__role__in=['SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER'])
                    for staff in staff_users:
                        Notification.objects.create(
                            recipient=staff,
                            notification_type='EMERGENCY_REQUEST',
                            title=f"🚨 EMERGENCY Blood Request: {blood_request.request_id}",
                            message=f"STAT emergency request for {item.units_requested}x {item.get_component_type_display()} [{item.blood_group}] at {blood_request.hospital.name}.",
                            link_url=f"/requests/{blood_request.pk}/"
                        )

                messages.success(request, f"Blood request {blood_request.request_id} submitted successfully.")
                return redirect('requests_app:detail', pk=blood_request.pk)
    else:
        form = BloodRequestForm(initial=initial)
        item_form = BloodRequestItemForm(initial={'units_requested': 1, 'component_type': 'PRBC', 'blood_group': 'O+'})

    return render(request, 'requests_app/request_form.html', {
        'form': form,
        'item_form': item_form,
        'action_title': 'Submit Blood Requisition',
    })

@login_required
def request_detail_view(request, pk):
    blood_request = get_object_or_404(BloodRequest.objects.select_related('hospital', 'patient', 'blood_bank', 'requested_by_user', 'reviewed_by'), pk=pk)
    items = blood_request.items.prefetch_related('reservations__inventory_item').all()
    issues = blood_request.issues.select_related('inventory_item', 'issued_by', 'authorized_by').all()
    
    return render(request, 'requests_app/request_detail.html', {
        'request': blood_request,
        'items': items,
        'issues': issues,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def request_review_view(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        
        with transaction.atomic():
            if action == 'APPROVE':
                blood_request.status = 'APPROVED'
                blood_request.reviewed_by = request.user
                blood_request.review_timestamp = timezone.now()
                blood_request.save()
                log_audit(request.user, 'APPROVE', blood_request, f"Approved request {blood_request.request_id}", request=request)
                messages.success(request, f"Request {blood_request.request_id} has been APPROVED.")
            elif action == 'REJECT':
                blood_request.status = 'REJECTED'
                blood_request.reviewed_by = request.user
                blood_request.review_timestamp = timezone.now()
                blood_request.rejection_reason = reason
                blood_request.save()
                log_audit(request.user, 'REJECT', blood_request, f"Rejected request {blood_request.request_id}: {reason}", request=request)
                messages.warning(request, f"Request {blood_request.request_id} has been REJECTED.")
                
            return redirect('requests_app:detail', pk=blood_request.pk)

    return render(request, 'requests_app/request_review.html', {'request': blood_request})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def reserve_inventory_view(request, item_pk):
    req_item = get_object_or_404(BloodRequestItem.objects.select_related('request'), pk=item_pk)
    blood_request = req_item.request

    # Find matching available units
    available_units = InventoryItem.objects.filter(
        component_type=req_item.component_type,
        blood_group=req_item.blood_group,
        status='AVAILABLE',
        expiry_date__gt=timezone.now(),
        is_locked=False
    ).select_related('blood_bag', 'component')

    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        
        # ATOMIC CONCURRENCY RESERVATION LOCKING
        with transaction.atomic():
            # Lock the target unit row with select_for_update
            target_unit = InventoryItem.objects.select_for_update().filter(
                pk=unit_id,
                status='AVAILABLE',
                expiry_date__gt=timezone.now(),
                is_locked=False
            ).first()

            if not target_unit:
                messages.error(request, "CONCURRENCY CONFLICT: Selected unit is no longer available or was just reserved by another technician.")
                return redirect('requests_app:reserve_inventory', item_pk=req_item.pk)

            # Create reservation record
            reservation = InventoryReservation.objects.create(
                request_item=req_item,
                inventory_item=target_unit,
                reserved_by=request.user,
                is_active=True
            )

            # Update unit status atomically
            target_unit.status = 'RESERVED'
            target_unit.save()

            # Update request item units_reserved count
            req_item.units_reserved += 1
            if req_item.units_reserved >= req_item.units_requested:
                req_item.status = 'RESERVED'
            req_item.save()

            # Update blood request status
            blood_request.status = 'RESERVED'
            blood_request.save()

            log_audit(request.user, 'RESERVE', target_unit, f"Atomically reserved unit {target_unit.unit_identifier} for Request {blood_request.request_id}", request=request)
            messages.success(request, f"Unit {target_unit.unit_identifier} successfully reserved.")
            return redirect('requests_app:detail', pk=blood_request.pk)

    return render(request, 'requests_app/reserve_unit.html', {
        'req_item': req_item,
        'request': blood_request,
        'available_units': available_units,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def cancel_reservation_view(request, rsv_pk):
    reservation = get_object_or_404(InventoryReservation.objects.select_related('inventory_item', 'request_item', 'request_item__request'), pk=rsv_pk)
    
    if request.method == 'POST':
        with transaction.atomic():
            unit = InventoryItem.objects.select_for_update().get(pk=reservation.inventory_item.pk)
            unit.status = 'AVAILABLE'
            unit.save()

            reservation.is_active = False
            reservation.cancelled_at = timezone.now()
            reservation.cancellation_reason = request.POST.get('cancellation_reason', 'Cancelled by technician')
            reservation.save()

            req_item = reservation.request_item
            if req_item.units_reserved > 0:
                req_item.units_reserved -= 1
                req_item.status = 'PENDING'
                req_item.save()

            log_audit(request.user, 'CANCEL_RESERVATION', unit, f"Cancelled reservation on unit {unit.unit_identifier}", request=request)
            messages.info(request, f"Reservation cancelled. Unit {unit.unit_identifier} is back in available inventory.")
            return redirect('requests_app:detail', pk=req_item.request.pk)

    return render(request, 'requests_app/cancel_reservation.html', {'reservation': reservation})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def issue_blood_view(request, rsv_pk):
    reservation = get_object_or_404(InventoryReservation.objects.select_related('inventory_item', 'request_item__request__patient', 'request_item__request__hospital'), pk=rsv_pk)
    blood_request = reservation.request_item.request
    unit = reservation.inventory_item

    if unit.status != 'RESERVED':
        messages.error(request, f"Unit {unit.unit_identifier} cannot be issued: Current status is {unit.get_status_display()}.")
        return redirect('requests_app:detail', pk=blood_request.pk)

    if unit.expiry_date <= timezone.now():
        messages.error(request, f"CRITICAL SAFETY VIOLATION: Unit {unit.unit_identifier} has EXPIRED and cannot be issued!")
        return redirect('requests_app:detail', pk=blood_request.pk)

    if request.method == 'POST':
        form = BloodIssueForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                issue = form.save(commit=False)
                issue.request = blood_request
                issue.inventory_item = unit
                issue.patient = blood_request.patient
                issue.issued_by = request.user
                issue.authorized_by = request.user
                issue.status = 'ISSUED'
                issue.save()

                unit.status = 'ISSUED'
                unit.save()

                reservation.is_active = False
                reservation.save()

                req_item = reservation.request_item
                req_item.units_issued += 1
                if req_item.units_issued >= req_item.units_requested:
                    req_item.status = 'ISSUED'
                req_item.save()

                # Check if all items in request are issued
                all_issued = all(i.units_issued >= i.units_requested for i in blood_request.items.all())
                if all_issued:
                    blood_request.status = 'ISSUED'
                else:
                    blood_request.status = 'PARTIALLY_FULFILLED'
                blood_request.save()

                log_audit(request.user, 'ISSUE', unit, f"Issued unit {unit.unit_identifier} to {issue.recipient_name} for patient {blood_request.patient.full_name}", request=request)
                messages.success(request, f"Blood Issue {issue.issue_id} successfully processed for unit {unit.unit_identifier}.")
                return redirect('requests_app:detail', pk=blood_request.pk)
    else:
        form = BloodIssueForm(initial={
            'recipient_name': f"Hospital Courier / {blood_request.hospital.name}",
            'crossmatch_compatible': True,
            'crossmatch_details': "Crossmatch Compatible (Major/Minor Tube Method)",
        })

    return render(request, 'requests_app/issue_form.html', {
        'form': form,
        'reservation': reservation,
        'request': blood_request,
        'unit': unit,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def return_blood_view(request, issue_pk):
    issue = get_object_or_404(BloodIssue.objects.select_related('inventory_item', 'request', 'patient'), pk=issue_pk)
    unit = issue.inventory_item

    if hasattr(issue, 'return_record'):
        messages.warning(request, "This issue has already been logged as returned.")
        return redirect('requests_app:detail', pk=issue.request.pk)

    if request.method == 'POST':
        form = BloodReturnForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                ret = form.save(commit=False)
                ret.blood_issue = issue
                ret.received_by = request.user
                ret.assessed_by = request.user
                ret.save()

                issue.status = 'RETURNED'
                issue.save()

                # Apply disposition to inventory item
                if ret.disposition == 'RE_ENTRY_APPROVED':
                    unit.status = 'AVAILABLE'
                elif ret.disposition == 'QUARANTINE_FOR_INVESTIGATION':
                    unit.status = 'QUARANTINED'
                elif ret.disposition == 'DISCARD_ORDERED':
                    unit.status = 'DISCARDED'
                unit.save()

                log_audit(request.user, 'RETURN', unit, f"Recorded blood return {ret.return_id} with disposition: {ret.get_disposition_display()}", request=request)
                messages.success(request, f"Blood return {ret.return_id} logged with disposition: {ret.get_disposition_display()}.")
                return redirect('requests_app:detail', pk=issue.request.pk)
    else:
        form = BloodReturnForm(initial={
            'cold_chain_maintained': True,
            'visual_inspection_passed': True,
            'bag_seal_intact': True,
            'disposition': 'QUARANTINE_FOR_INVESTIGATION',
        })

    return render(request, 'requests_app/return_form.html', {
        'form': form,
        'issue': issue,
        'unit': unit,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def discard_unit_view(request, inv_pk):
    unit = get_object_or_404(InventoryItem, pk=inv_pk)
    if unit.status == 'DISCARDED':
        messages.warning(request, "This unit is already discarded.")
        return redirect('inventory:detail', pk=unit.pk)

    if request.method == 'POST':
        form = DiscardForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                discard = form.save(commit=False)
                discard.inventory_item = unit
                discard.discarded_by = request.user
                discard.authorized_by = request.user
                discard.save()

                unit.status = 'DISCARDED'
                unit.save()

                # Also update blood bag / component status
                if unit.blood_bag:
                    unit.blood_bag.status = 'DISCARDED'
                    unit.blood_bag.save()
                if unit.component:
                    unit.component.status = 'DISCARDED'
                    unit.component.save()

                log_audit(request.user, 'DISCARD', unit, f"Authorized biohazard discard {discard.discard_id}: {discard.get_discard_reason_display()}", request=request)
                messages.warning(request, f"Unit {unit.unit_identifier} has been authorized for biohazard discard ({discard.discard_id}).")
                return redirect('inventory:detail', pk=unit.pk)
    else:
        reason_initial = 'EXPIRED' if unit.expiry_date <= timezone.now() else 'QUALITY_FAILURE'
        form = DiscardForm(initial={'discard_reason': reason_initial})

    return render(request, 'requests_app/discard_form.html', {'form': form, 'unit': unit})
