from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag, TagRecipe

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(TagRecipe)