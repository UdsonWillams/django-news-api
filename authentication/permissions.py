from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to allow only admin users
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsEditor(permissions.BasePermission):
    """
    Permission to allow only editor users
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_editor()


class IsSelf(permissions.BasePermission):
    """
    Permission to allow users to manage only their own data
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
