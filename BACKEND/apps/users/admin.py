"""
Admin configuration for User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = [
        'email_primary',
        'full_name',
        'id_type',
        'id_number',
        'role',
        'status',
        'created_at',
        'last_login_at',
    ]
    
    list_filter = [
        'role',
        'status',
        'id_type',
        'created_at',
        'last_login_at',
    ]
    
    search_fields = [
        'email_primary',
        'email_secondary',
        'full_name',
        'id_number',
        'phone',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'last_login_at',
    ]
    
    fieldsets = (
        (None, {'fields': ('email_primary', 'password')}),
        ('Información Personal', {
            'fields': (
                'full_name',
                'id_type',
                'id_number',
                'birth_date',
                'phone',
                'address',
                'profile_photo_url',
            )
        }),
        ('Contacto', {
            'fields': ('email_secondary',)
        }),
        ('Permisos y Estado', {
            'fields': (
                'role',
                'status',
                'groups',
                'user_permissions',
            ),
            'description': 'is_active, is_staff e is_superuser se calculan automáticamente según el role y status'
        }),
        ('Fechas', {
            'fields': (
                'created_at',
                'updated_at',
                'last_login_at',
            )
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email_primary',
                'password1',
                'password2',
                'full_name',
                'id_type',
                'id_number',
                'birth_date',
                'phone',
                'role',
                'status',
            ),
        }),
    )
    
    ordering = ('-created_at',)
    filter_horizontal = ('groups', 'user_permissions',)

