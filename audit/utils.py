from django.utils import timezone
from audit.models import AuditLog
from audit.middleware import get_current_request

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit(user=None, action='UPDATE', instance=None, reason="", details=None, request=None):
    try:
        if request is None:
            request = get_current_request()
            
        if user is None and request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            
        ip = get_client_ip(request)
        
        model_name = instance.__class__.__name__ if instance else "Unknown"
        object_id = str(getattr(instance, 'pk', getattr(instance, 'id', 'N/A')))
        object_repr = str(instance)[:255] if instance else "N/A"
        
        if details is None:
            details = {}
            
        return AuditLog.objects.create(
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            user=user if (user and user.is_authenticated) else None,
            user_ip=ip,
            details=details,
            reason=reason,
            timestamp=timezone.now()
        )
    except Exception as e:
        # Never let audit logging crash the primary transaction
        print(f"Audit log failed: {e}")
        return None
