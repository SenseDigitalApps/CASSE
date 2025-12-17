"""
Serializers for authentication.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email_primary = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Validate user credentials.
        """
        email = attrs.get('email_primary')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Debe proporcionar email y contraseña'
            )

        # Normalizar email
        email = email.strip().lower()

        try:
            # Obtener usuario por email
            user = User.objects.get(email_primary=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Credenciales inválidas')

        # Verificar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError('Credenciales inválidas')

        # Verificar que el usuario esté activo
        if user.status != User.Status.ACTIVE:
            raise serializers.ValidationError('Usuario suspendido')

        attrs['user'] = user
        return attrs

