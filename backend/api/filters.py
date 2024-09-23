"""Кастомные фильтры."""
import django_filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import filters
from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(django_filters.FilterSet):
    """Фильтрация рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all()
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shopping_cart",
    )
    is_favorited = django_filters.NumberFilter(
        method="filter_is_favorited",
    )

    class Meta:
        """:)."""

        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр наличия рецепта в списке покупок."""
        value = bool(int(value))
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shoppingcart__user=user).distinct()
            return queryset.exclude(shoppingcart__user=user).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр наличия рецепта в избранных."""
        value = bool(int(value))
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(favoriterecipes__user=user).distinct()
            return queryset.exclude(favoriterecipes__user=user).distinct()
        return queryset
