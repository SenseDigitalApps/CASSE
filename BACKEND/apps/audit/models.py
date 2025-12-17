"""
Audit log model for tracking system actions.
"""
import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """Model for storing audit logs of system actions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario Actor'
    )
    
    action = models.CharField(
        max_length=100,
        verbose_name='Acción',
        help_text='Tipo de acción realizada (ej: LOGIN_SUCCESS, USER_CREATED)'
    )
    
    entity = models.CharField(
        max_length=50,
        verbose_name='Entidad',
        help_text='Entidad afectada (ej: User, Policy)'
    )
    
    entity_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID de Entidad',
        help_text='ID de la entidad afectada'
    )
    
    metadata = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        verbose_name='Metadatos',
        help_text='Información adicional sobre la acción'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP',
        help_text='IP del cliente que realizó la acción'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['entity']),
            models.Index(fields=['created_at']),
            models.Index(fields=['actor_user']),
            models.Index(fields=['entity', 'entity_id']),
        ]

    def __str__(self):
        actor = self.actor_user.email_primary if self.actor_user else 'Sistema'
        return f"{self.action} - {self.entity} - {actor} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

