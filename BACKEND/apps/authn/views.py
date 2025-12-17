"""
Views for authentication endpoints.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer
from apps.users.serializers import UserRegisterSerializer, UserPublicSerializer
from apps.users.services.users import register_user
from apps.authn.services.jwt import generate_tokens_for_user
from apps.audit.services.audit_log import log_audit_event
from apps.audit.constants import LOGIN_SUCCESS, LOGIN_FAILED

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtiene la IP del cliente desde el request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LoginView(APIView):
    """
    View for user login.
    POST /api/v1/auth/login/
    
    Rate limited: 5 attempts per minute to prevent brute force attacks.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        """
        Handle user login.
        """
        serializer = LoginSerializer(data=request.data)
        ip_address = get_client_ip(request)
        
        if not serializer.is_valid():
            # Intentar obtener email para audit log
            email = request.data.get('email_primary', '')
            if email:
                log_audit_event(
                    actor_user=None,
                    action=LOGIN_FAILED,
                    entity='User',
                    entity_id=None,
                    metadata={'email': email, 'reason': 'invalid_credentials'},
                    ip_address=ip_address
                )
            
            return Response(
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Usuario validado en el serializer
        user = serializer.validated_data['user']
        
        # Verificar que el usuario esté activo (ya validado en serializer, pero doble verificación)
        if user.status != user.Status.ACTIVE:
            log_audit_event(
                actor_user=user,
                action=LOGIN_FAILED,
                entity='User',
                entity_id=user.id,
                metadata={'reason': 'user_suspended'},
                ip_address=ip_address
            )
            return Response(
                {'detail': 'Usuario suspendido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generar tokens JWT
        try:
            tokens = generate_tokens_for_user(user)
        except Exception as e:
            logger.error(f"Error al generar tokens para usuario {user.id}: {e}", exc_info=True)
            return Response(
                {'detail': 'Error al generar tokens'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Actualizar last_login_at
        from django.utils import timezone
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        # Generar audit log
        log_audit_event(
            actor_user=user,
            action=LOGIN_SUCCESS,
            entity='User',
            entity_id=user.id,
            metadata={'email': user.email_primary},
            ip_address=ip_address
        )
        
        # Serializar datos del usuario
        user_data = UserPublicSerializer(user, context={'request': request}).data
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': user_data
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    View for user registration.
    POST /api/v1/auth/register/
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        """
        Handle user registration.
        """
        serializer = UserRegisterSerializer(data=request.data)
        ip_address = get_client_ip(request)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear usuario usando el servicio (ya genera AuditLog)
        try:
            user = register_user(serializer.validated_data, ip_address=ip_address)
        except Exception as e:
            logger.error(f"Error al registrar usuario: {e}", exc_info=True)
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serializar datos del usuario
        user_data = UserPublicSerializer(user, context={'request': request}).data
        
        return Response(
            user_data,
            status=status.HTTP_201_CREATED
        )


class RefreshTokenView(TokenRefreshView):
    """
    View for refreshing JWT access token.
    POST /api/v1/auth/jwt/refresh/
    
    Uses rest_framework_simplejwt's TokenRefreshView.
    """
    permission_classes = [AllowAny]

