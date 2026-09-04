from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from camps.models import BloodCamp, CampRegistration
from camps.forms import BloodCampForm
from accounts.decorators import role_required
from audit.utils import log_audit
from donors.models import Donor

@login_required
def camp_list_view(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    queryset = BloodCamp.objects.select_related('blood_bank', 'coordinator').all()
    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(city__icontains=search) | queryset.filter(camp_id__icontains=search)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'camps/camp_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'statuses': BloodCamp.STATUS_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'RECEPTIONIST')
def camp_create_view(request):
    if request.method == 'POST':
        form = BloodCampForm(request.POST)
        if form.is_valid():
            camp = form.save()
            log_audit(request.user, 'CREATE', camp, f"Created blood camp {camp.name}", request=request)
            messages.success(request, f"Blood camp {camp.name} created successfully.")
            return redirect('camps:detail', pk=camp.pk)
    else:
        form = BloodCampForm()
    return render(request, 'camps/camp_form.html', {'form': form, 'action_title': 'Plan Blood Donation Camp'})

@login_required
def camp_detail_view(request, pk):
    camp = get_object_or_404(BloodCamp.objects.select_related('blood_bank', 'coordinator'), pk=pk)
    registrations = camp.registrations.select_related('donor').all()
    return render(request, 'camps/camp_detail.html', {
        'camp': camp,
        'registrations': registrations,
    })

@login_required
def camp_register_donor_view(request, pk):
    camp = get_object_or_404(BloodCamp, pk=pk)
    donor = None
    if hasattr(request.user, 'profile') and request.user.profile.donor_profile:
        donor = request.user.profile.donor_profile
    else:
        donor = Donor.objects.filter(user=request.user).first()
        
    if not donor:
        messages.error(request, "Only registered donors can register for blood camps.")
        return redirect('camps:detail', pk=pk)

    registration, created = CampRegistration.objects.get_or_create(camp=camp, donor=donor)
    if created:
        messages.success(request, f"You are successfully registered for {camp.name}!")
        log_audit(request.user, 'CREATE', registration, f"Registered for camp {camp.name}", request=request)
    else:
        messages.info(request, "You are already registered for this camp.")
    return redirect('camps:detail', pk=pk)
