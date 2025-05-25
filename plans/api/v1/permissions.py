from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission to allow only admin users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class ReadOnly(permissions.BasePermission):
    """Permission to allow read-only access"""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
