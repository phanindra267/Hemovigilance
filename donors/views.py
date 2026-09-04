from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from donors.models import Donor, EligibilityAssessment
from donors.forms import DonorRegistrationForm, EligibilityAssessmentForm
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def donor_list_view(request):
    search = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')
    donor_status = request.GET.get('status', '')

    queryset = Donor.objects.all()
    if search:
        queryset = queryset.filter(first_name__icontains=search) | queryset.filter(last_name__icontains=search) | queryset.filter(donor_id__icontains=search) | queryset.filter(phone__icontains=search)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if donor_status:
        queryset = queryset.filter(donor_status=donor_status)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'donors/donor_list.html', {
        'page_obj': page_obj,
        'search': search,
        'blood_group': blood_group,
        'donor_status': donor_status,
        'blood_groups': Donor.BLOOD_GROUP_CHOICES,
        'statuses': Donor.DONOR_STATUS_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'RECEPTIONIST', 'BLOOD_BANK_TECH')
def donor_create_view(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save()
            log_audit(request.user, 'CREATE', donor, f"Registered new donor {donor.full_name} ({donor.donor_id})", request=request)
            messages.success(request, f"Donor {donor.full_name} ({donor.donor_id}) successfully registered.")
            return redirect('donors:detail', pk=donor.pk)
    else:
        form = DonorRegistrationForm()
    return render(request, 'donors/donor_form.html', {'form': form, 'action_title': 'Register New Donor'})

@login_required
def donor_detail_view(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    assessments = donor.eligibility_assessments.order_by('-assessment_date')[:5]
    
    # Donations and appointments
    from donations.models import Donation
    from appointments.models import Appointment
    donations = Donation.objects.filter(donor=donor).order_by('-collection_date')[:10]
    appointments = Appointment.objects.filter(donor=donor).order_by('-scheduled_date')[:5]
    
    return render(request, 'donors/donor_detail.html', {
        'donor': donor,
        'assessments': assessments,
        'donations': donations,
        'appointments': appointments,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'RECEPTIONIST')
def donor_update_view(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, instance=donor)
        if form.is_valid():
            donor = form.save()
            log_audit(request.user, 'UPDATE', donor, f"Updated donor {donor.full_name}", request=request)
            messages.success(request, f"Donor {donor.full_name} updated successfully.")
            return redirect('donors:detail', pk=donor.pk)
    else:
        form = DonorRegistrationForm(instance=donor)
    return render(request, 'donors/donor_form.html', {'form': form, 'donor': donor, 'action_title': 'Edit Donor'})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def eligibility_assessment_create_view(request, donor_pk):
    donor = get_object_or_404(Donor, pk=donor_pk)
    if request.method == 'POST':
        form = EligibilityAssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.donor = donor
            assessment.assessed_by = request.user
            assessment.save()
            
            # Update donor status based on assessment
            if assessment.status == 'ELIGIBLE':
                donor.donor_status = 'ACTIVE'
            elif assessment.status == 'TEMPORARILY_DEFERRED':
                donor.donor_status = 'TEMPORARILY_DEFERRED'
                if assessment.deferral_end_date:
                    donor.next_eligible_date = assessment.deferral_end_date
            elif assessment.status == 'PERMANENTLY_DEFERRED':
                donor.donor_status = 'PERMANENTLY_DEFERRED'
            elif assessment.status == 'REJECTED':
                donor.donor_status = 'BLOCKED'
            donor.save()
            
            log_audit(request.user, 'APPROVE' if assessment.status == 'ELIGIBLE' else 'REJECT', assessment, f"Completed eligibility assessment for {donor.full_name}: {assessment.get_status_display()}", request=request)
            messages.success(request, f"Eligibility assessment recorded: {assessment.get_status_display()}")
            return redirect('donors:detail', pk=donor.pk)
    else:
        form = EligibilityAssessmentForm(initial={
            'donor': donor,
            'status': 'ELIGIBLE',
            'weight_kg': 65.0,
            'hemoglobin_g_dl': 13.5,
            'systolic_bp': 120,
            'diastolic_bp': 80,
            'pulse_bpm': 72,
            'temperature_c': 36.6,
        })
    return render(request, 'donors/assessment_form.html', {'form': form, 'donor': donor})
