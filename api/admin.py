from django.contrib import admin
from .models import APIToken


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    """Admin para tokens de API"""
    list_display = ['user', 'description', 'created_at', 'last_used_at']
    list_filter = ['created_at', 'last_used_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'description')
        }),
        ('Token', {
            'fields': ('key',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'last_used_at')
        }),
    )
