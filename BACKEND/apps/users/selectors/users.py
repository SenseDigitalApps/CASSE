"""
User selector functions for querying users from the database.
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet

User = get_user_model()
logger = logging.getLogger(__name__)

# Roles permitidos para listar usuarios
ALLOWED_LIST_ROLES = {
    User.Role.ADMIN,
    User.Role.SUPERVISOR,
    User.Role.INTERVENTORIA,
}


def get_user_by_id(user_id: UUID) -> User:
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        User: Instancia del usuario
    
    Raises:
        User.DoesNotExist: Si el usuario no existe
    
    Example:
        >>> from uuid import UUID
        >>> user = get_user_by_id(UUID('123e4567-e89b-12d3-a456-426614174000'))
    """
    try:
        user = User.objects.get(id=user_id)
        logger.debug(f"Usuario encontrado por ID: {user_id}")
        return user
    except User.DoesNotExist:
        logger.warning(f"Usuario con ID {user_id} no encontrado")
        raise


def get_user_by_email(email: str) -> User:
    """
    Obtiene un usuario por su email_primary.
    
    Args:
        email: Email principal del usuario
    
    Returns:
        User: Instancia del usuario
    
    Raises:
        User.DoesNotExist: Si el usuario no existe
    
    Example:
        >>> user = get_user_by_email('user@example.com')
    """
    # Normalizar email
    email = email.strip().lower() if email else ''
    
    if not email:
        raise ValueError('El email no puede estar vacío')
    
    try:
        user = User.objects.get(email_primary=email)
        logger.debug(f"Usuario encontrado por email: {email}")
        return user
    except User.DoesNotExist:
        logger.warning(f"Usuario con email {email} no encontrado")
        raise


def list_users(
    filters: Optional[Dict[str, Any]] = None,
    actor_user: Optional[User] = None
) -> QuerySet[User]:
    """
    Lista usuarios con filtros aplicados.
    
    Solo usuarios con roles ADMIN, SUPERVISOR o INTERVENTORIA pueden listar usuarios.
    
    Args:
        filters: Diccionario con filtros opcionales:
            - role: Filtrar por rol (ADMIN, CLIENT, INTERVENTORIA, SUPERVISOR)
            - status: Filtrar por estado (ACTIVE, SUSPENDED)
            - search: Búsqueda en full_name, email_primary, id_number, phone
        actor_user: Usuario que realiza la consulta (requerido para validar permisos)
    
    Returns:
        QuerySet[User]: QuerySet de usuarios filtrados y ordenados
    
    Raises:
        PermissionDenied: Si el actor_user no tiene permisos para listar usuarios
        ValueError: Si actor_user es None
    
    Example:
        >>> admin_user = User.objects.get(role=User.Role.ADMIN)
        >>> users = list_users(
        ...     filters={'role': 'CLIENT', 'status': 'ACTIVE', 'search': 'juan'},
        ...     actor_user=admin_user
        ... )
    """
    # Validar que actor_user esté presente
    if actor_user is None:
        raise ValueError('actor_user es requerido para listar usuarios')
    
    # Validar permisos
    if actor_user.role not in ALLOWED_LIST_ROLES:
        logger.warning(
            f"Intento de listar usuarios por usuario sin permisos: "
            f"{actor_user.email_primary} (role: {actor_user.role})"
        )
        raise PermissionDenied('No tiene permisos para listar usuarios')
    
    # Iniciar QuerySet
    queryset = User.objects.all()
    
    # Aplicar filtros si se proporcionan
    if filters:
        # Filtro por rol
        role = filters.get('role')
        if role:
            # Validar que el rol sea válido
            if role in [choice[0] for choice in User.Role.choices]:
                queryset = queryset.filter(role=role)
            else:
                logger.warning(f"Rol inválido en filtro: {role}")
        
        # Filtro por estado
        status = filters.get('status')
        if status:
            # Validar que el estado sea válido
            if status in [choice[0] for choice in User.Status.choices]:
                queryset = queryset.filter(status=status)
            else:
                logger.warning(f"Estado inválido en filtro: {status}")
        
        # Búsqueda en múltiples campos
        search = filters.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email_primary__icontains=search) |
                Q(id_number__icontains=search) |
                Q(phone__icontains=search)
            )
    
    # Ordenar por fecha de creación (más recientes primero)
    queryset = queryset.order_by('-created_at')
    
    logger.debug(
        f"Lista de usuarios obtenida por {actor_user.email_primary}: "
        f"{queryset.count()} usuarios"
    )
    
    return queryset

