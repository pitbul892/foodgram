
from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
import recipes
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, TagRecipe

from .serializers import IngredientSerializer, RecipeCreateSerializer, RecipeReadSerializer, RecipeSerializer, TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return RecipeReadSerializer
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    
    @action(
        methods=['get',],
        url_path='get-link',
        detail=True,
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def get_link(self, request, pk=None):
        id = self.get_object().id
        name  = self.get_object().name
        print(id, name)
        return Response({'short-link': f'{settings.HOST}/{id}'}, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer