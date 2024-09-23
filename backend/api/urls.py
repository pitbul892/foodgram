"""Эндопинты api."""
from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = routers.DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
