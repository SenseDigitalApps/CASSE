"""
Admin configuration for AuditLog model.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""

    list_display = [
        'action',
        'entity',
        'actor_user',
        'ip_address',
        'created_at',
    ]
    
    list_filter = [
        'action',
        'entity',
        'created_at',
        'actor_user',
    ]
    
    search_fields = [
        'action',
        'entity',
        'actor_user__email_primary',
        'actor_user__full_name',
        'ip_address',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
    ]
    
    date_hierarchy = 'created_at'
    
    ordering = ['-created_at']
    
    list_per_page = 50
    
    fieldsets = (
        ('Información de la Acción', {
            'fields': (
                'action',
                'entity',
                'entity_id',
            )
        }),
        ('Actor', {
            'fields': (
                'actor_user',
                'ip_address',
            )
        }),
        ('Metadatos', {
            'fields': ('metadata',)
        }),
        ('Información del Sistema', {
            'fields': (
                'id',
                'created_at',
            )
        }),
    )

