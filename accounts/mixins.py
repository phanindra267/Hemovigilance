from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not hasattr(request.user, 'profile') or request.user.profile.role not in self.allowed_roles:
            messages.error(request, "Access restricted for your account role.")
            raise PermissionDenied("Insufficient Permissions.")
        return super().dispatch(request, *args, **kwargs)
