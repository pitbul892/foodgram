"""Админ-зона."""
from django.contrib import admin

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = ('id', 'name', 'get_favorite_count')


    def get_favorite_count(self, obj):
        """Получение количества избранных."""
        return FavoriteRecipes.objects.filter(recipe=obj).count()


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
