"""Кастомные разрешения."""
from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    """Проверка на автораю или безопасные методы."""

    def has_permission(self, request, view):
        """list."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """detail."""
        if request.method in permissions.SAFE_METHODS:
            return request.method in permissions.SAFE_METHODS
        return obj.author == request.user
