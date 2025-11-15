from django.contrib import admin
from .models import CTFConfig, Achievement

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

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['get_achievement_name', 'category', 'get_entity', 'earned_at']
    list_filter = ['category', 'earned_at']
    search_fields = ['code', 'team__name', 'user__username']
    readonly_fields = ['code', 'team', 'user', 'category', 'earned_at']
    
    def get_achievement_name(self, obj):
        info = obj.get_info()
        return f"{info.icon} {info.name}" if info else obj.code
    get_achievement_name.short_description = 'Logro'
    
    def get_entity(self, obj):
        if obj.category == 'team':
            return f"🏆 {obj.team.name}" if obj.team else '-'
        else:
            return f"👤 {obj.user.username}" if obj.user else '-'
    get_entity.short_description = 'Entidad'
    
    def has_add_permission(self, request):
        # Los logros se otorgan automáticamente
        return False
    
    def has_change_permission(self, request, obj=None):
        # Los logros no se pueden editar
        return False
