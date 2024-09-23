"""Админ-зона."""
from django.contrib import admin

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, TagRecipe)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(TagRecipe)
admin.site.register(FavoriteRecipes)
admin.site.register(ShoppingCart)
