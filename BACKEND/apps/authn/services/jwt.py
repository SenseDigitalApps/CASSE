"""
JWT service functions for token generation and validation.
"""
import logging
from typing import Dict, Optional

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_tokens_for_user(user: User) -> Dict[str, str]:
    """
    Genera tokens JWT (access y refresh) para un usuario.
    
    Args:
        user: Instancia del usuario
    
    Returns:
        Dict con 'access' y 'refresh' tokens
    
    Example:
        >>> tokens = generate_tokens_for_user(user)
        >>> access_token = tokens['access']
        >>> refresh_token = tokens['refresh']
    """
    try:
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    except Exception as e:
        logger.error(f"Error al generar tokens para usuario {user.id}: {e}", exc_info=True)
        raise


def get_user_from_token(token: str) -> Optional[User]:
    """
    Obtiene el usuario desde un token JWT.
    
    Args:
        token: Access token JWT
    
    Returns:
        User si el token es válido, None si no
    
    Example:
        >>> user = get_user_from_token(access_token)
        >>> if user:
        ...     print(f"Usuario: {user.email_primary}")
    """
    try:
        # Configurar backend de tokens
        token_backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256'),
            signing_key=settings.SIMPLE_JWT.get('SIGNING_KEY', settings.SECRET_KEY)
        )
        
        # Decodificar token
        validated_data = token_backend.decode(token, verify=True)
        
        # Obtener user_id del token
        user_id = validated_data.get('user_id')
        if not user_id:
            logger.warning("Token no contiene user_id")
            return None
        
        # Obtener usuario
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            return None
            
    except (TokenError, InvalidToken) as e:
        logger.debug(f"Token inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al obtener usuario desde token: {e}", exc_info=True)
        return None


def validate_token(token: str) -> bool:
    """
    Valida si un token JWT es válido y no está expirado.
    
    Args:
        token: Access token JWT
    
    Returns:
        True si el token es válido, False si no
    
    Example:
        >>> if validate_token(access_token):
        ...     print("Token válido")
    """
    try:
        # Configurar backend de tokens
        token_backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256'),
            signing_key=settings.SIMPLE_JWT.get('SIGNING_KEY', settings.SECRET_KEY)
        )
        
        # Intentar decodificar (valida expiración automáticamente)
        token_backend.decode(token, verify=True)
        return True
        
    except (TokenError, InvalidToken):
        return False
    except Exception as e:
        logger.error(f"Error al validar token: {e}", exc_info=True)
        return False

