
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin')


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'agent')


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # read permissions: only owner or admin can view
        from django.contrib.auth.models import User
        is_admin = bool(request.user and hasattr(request.user, 'profile') and request.user.profile.role == 'admin')

        if request.method in SAFE_METHODS:
            # If obj is a User instance
            if isinstance(obj, User):
                return obj == request.user or is_admin

            # If obj has `user` relation (e.g., Profile)
            if hasattr(obj, 'user'):
                return obj.user == request.user or is_admin

            return False

        # write permissions: only owner
        if isinstance(obj, User):
            return obj == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
