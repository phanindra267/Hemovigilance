from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from donations.models import Donation
from donations.forms import DonationForm
from donors.models import Donor, EligibilityAssessment
from appointments.models import Appointment
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def donation_list_view(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    donation_type = request.GET.get('donation_type', '')

    queryset = Donation.objects.select_related('donor', 'blood_bank', 'collected_by').all()
    if search:
        queryset = queryset.filter(donor__first_name__icontains=search) | queryset.filter(donor__last_name__icontains=search) | queryset.filter(donation_id__icontains=search)
    if status:
        queryset = queryset.filter(status=status)
    if donation_type:
        queryset = queryset.filter(donation_type=donation_type)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'donations/donation_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'donation_type': donation_type,
        'statuses': Donation.STATUS_CHOICES,
        'donation_types': Donation.DONATION_TYPE_CHOICES,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH', 'RECEPTIONIST')
def donation_create_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                donation = form.save(commit=False)
                if not donation.collected_by:
                    donation.collected_by = request.user
                donation.save()
                
                # If collected, create blood bag and sample
                if donation.status in ['COLLECTED', 'COMPLETED']:
                    from laboratory.models import BloodBag, LabSample
                    from inventory.models import InventoryItem
                    
                    # Update donor stats
                    donor = donation.donor
                    donor.last_donation_date = timezone.now().date()
                    donor.next_eligible_date = timezone.now().date() + timedelta(days=90) # standard interval
                    donor.total_donations_count += 1
                    donor.save()
                    
                    # Create BloodBag
                    expiry = timezone.now() + timedelta(days=35) # 35 days for CPDA-1 Whole Blood
                    blood_bag, _ = BloodBag.objects.get_or_create(
                        donation=donation,
                        defaults={
                            'blood_group': donor.blood_group,
                            'rh_factor': donor.rh_factor,
                            'collection_date': donation.collection_date,
                            'expiry_date': expiry,
                            'bag_type': donation.bag_type,
                            'volume_ml': donation.volume_ml,
                            'status': 'QUARANTINED',
                            'storage_location': 'Quarantine Storage Area #1',
                        }
                    )
                    
                    # Create LabSample for screening
                    sample, _ = LabSample.objects.get_or_create(
                        blood_bag=blood_bag,
                        defaults={
                            'collected_at': timezone.now(),
                            'collected_by': request.user,
                            'status': 'PENDING'
                        }
                    )
                    
                    # Create initial InventoryItem in QUARANTINED state
                    InventoryItem.objects.get_or_create(
                        blood_bag=blood_bag,
                        defaults={
                            'item_type': 'WHOLE_BLOOD_BAG',
                            'blood_group': blood_bag.blood_group,
                            'rh_factor': blood_bag.rh_factor,
                            'component_type': 'WHOLE_BLOOD',
                            'volume_ml': blood_bag.volume_ml,
                            'collection_date': blood_bag.collection_date,
                            'expiry_date': blood_bag.expiry_date,
                            'status': 'QUARANTINED',
                        }
                    )
                    
                    log_audit(request.user, 'CREATE', blood_bag, f"Blood Bag {blood_bag.bag_id} registered and quarantined pending lab screening", request=request)

                log_audit(request.user, 'CREATE', donation, f"Recorded blood donation {donation.donation_id} for donor {donation.donor.full_name}", request=request)
                messages.success(request, f"Donation {donation.donation_id} successfully recorded.")
                return redirect('donations:detail', pk=donation.pk)
    else:
        form = DonationForm(initial={'status': 'COLLECTED'})
    return render(request, 'donations/donation_form.html', {'form': form, 'action_title': 'Record Blood Donation'})

@login_required
def donation_detail_view(request, pk):
    donation = get_object_or_404(Donation.objects.select_related('donor', 'blood_bank', 'collected_by', 'appointment', 'assessment'), pk=pk)
    blood_bag = getattr(donation, 'blood_bag', None)
    return render(request, 'donations/donation_detail.html', {
        'donation': donation,
        'blood_bag': blood_bag,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER', 'BLOOD_BANK_TECH')
def donation_create_from_appointment_view(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    donor = appointment.donor
    
    # Check latest assessment
    latest_assessment = donor.eligibility_assessments.order_by('-assessment_date').first()
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                donation = form.save(commit=False)
                donation.donor = donor
                donation.appointment = appointment
                donation.camp = appointment.camp
                donation.blood_bank = appointment.blood_bank or form.cleaned_data.get('blood_bank')
                donation.collected_by = request.user
                donation.save()
                
                appointment.status = 'COMPLETED'
                appointment.completed_at = timezone.now()
                appointment.save()

                # Create blood bag & sample
                if donation.status in ['COLLECTED', 'COMPLETED']:
                    from laboratory.models import BloodBag, LabSample
                    from inventory.models import InventoryItem
                    
                    donor.last_donation_date = timezone.now().date()
                    donor.next_eligible_date = timezone.now().date() + timedelta(days=90)
                    donor.total_donations_count += 1
                    donor.save()
                    
                    expiry = timezone.now() + timedelta(days=35)
                    blood_bag = BloodBag.objects.create(
                        donation=donation,
                        blood_group=donor.blood_group,
                        rh_factor=donor.rh_factor,
                        collection_date=donation.collection_date,
                        expiry_date=expiry,
                        bag_type=donation.bag_type,
                        volume_ml=donation.volume_ml,
                        status='QUARANTINED',
                        storage_location='Quarantine Storage Area #1',
                    )
                    
                    LabSample.objects.create(
                        blood_bag=blood_bag,
                        collected_at=timezone.now(),
                        collected_by=request.user,
                        status='PENDING'
                    )
                    
                    InventoryItem.objects.create(
                        blood_bag=blood_bag,
                        item_type='WHOLE_BLOOD_BAG',
                        blood_group=blood_bag.blood_group,
                        rh_factor=blood_bag.rh_factor,
                        component_type='WHOLE_BLOOD',
                        volume_ml=blood_bag.volume_ml,
                        collection_date=blood_bag.collection_date,
                        expiry_date=blood_bag.expiry_date,
                        status='QUARANTINED',
                    )

                log_audit(request.user, 'CREATE', donation, f"Completed appointment {appointment.appointment_id} with donation {donation.donation_id}", request=request)
                messages.success(request, f"Donation {donation.donation_id} completed and Blood Bag created.")
                return redirect('donations:detail', pk=donation.pk)
    else:
        initial = {
            'donor': donor,
            'appointment': appointment,
            'camp': appointment.camp,
            'blood_bank': appointment.blood_bank,
            'assessment': latest_assessment,
            'status': 'COLLECTED',
            'volume_ml': 450,
        }
        form = DonationForm(initial=initial)
    return render(request, 'donations/donation_form.html', {
        'form': form,
        'appointment': appointment,
        'donor': donor,
        'latest_assessment': latest_assessment,
        'action_title': f'Process Donation for {donor.full_name}'
    })
