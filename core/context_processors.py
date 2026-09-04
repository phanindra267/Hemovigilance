from django.conf import settings
from core.models import BloodBank

def lifeflow_global_context(request):
    user_profile = None
    unread_count = 0
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            user_profile = request.user.profile
        try:
            from notifications.models import Notification
            unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        except Exception:
            unread_count = 0

    return {
        'ORGANIZATION_NAME': getattr(settings, 'ORGANIZATION_NAME', 'RedLink Hemovigilance'),
        'ORGANIZATION_CODE': getattr(settings, 'ORGANIZATION_CODE', 'LIFEFLOW-HQ'),
        'current_user_profile': user_profile,
        'unread_notifications_count': unread_count,
        'BLOOD_BANK_PRIMARY': BloodBank.objects.filter(is_active=True).first(),
    }
