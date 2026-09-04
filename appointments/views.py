from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from appointments.models import Appointment
from appointments.forms import AppointmentForm, DonorSelfAppointmentForm
from accounts.decorators import role_required
from audit.utils import log_audit
from donors.models import Donor

@login_required
def appointment_list_view(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    date = request.GET.get('date', '')

    queryset = Appointment.objects.select_related('donor', 'blood_bank', 'camp').all()

    # Donor only sees their appointments
    if hasattr(request.user, 'profile') and request.user.profile.role == 'DONOR':
        donor = request.user.profile.donor_profile or Donor.objects.filter(user=request.user).first()
        queryset = queryset.filter(donor=donor)

    if search:
        queryset = queryset.filter(donor__first_name__icontains=search) | queryset.filter(donor__last_name__icontains=search) | queryset.filter(appointment_id__icontains=search)
    if status:
        queryset = queryset.filter(status=status)
    if date:
        queryset = queryset.filter(scheduled_date=date)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'appointments/appointment_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'date': date,
        'statuses': Appointment.STATUS_CHOICES,
    })

@login_required
def appointment_create_view(request):
    is_donor = hasattr(request.user, 'profile') and request.user.profile.role == 'DONOR'
    donor = None
    if is_donor:
        donor = request.user.profile.donor_profile or Donor.objects.filter(user=request.user).first()
        if not donor:
            messages.error(request, "Donor profile missing. Please register as a donor first.")
            return redirect('donors:create')

    if request.method == 'POST':
        if is_donor:
            form = DonorSelfAppointmentForm(request.POST)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.donor = donor
                appointment.save()
                log_audit(request.user, 'CREATE', appointment, f"Scheduled donation appointment for {donor.full_name}", request=request)
                messages.success(request, "Your appointment has been scheduled successfully!")
                return redirect('appointments:list')
        else:
            form = AppointmentForm(request.POST)
            if form.is_valid():
                appointment = form.save()
                log_audit(request.user, 'CREATE', appointment, f"Scheduled appointment for donor {appointment.donor.full_name}", request=request)
                messages.success(request, f"Appointment {appointment.appointment_id} scheduled.")
                return redirect('appointments:list')
    else:
        if is_donor:
            form = DonorSelfAppointmentForm(initial={'scheduled_date': timezone.now().date()})
        else:
            form = AppointmentForm(initial={'scheduled_date': timezone.now().date()})
    return render(request, 'appointments/appointment_form.html', {'form': form, 'is_donor': is_donor})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'RECEPTIONIST', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def appointment_checkin_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status != 'SCHEDULED':
        messages.warning(request, f"Appointment is already {appointment.get_status_display()}.")
        return redirect('appointments:list')
    appointment.status = 'CHECKED_IN'
    appointment.checked_in_at = timezone.now()
    appointment.save()
    log_audit(request.user, 'CHECK_IN', appointment, f"Checked in donor {appointment.donor.full_name} for appointment", request=request)
    messages.success(request, f"Donor {appointment.donor.full_name} successfully checked in. Ready for screening & donation.")
    return redirect('donations:create_from_appointment', appointment_pk=appointment.pk)

@login_required
def appointment_cancel_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', 'Cancelled by user')
        appointment.status = 'CANCELLED'
        appointment.cancellation_reason = reason
        appointment.save()
        log_audit(request.user, 'CANCEL', appointment, f"Cancelled appointment: {reason}", request=request)
        messages.info(request, "Appointment has been cancelled.")
        return redirect('appointments:list')
    return render(request, 'appointments/appointment_cancel.html', {'appointment': appointment})
