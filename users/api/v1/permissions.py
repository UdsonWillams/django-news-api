from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission to allow only admin users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission to allow:
    - Admin to do anything
    - Users to view/edit only themselves
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin():
            return True

        # Users can only access their own data
        return obj.id == request.user.id
