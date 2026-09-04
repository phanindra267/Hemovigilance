from django.contrib import admin
from audit.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'model_name', 'object_id', 'user', 'user_ip', 'reason')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('model_name', 'object_id', 'object_repr', 'reason', 'user__username', 'user_ip')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
