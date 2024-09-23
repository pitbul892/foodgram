"""Кастомный пагинатор."""
from rest_framework.pagination import PageNumberPagination


class RecipesLimitPagination(PageNumberPagination):
    """Пагинация рецептов."""

    limit_query_param = 'recipes_limit'

    def get_paginated_response(self, data):
        """результат."""
        return self.paginator.get_paginated_response(data)
