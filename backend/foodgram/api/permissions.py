from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Все права есть у администратора, у остальных только на чтение."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_staff
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Все права есть у администратора или автора, у остальных только на чтение.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )


class IsAuthenticatedOrAdminOrReadOnly(permissions.BasePermission):
    """
    Все права есть у авторизованного пользователя или администротора,
    у остальных только на чтение.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_active
            or request.user
            and request.user.is_staff
        )
