from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from laboratory.models import BloodBag, LabSample, ScreeningResult
from laboratory.forms import LabSampleForm, ScreeningResultForm, BloodBagForm
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def blood_bag_list_view(request):
    search = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')
    status = request.GET.get('status', '')

    queryset = BloodBag.objects.select_related('donation', 'donation__donor').all()
    if search:
        queryset = queryset.filter(bag_id__icontains=search) | queryset.filter(donation__donor__first_name__icontains=search) | queryset.filter(donation__donor__last_name__icontains=search)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'laboratory/blood_bag_list.html', {
        'page_obj': page_obj,
        'search': search,
        'blood_group': blood_group,
        'status': status,
        'statuses': BloodBag.STATUS_CHOICES,
    })

@login_required
def blood_bag_detail_view(request, pk):
    bag = get_object_or_404(BloodBag.objects.select_related('donation', 'donation__donor'), pk=pk)
    samples = bag.samples.prefetch_related('screening_results').all()
    components = getattr(bag, 'components', None)
    component_list = components.all() if components else []
    return render(request, 'laboratory/blood_bag_detail.html', {
        'bag': bag,
        'samples': samples,
        'components': component_list,
    })

@login_required
def sample_list_view(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    queryset = LabSample.objects.select_related('blood_bag', 'blood_bag__donation__donor').all()
    if search:
        queryset = queryset.filter(sample_id__icontains=search) | queryset.filter(blood_bag__bag_id__icontains=search)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'laboratory/sample_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'statuses': LabSample.STATUS_CHOICES,
    })

@login_required
def sample_detail_view(request, pk):
    sample = get_object_or_404(LabSample.objects.select_related('blood_bag', 'blood_bag__donation__donor'), pk=pk)
    results = sample.screening_results.select_related('tested_by').all()
    return render(request, 'laboratory/sample_detail.html', {
        'sample': sample,
        'results': results,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'LAB_TECHNICIAN', 'MEDICAL_OFFICER')
def add_screening_result_view(request, sample_pk):
    sample = get_object_or_404(LabSample, pk=sample_pk)
    if request.method == 'POST':
        form = ScreeningResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.sample = sample
            result.tested_by = request.user
            result.save()
            
            sample.status = 'IN_TESTING'
            sample.save()
            
            log_audit(request.user, 'CREATE', result, f"Recorded {result.get_test_category_display()} result: {result.get_result_display()} for Sample {sample.sample_id}", request=request)
            messages.success(request, f"Screening result for {result.get_test_category_display()} recorded.")
            return redirect('laboratory:sample_detail', pk=sample.pk)
    else:
        form = ScreeningResultForm(initial={
            'test_name': 'Standard ELISA / CMIA Assay',
            'kit_lot_number': 'LOT-2026-A1',
            'result': 'NON_REACTIVE',
        })
    return render(request, 'laboratory/add_result.html', {'form': form, 'sample': sample})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def verify_sample_view(request, pk):
    sample = get_object_or_404(LabSample.objects.select_related('blood_bag'), pk=pk)
    results = sample.screening_results.all()
    
    if not results.exists():
        messages.error(request, "Cannot verify sample: No screening tests recorded yet.")
        return redirect('laboratory:sample_detail', pk=sample.pk)

    # Check for any reactive or invalid tests
    any_reactive = any(r.result in ['REACTIVE', 'CONFIRMED_REACTIVE'] for r in results)
    any_invalid = any(r.result in ['INVALID', 'INCONCLUSIVE', 'PENDING'] for r in results)

    if request.method == 'POST':
        decision = request.POST.get('decision')
        notes = request.POST.get('notes', '')
        
        with transaction.atomic():
            bag = sample.blood_bag
            from inventory.models import InventoryItem
            inv_item = InventoryItem.objects.filter(blood_bag=bag).first()

            if decision == 'APPROVE_SAFE':
                if any_reactive:
                    messages.error(request, "SAFETY ERROR: Cannot approve a sample with reactive/positive screening results!")
                    return redirect('laboratory:sample_detail', pk=sample.pk)
                
                sample.status = 'VERIFIED'
                sample.verified_by = request.user
                sample.verified_at = timezone.now()
                sample.notes = notes
                sample.save()

                bag.status = 'TESTED_SAFE'
                bag.storage_location = 'Main Cold Storage Unit #1 (2-6?C)'
                bag.save()

                if inv_item:
                    inv_item.status = 'AVAILABLE'
                    inv_item.save()

                log_audit(request.user, 'VERIFY', sample, f"Approved & verified blood bag {bag.bag_id} as SAFE for transfusion/processing", request=request)
                messages.success(request, f"Sample {sample.sample_id} verified. Blood Bag {bag.bag_id} is now RELEASED & AVAILABLE in inventory.")
            
            elif decision == 'REJECT_UNSAFE':
                sample.status = 'REJECTED'
                sample.verified_by = request.user
                sample.verified_at = timezone.now()
                sample.notes = notes
                sample.save()

                bag.status = 'REACTIVE_UNSAFE'
                bag.storage_location = 'Biohazard Quarantine Discard Area'
                bag.save()

                if inv_item:
                    inv_item.status = 'QUARANTINED'
                    inv_item.save()

                log_audit(request.user, 'REJECT', sample, f"Flagged Blood Bag {bag.bag_id} as REACTIVE / UNSAFE. Transferred to biohazard quarantine.", request=request)
                messages.warning(request, f"Blood Bag {bag.bag_id} marked as REACTIVE/UNSAFE and locked in quarantine.")

            return redirect('laboratory:sample_detail', pk=sample.pk)

    return render(request, 'laboratory/verify_sample.html', {
        'sample': sample,
        'results': results,
        'any_reactive': any_reactive,
        'any_invalid': any_invalid,
    })
