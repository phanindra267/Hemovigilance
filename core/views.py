from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import BloodBank, SystemConfiguration

def home_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    primary_bank = BloodBank.objects.filter(is_active=True).first()
    return render(request, 'core/home.html', {
        'blood_bank': primary_bank,
    })

def about_view(request):
    return render(request, 'core/about.html')

def guidelines_view(request):
    configs = SystemConfiguration.objects.filter(is_active=True).order_by('category')
    return render(request, 'core/guidelines.html', {'configs': configs})

def handler400(request, exception=None):
    return render(request, '400.html', status=400)

def handler403(request, exception=None):
    return render(request, '403.html', status=403)

def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
