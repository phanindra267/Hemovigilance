from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from accounts.models import UserProfile, Role
from accounts.forms import (
    LifeFlowLoginForm, DonorRegistrationUserForm,
    HospitalUserRegistrationForm, UserProfileUpdateForm,
    StaffUserCreateForm
)
from accounts.decorators import role_required
from audit.utils import log_audit
from donors.models import Donor

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LifeFlowLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_audit(user, 'LOGIN', user, "User logged in successfully", request=request)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LifeFlowLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        log_audit(request.user, 'LOGOUT', request.user, "User logged out", request=request)
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

def register_donor_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = DonorRegistrationUserForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                donor = Donor.objects.create(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    dob=form.cleaned_data['dob'],
                    gender=form.cleaned_data['gender'],
                    blood_group=form.cleaned_data['blood_group'],
                    phone=form.cleaned_data['phone'],
                    email=form.cleaned_data['email'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    district=form.cleaned_data['district'],
                    state=form.cleaned_data['state'],
                    postal_code=form.cleaned_data['postal_code'],
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = Role.DONOR
                profile.phone = form.cleaned_data['phone']
                profile.donor_profile = donor
                profile.save()

                log_audit(user, 'CREATE', donor, f"Public self-registration for donor {donor.full_name}", request=request)
                login(request, user)
                messages.success(request, f"Registration complete! Welcome to LIFEFlow, {donor.full_name}.")
                return redirect('accounts:dashboard')
    else:
        form = DonorRegistrationUserForm()
    return render(request, 'accounts/register_donor.html', {'form': form})

def register_hospital_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = HospitalUserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = Role.HOSPITAL_USER
                profile.phone = form.cleaned_data['phone']
                profile.hospital = form.cleaned_data['hospital']
                profile.employee_id = form.cleaned_data['employee_id']
                profile.save()

                log_audit(user, 'CREATE', profile, f"Hospital user registered for {profile.hospital.name}", request=request)
                login(request, user)
                messages.success(request, "Hospital account registered successfully.")
                return redirect('accounts:dashboard')
    else:
        form = HospitalUserRegistrationForm()
    return render(request, 'accounts/register_hospital.html', {'form': form})

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            log_audit(request.user, 'UPDATE', profile, "Updated user profile", request=request)
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    role = profile.role if not request.user.is_superuser else Role.SUPER_ADMIN

    # Statistics & Data depending on role
    from inventory.models import InventoryItem
    from requests_app.models import BloodRequest
    from donations.models import Donation
    from laboratory.models import BloodBag, LabSample
    from appointments.models import Appointment
    from camps.models import BloodCamp

    context = {
        'role': role,
        'profile': profile,
    }

    if role in [Role.SUPER_ADMIN, Role.BLOOD_BANK_ADMIN, Role.MEDICAL_OFFICER, Role.BLOOD_BANK_TECH, Role.RECEPTIONIST]:
        context.update({
            'total_available_units': InventoryItem.objects.filter(status='AVAILABLE').count(),
            'total_quarantined_units': InventoryItem.objects.filter(status='QUARANTINED').count(),
            'total_pending_requests': BloodRequest.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count(),
            'total_donors_count': Donor.objects.count(),
            'today_donations_count': Donation.objects.filter(collection_date__date=Donation.objects.none()).count() if False else Donation.objects.count(),
            'pending_samples_count': LabSample.objects.filter(status__in=['PENDING', 'IN_TESTING']).count(),
            'recent_donations': Donation.objects.select_related('donor').order_by('-collection_date')[:5],
            'recent_requests': BloodRequest.objects.select_related('hospital', 'patient').order_by('-created_at')[:5],
            'active_camps': BloodCamp.objects.filter(status__in=['PLANNED', 'ACTIVE'])[:3],
        })
    elif role == Role.LAB_TECHNICIAN:
        context.update({
            'pending_samples': LabSample.objects.filter(status__in=['PENDING', 'IN_TESTING']).select_related('blood_bag')[:10],
            'recent_bags': BloodBag.objects.order_by('-collection_date')[:10],
        })
    elif role == Role.HOSPITAL_USER:
        hospital = profile.hospital
        context.update({
            'hospital': hospital,
            'hospital_requests': BloodRequest.objects.filter(hospital=hospital).order_by('-created_at')[:10] if hospital else [],
            'pending_hospital_requests': BloodRequest.objects.filter(hospital=hospital, status__in=['SUBMITTED', 'UNDER_REVIEW', 'APPROVED']).count() if hospital else 0,
        })
    elif role == Role.DONOR:
        donor = profile.donor_profile or Donor.objects.filter(user=request.user).first()
        context.update({
            'donor': donor,
            'my_donations': Donation.objects.filter(donor=donor).order_by('-collection_date') if donor else [],
            'my_appointments': Appointment.objects.filter(donor=donor).order_by('-scheduled_date') if donor else [],
            'upcoming_camps': BloodCamp.objects.filter(status__in=['PLANNED', 'ACTIVE']).order_by('start_date')[:5],
        })

    return render(request, 'accounts/dashboard.html', context)

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN')
def user_list_view(request):
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    queryset = User.objects.select_related('profile').all().order_by('-date_joined')
    if search:
        queryset = queryset.filter(username__icontains=search) | queryset.filter(first_name__icontains=search) | queryset.filter(last_name__icontains=search) | queryset.filter(email__icontains=search)
    if role:
        queryset = queryset.filter(profile__role=role)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'accounts/user_list.html', {
        'page_obj': page_obj,
        'search': search,
        'role': role,
        'roles': Role.choices,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN')
def user_create_view(request):
    if request.method == 'POST':
        form = StaffUserCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = form.cleaned_data['role']
                profile.phone = form.cleaned_data['phone']
                profile.employee_id = form.cleaned_data['employee_id']
                profile.license_number = form.cleaned_data['license_number']
                profile.save()

                log_audit(request.user, 'CREATE', user, f"Created staff user {user.username} with role {profile.role}", request=request)
                messages.success(request, f"User {user.username} created successfully.")
                return redirect('accounts:user_list')
    else:
        form = StaffUserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'action_title': 'Add System / Staff User'})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN')
def user_toggle_status_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:user_list')
    target_user.is_active = not target_user.is_active
    target_user.save()
    status_str = "activated" if target_user.is_active else "deactivated"
    log_audit(request.user, 'UPDATE', target_user, f"User account {status_str}", request=request)
    messages.success(request, f"User {target_user.username} has been {status_str}.")
    return redirect('accounts:user_list')
