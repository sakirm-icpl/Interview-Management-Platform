"""
Custom permissions for authentication app.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners to edit their objects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsHROrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only HR managers and admins.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_hr_or_admin


class IsCandidate(permissions.BasePermission):
    """
    Custom permission to allow only candidates.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_candidate


class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow only owners to access their objects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has a candidate field
        if hasattr(obj, 'candidate'):
            return obj.candidate == request.user
        
        # Check if the object has a created_by field
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Default to allowing access if object is the user itself
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to allow only admin users.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role == request.user.UserRole.ADMIN