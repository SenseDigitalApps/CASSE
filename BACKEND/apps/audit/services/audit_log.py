"""
Service for logging audit events.
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID

from django.contrib.auth import get_user_model
from ..models import AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


def log_audit_event(
    actor_user: Optional[User],
    action: str,
    entity: str,
    entity_id: Optional[UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Registra un evento de auditoría.
    
    Args:
        actor_user: Usuario que realiza la acción (puede ser None para acciones del sistema)
        action: Tipo de acción (ej: "LOGIN_SUCCESS", "USER_CREATED")
        entity: Entidad afectada (ej: "User", "Policy")
        entity_id: ID de la entidad (UUID, opcional)
        metadata: Diccionario con información adicional (opcional)
        ip_address: IP del cliente (opcional)
    
    Returns:
        AuditLog: Instancia del log creado, o None si hubo un error
    
    Example:
        >>> from apps.audit.services.audit_log import log_audit_event
        >>> from apps.audit.constants import LOGIN_SUCCESS
        >>> log_audit_event(
        ...     actor_user=user,
        ...     action=LOGIN_SUCCESS,
        ...     entity='User',
        ...     entity_id=user.id,
        ...     ip_address='192.168.1.1'
        ... )
    """
    try:
        # Validar campos requeridos
        if not action or not entity:
            logger.warning(f"Intento de crear audit log sin action o entity: action={action}, entity={entity}")
            return None
        
        # Crear instancia de AuditLog
        audit_log = AuditLog.objects.create(
            actor_user=actor_user,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata=metadata or {},
            ip_address=ip_address
        )
        
        logger.debug(f"Audit log creado: {audit_log}")
        return audit_log
        
    except Exception as e:
        # No debe romper el flujo principal si falla la auditoría
        logger.error(f"Error al crear audit log: {e}", exc_info=True)
        return None

