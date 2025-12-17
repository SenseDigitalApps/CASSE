"""
Custom permissions for user management.
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an ADMIN.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and is an ADMIN.
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Permission class to check if user is ADMIN or SUPERVISOR.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and is ADMIN or SUPERVISOR.
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.ADMIN, User.Role.SUPERVISOR]
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class: ADMIN can edit, others can only read.
    """
    
    def has_permission(self, request, view):
        """
        Read permissions are allowed to any authenticated user.
        Write permissions are only allowed to ADMIN.
        """
        # Read permissions (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions (POST, PUT, PATCH, DELETE) - only ADMIN
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class: user can access their own data or ADMIN can access any.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object or is ADMIN.
        """
        # ADMIN can access any object
        if request.user.role == User.Role.ADMIN:
            return True
        
        # User can access their own object
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False

