from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from blood_components.models import BloodComponent
from blood_components.forms import BloodComponentForm, ComponentSeparationForm
from laboratory.models import BloodBag
from accounts.decorators import role_required
from audit.utils import log_audit

@login_required
def component_list_view(request):
    search = request.GET.get('search', '')
    component_type = request.GET.get('component_type', '')
    blood_group = request.GET.get('blood_group', '')
    status = request.GET.get('status', '')

    queryset = BloodComponent.objects.select_related('parent_bag').all()
    if search:
        queryset = queryset.filter(component_id__icontains=search) | queryset.filter(parent_bag__bag_id__icontains=search)
    if component_type:
        queryset = queryset.filter(component_type=component_type)
    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blood_components/component_list.html', {
        'page_obj': page_obj,
        'search': search,
        'component_type': component_type,
        'blood_group': blood_group,
        'status': status,
        'component_types': BloodComponent.COMPONENT_TYPE_CHOICES,
        'blood_groups': Donor.BLOOD_GROUP_CHOICES if 'Donor' in globals() else [],
        'statuses': BloodComponent.STATUS_CHOICES,
    })

@login_required
def component_detail_view(request, pk):
    component = get_object_or_404(BloodComponent.objects.select_related('parent_bag', 'prepared_by'), pk=pk)
    return render(request, 'blood_components/component_detail.html', {'component': component})

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'BLOOD_BANK_TECH', 'LAB_TECHNICIAN', 'MEDICAL_OFFICER')
def separate_components_view(request, bag_pk):
    bag = get_object_or_404(BloodBag, pk=bag_pk)
    
    # Check if bag is safe
    if bag.status not in ['TESTED_SAFE', 'QUARANTINED']:
        messages.error(request, f"Bag {bag.bag_id} with status {bag.get_status_display()} cannot be processed into components.")
        return redirect('laboratory:blood_bag_detail', pk=bag.pk)

    if request.method == 'POST':
        form = ComponentSeparationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                from inventory.models import InventoryItem
                
                created_components = []
                now = timezone.now()
                status_to_assign = 'AVAILABLE' if bag.status == 'TESTED_SAFE' else 'QUARANTINED'

                if form.cleaned_data['create_prbc']:
                    prbc = BloodComponent.objects.create(
                        parent_bag=bag,
                        component_type='PRBC',
                        blood_group=bag.blood_group,
                        rh_factor=bag.rh_factor,
                        prepared_date=now,
                        expiry_date=now + timedelta(days=42),
                        volume_ml=form.cleaned_data['prbc_volume'],
                        prepared_by=request.user,
                        status=status_to_assign,
                        storage_location='PRBC Refrigerator #1 (2-6?C)',
                        leukoreduced=form.cleaned_data['leukoreduced'],
                    )
                    created_components.append(prbc)
                    InventoryItem.objects.create(
                        component=prbc,
                        item_type='COMPONENT',
                        blood_group=prbc.blood_group,
                        rh_factor=prbc.rh_factor,
                        component_type='PRBC',
                        volume_ml=prbc.volume_ml,
                        collection_date=bag.collection_date,
                        expiry_date=prbc.expiry_date,
                        status=status_to_assign,
                    )

                if form.cleaned_data['create_ffp']:
                    ffp = BloodComponent.objects.create(
                        parent_bag=bag,
                        component_type='FFP',
                        blood_group=bag.blood_group,
                        rh_factor=bag.rh_factor,
                        prepared_date=now,
                        expiry_date=now + timedelta(days=365),
                        volume_ml=form.cleaned_data['ffp_volume'],
                        prepared_by=request.user,
                        status=status_to_assign,
                        storage_location='Deep Freezer Unit #1 (-40?C)',
                    )
                    created_components.append(ffp)
                    InventoryItem.objects.create(
                        component=ffp,
                        item_type='COMPONENT',
                        blood_group=ffp.blood_group,
                        rh_factor=ffp.rh_factor,
                        component_type='FFP',
                        volume_ml=ffp.volume_ml,
                        collection_date=bag.collection_date,
                        expiry_date=ffp.expiry_date,
                        status=status_to_assign,
                    )

                if form.cleaned_data['create_platelet']:
                    plt = BloodComponent.objects.create(
                        parent_bag=bag,
                        component_type='PLATELET',
                        blood_group=bag.blood_group,
                        rh_factor=bag.rh_factor,
                        prepared_date=now,
                        expiry_date=now + timedelta(days=5),
                        volume_ml=form.cleaned_data['platelet_volume'],
                        prepared_by=request.user,
                        status=status_to_assign,
                        storage_location='Platelet Agitator #1 (20-24?C)',
                    )
                    created_components.append(plt)
                    InventoryItem.objects.create(
                        component=plt,
                        item_type='COMPONENT',
                        blood_group=plt.blood_group,
                        rh_factor=plt.rh_factor,
                        component_type='PLATELET',
                        volume_ml=plt.volume_ml,
                        collection_date=bag.collection_date,
                        expiry_date=plt.expiry_date,
                        status=status_to_assign,
                    )

                if form.cleaned_data['create_cryo']:
                    cryo = BloodComponent.objects.create(
                        parent_bag=bag,
                        component_type='CRYOPRECIPITATE',
                        blood_group=bag.blood_group,
                        rh_factor=bag.rh_factor,
                        prepared_date=now,
                        expiry_date=now + timedelta(days=365),
                        volume_ml=form.cleaned_data['cryo_volume'],
                        prepared_by=request.user,
                        status=status_to_assign,
                        storage_location='Deep Freezer Unit #2 (-40?C)',
                    )
                    created_components.append(cryo)
                    InventoryItem.objects.create(
                        component=cryo,
                        item_type='COMPONENT',
                        blood_group=cryo.blood_group,
                        rh_factor=cryo.rh_factor,
                        component_type='CRYOPRECIPITATE',
                        volume_ml=cryo.volume_ml,
                        collection_date=bag.collection_date,
                        expiry_date=cryo.expiry_date,
                        status=status_to_assign,
                    )

                bag.status = 'PROCESSED_TO_COMPONENTS'
                bag.save()

                # Also mark parent bag inventory item as discarded or processed
                parent_inv = InventoryItem.objects.filter(blood_bag=bag).first()
                if parent_inv:
                    parent_inv.status = 'DISCARDED'
                    parent_inv.save()

                comp_names = ", ".join([c.get_component_type_display() for c in created_components])
                log_audit(request.user, 'CREATE', bag, f"Separated blood bag {bag.bag_id} into components: {comp_names}", request=request)
                messages.success(request, f"Successfully prepared {len(created_components)} components from {bag.bag_id}: {comp_names}.")
                return redirect('laboratory:blood_bag_detail', pk=bag.pk)
    else:
        form = ComponentSeparationForm()

    return render(request, 'blood_components/separate_components.html', {
        'form': form,
        'bag': bag,
    })
