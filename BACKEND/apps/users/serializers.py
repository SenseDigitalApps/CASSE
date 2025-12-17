"""
Serializers for User model.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public user data.
    Adjusts fields based on the requesting user's role.
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email_primary',
            'phone',
            'email_secondary',
            'role',
            'status',
            'profile_photo_url',
            'created_at',
            'updated_at',
            'last_login_at',
        ]
        read_only_fields = [
            'id',
            'email_primary',
            'role',
            'status',
            'created_at',
            'updated_at',
            'last_login_at',
        ]

    def to_representation(self, instance):
        """
        Adjust fields based on the requesting user's role.
        """
        representation = super().to_representation(instance)
        
        # Obtener el usuario que hace la petición (si está disponible)
        request = self.context.get('request')
        requesting_user = getattr(request, 'user', None) if request else None
        
        # Verificar si el usuario está autenticado (no es AnonymousUser)
        is_authenticated = requesting_user and requesting_user.is_authenticated
        
        # Si no hay usuario autenticado o es CLIENT, ocultar datos sensibles
        if not is_authenticated or requesting_user.role == User.Role.CLIENT:
            # Solo mostrar datos básicos para clientes
            if is_authenticated and requesting_user.id == instance.id:
                # Si es el propio usuario, mostrar más campos
                pass  # Mostrar todos los campos definidos
            else:
                # Si es otro usuario o no autenticado, ocultar datos sensibles
                representation.pop('email_secondary', None)
                representation.pop('phone', None)
        
        # Para ADMIN, SUPERVISOR, INTERVENTORIA mostrar todos los campos
        # (ya están incluidos en fields)
        
        return representation


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (self-registration).
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'id_type',
            'id_number',
            'email_primary',
            'phone',
            'birth_date',
            'password',
            'email_secondary',
            'address',
            'profile_photo_url',
        ]
        extra_kwargs = {
            'full_name': {'required': True},
            'id_type': {'required': True},
            'id_number': {'required': True},
            'email_primary': {'required': True},
            'phone': {'required': True},
            'birth_date': {'required': True},
            'email_secondary': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'profile_photo_url': {'required': False, 'allow_blank': True},
        }

    def validate_email_primary(self, value):
        """
        Validate that email is unique.
        """
        value = value.strip().lower()
        if User.objects.filter(email_primary=value).exists():
            raise serializers.ValidationError('Este email ya está en uso')
        return value

    def create(self, validated_data):
        """
        Create user with hashed password.
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserCreateByAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users by admin.
    Includes role and status fields.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'id_type',
            'id_number',
            'email_primary',
            'phone',
            'birth_date',
            'password',
            'email_secondary',
            'address',
            'profile_photo_url',
            'role',
            'status',
        ]
        extra_kwargs = {
            'full_name': {'required': True},
            'id_type': {'required': True},
            'id_number': {'required': True},
            'email_primary': {'required': True},
            'phone': {'required': True},
            'birth_date': {'required': True},
            'role': {'required': True},
            'status': {'required': True},
            'email_secondary': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'profile_photo_url': {'required': False, 'allow_blank': True},
        }

    def validate_email_primary(self, value):
        """
        Validate that email is unique.
        """
        value = value.strip().lower()
        if User.objects.filter(email_primary=value).exists():
            raise serializers.ValidationError('Este email ya está en uso')
        return value

    def validate_role(self, value):
        """
        Validate that role is valid.
        """
        valid_roles = [choice[0] for choice in User.Role.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f'Rol inválido. Opciones: {", ".join(valid_roles)}')
        return value

    def validate_status(self, value):
        """
        Validate that status is valid.
        """
        valid_statuses = [choice[0] for choice in User.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Estado inválido. Opciones: {", ".join(valid_statuses)}')
        return value

    def create(self, validated_data):
        """
        Create user with hashed password.
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateByAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users by admin.
    Allows updating all fields except id and created_at.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'id_type',
            'id_number',
            'email_primary',
            'phone',
            'birth_date',
            'password',
            'email_secondary',
            'address',
            'profile_photo_url',
            'role',
            'status',
        ]
        extra_kwargs = {
            'email_primary': {'required': False},
            'full_name': {'required': False},
            'id_type': {'required': False},
            'id_number': {'required': False},
            'phone': {'required': False},
            'birth_date': {'required': False},
            'role': {'required': False},
            'status': {'required': False},
            'email_secondary': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'profile_photo_url': {'required': False, 'allow_blank': True},
        }

    def validate_email_primary(self, value):
        """
        Validate that email is unique if it's being changed.
        """
        if value:
            value = value.strip().lower()
            # Excluir el usuario actual de la validación
            instance = self.instance
            if instance and User.objects.filter(email_primary=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError('Este email ya está en uso')
        return value

    def validate_role(self, value):
        """
        Validate that role is valid.
        """
        if value:
            valid_roles = [choice[0] for choice in User.Role.choices]
            if value not in valid_roles:
                raise serializers.ValidationError(f'Rol inválido. Opciones: {", ".join(valid_roles)}')
        return value

    def validate_status(self, value):
        """
        Validate that status is valid.
        """
        if value:
            valid_statuses = [choice[0] for choice in User.Status.choices]
            if value not in valid_statuses:
                raise serializers.ValidationError(f'Estado inválido. Opciones: {", ".join(valid_statuses)}')
        return value

    def update(self, instance, validated_data):
        """
        Update user, handling password separately.
        """
        password = validated_data.pop('password', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar password si se proporcionó
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserMeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for users to update their own profile.
    Only allows updating specific fields.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'phone',
            'address',
            'email_secondary',
            'profile_photo_url',
            'password',
        ]
        extra_kwargs = {
            'full_name': {'required': False},
            'phone': {'required': False},
            'address': {'required': False, 'allow_blank': True},
            'email_secondary': {'required': False, 'allow_blank': True},
            'profile_photo_url': {'required': False, 'allow_blank': True},
        }

    # Campos prohibidos
    PROHIBITED_FIELDS = {
        'role',
        'status',
        'email_primary',
        'id_type',
        'id_number',
        'birth_date',
        'created_at',
        'updated_at',
        'last_login_at',
    }

    def validate(self, attrs):
        """
        Validate that prohibited fields are not being updated.
        """
        # Verificar que no se intenten actualizar campos prohibidos
        prohibited = set(attrs.keys()) & self.PROHIBITED_FIELDS
        if prohibited:
            raise serializers.ValidationError(
                f'No se pueden actualizar los siguientes campos: {", ".join(prohibited)}'
            )
        return attrs

    def update(self, instance, validated_data):
        """
        Update user profile, handling password separately.
        """
        password = validated_data.pop('password', None)
        
        # Actualizar campos permitidos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar password si se proporcionó
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

