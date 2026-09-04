from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not hasattr(request.user, 'profile'):
                messages.error(request, "User profile not found. Please contact administrator.")
                return redirect('accounts:login')
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have the required permissions to access this feature.")
            raise PermissionDenied("Access Denied: Insufficient Role Permissions.")
        return _wrapped_view
    return decorator
