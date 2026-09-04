from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from patients.models import Patient
from patients.forms import PatientForm
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def patient_list_view(request):
    search = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')
    queryset = Patient.objects.select_related('hospital').all()
    if search:
        queryset = queryset.filter(first_name__icontains=search) | queryset.filter(last_name__icontains=search) | queryset.filter(patient_id__icontains=search) | queryset.filter(hospital_mrn__icontains=search)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'patients/patient_list.html', {
        'page_obj': page_obj,
        'search': search,
        'blood_group': blood_group,
        'blood_groups': Patient.BLOOD_GROUP_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'RECEPTIONIST', 'HOSPITAL_USER')
def patient_create_view(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            log_audit(request.user, 'CREATE', patient, f"Registered patient {patient.full_name} ({patient.patient_id})", request=request)
            messages.success(request, f"Patient {patient.full_name} ({patient.patient_id}) created.")
            return redirect('patients:detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form, 'action_title': 'Register Patient'})

@login_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient.objects.select_related('hospital'), pk=pk)
    from requests_app.models import BloodRequest, BloodIssue
    requests = BloodRequest.objects.filter(patient=patient).order_by('-created_at')[:10]
    issues = BloodIssue.objects.filter(patient=patient).order_by('-issued_at')[:10]
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'requests': requests,
        'issues': issues,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'RECEPTIONIST')
def patient_update_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            log_audit(request.user, 'UPDATE', patient, f"Updated patient {patient.full_name}", request=request)
            messages.success(request, f"Patient {patient.full_name} updated.")
            return redirect('patients:detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'patient': patient, 'action_title': 'Edit Patient'})
