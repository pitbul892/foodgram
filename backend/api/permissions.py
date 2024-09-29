"""Кастомные разрешения."""
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверка на автораю или безопасные методы."""

    def has_permission(self, request, view):
        """list."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """detail."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAuthenticatedOrReadOnlyOrMe(permissions.BasePermission):
    """Проверка на пользователя, аноним или на страничку me."""

    def has_permission(self, request, view):
        """list."""
        if "me" in request.path.split("/"):
            return request.user.is_authenticated
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """detail."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)
