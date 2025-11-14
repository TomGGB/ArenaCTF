from django.contrib import admin
from .models import CTFConfig

@admin.register(CTFConfig)
class CTFConfigAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'start_time', 'end_time']
    fieldsets = [
        ('Estado del CTF', {
            'fields': ['is_active']
        }),
        ('Tiempos', {
            'fields': ['start_time', 'end_time']
        }),
    ]
    
    def has_add_permission(self, request):
        # Solo permitir una configuración
        return not CTFConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False
