from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_staff
        )


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )


class IsAuthenticatedOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_active
            or request.user
            and request.user.is_staff
        )
