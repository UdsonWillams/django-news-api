from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission to allow only admin users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsEditor(permissions.BasePermission):
    """Permission to allow only editor users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_editor()


class IsNewsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission to allow:
    - Editors to modify only their own news
    - Admins to modify any news
    - Others can only read
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can do anything
        if request.user.is_admin():
            return True

        # Editors can only modify their own news
        if request.user.is_editor():
            return obj.author == request.user

        # Others don't have write permissions
        return False


class CanViewNewsContent(permissions.BasePermission):
    """Permission to check if user can access news content based on subscription"""

    def has_object_permission(self, request, view, obj):
        # Check if news is published
        if not obj.is_published:
            # Only admin and author can see unpublished content
            if request.user.is_admin() or obj.author == request.user:
                return True
            return False

        # For published content, check subscription access
        return request.user.can_access_content(obj)
