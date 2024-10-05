"""Админ-зона."""
from django.contrib import admin

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Inline для отображения ингредиентов и их количества в рецепте."""

    model = RecipeIngredient
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'
    extra = 1  # Количество пустых форм  ингредиентов
    min_num = 1  # Минколичество ингредиентов


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = ('id', 'name', 'get_favorite_count')
    inlines = [RecipeIngredientInline]

    def get_favorite_count(self, obj):
        """Получение количества избранных."""
        return obj.favoriterecipes.count()


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
