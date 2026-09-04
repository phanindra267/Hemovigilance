from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from hospitals.models import Hospital
from hospitals.forms import HospitalForm
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def hospital_list_view(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    queryset = Hospital.objects.all()
    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(code__icontains=search) | queryset.filter(city__icontains=search)
    if category:
        queryset = queryset.filter(category=category)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'hospitals/hospital_list.html', {
        'page_obj': page_obj,
        'search': search,
        'category': category,
        'categories': Hospital.CATEGORY_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'RECEPTIONIST')
def hospital_create_view(request):
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            hospital = form.save()
            log_audit(request.user, 'CREATE', hospital, f"Registered hospital {hospital.name}", request=request)
            messages.success(request, f"Hospital {hospital.name} successfully registered.")
            return redirect('hospitals:detail', pk=hospital.pk)
    else:
        form = HospitalForm()
    return render(request, 'hospitals/hospital_form.html', {'form': form, 'action_title': 'Register Hospital'})

@login_required
def hospital_detail_view(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    # Get associated blood requests
    from requests_app.models import BloodRequest
    recent_requests = BloodRequest.objects.filter(hospital=hospital).order_by('-created_at')[:10]
    return render(request, 'hospitals/hospital_detail.html', {
        'hospital': hospital,
        'recent_requests': recent_requests,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN')
def hospital_update_view(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            hospital = form.save()
            log_audit(request.user, 'UPDATE', hospital, f"Updated hospital {hospital.name}", request=request)
            messages.success(request, f"Hospital {hospital.name} updated.")
            return redirect('hospitals:detail', pk=hospital.pk)
    else:
        form = HospitalForm(instance=hospital)
    return render(request, 'hospitals/hospital_form.html', {'form': form, 'hospital': hospital, 'action_title': 'Edit Hospital'})
