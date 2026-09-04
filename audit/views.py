from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from audit.models import AuditLog
from accounts.decorators import role_required

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def audit_log_list_view(request):
    action = request.GET.get('action', '')
    model_name = request.GET.get('model_name', '')
    search = request.GET.get('search', '')

    queryset = AuditLog.objects.select_related('user').all()
    if action:
        queryset = queryset.filter(action=action)
    if model_name:
        queryset = queryset.filter(model_name__icontains=model_name)
    if search:
        queryset = queryset.filter(object_repr__icontains=search) | queryset.filter(reason__icontains=search) | queryset.filter(object_id__icontains=search)

    paginator = Paginator(queryset, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    actions = AuditLog.ACTION_CHOICES
    models_list = AuditLog.objects.values_list('model_name', flat=True).distinct()

    return render(request, 'audit/audit_list.html', {
        'page_obj': page_obj,
        'actions': actions,
        'models_list': models_list,
        'selected_action': action,
        'selected_model': model_name,
        'search': search,
    })

@login_required
@role_required('SUPER_ADMIN', 'BLOOD_BANK_ADMIN', 'MEDICAL_OFFICER')
def audit_log_detail_view(request, pk):
    log = get_object_or_404(AuditLog.objects.select_related('user'), pk=pk)
    return render(request, 'audit/audit_detail.html', {'log': log})
