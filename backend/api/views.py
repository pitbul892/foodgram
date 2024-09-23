"""Функции для работы с рецептами и пользователями."""
from core import functions
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from recipes.models import (FavoriteRecipes, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (AvatarSerializer, FavoriteRecipesSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          RecipeShoppingCartSerializer, RecipeShopSerializer,
                          SubscribeCreateSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Recipe."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_serializer_class(self):
        """Сериалайзер."""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def get_serializer_context(self):
        """Добавляем request в контекст."""
        return {'request': self.request}

    def perform_create(self, serializer):
        """Значение поля author."""
        serializer.save(author=self.request.user)

    @action(
        methods=[
            'get',
        ],
        url_path='get-link',
        detail=True,
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        id = self.get_object().id
        return Response(
            {'short-link': f'{settings.HOST}/{id}'}, status=status.HTTP_200_OK
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в корзину."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":

            serializer = RecipeShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSerializer(
                recipe,
                context={
                    'request': request,
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = RecipeSerializer(
            recipe,
            context={
                'request': request,
            },
        )
        try:
            recipe_in_shop = ShoppingCart.objects.get(user=user, recipe=recipe)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_in_shop.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=[
            'get',
        ],
        detail=False,
    )
    def download_shopping_cart(self, request):
        """Получение списка продуктов."""
        user = request.user
        recipes = Recipe.objects.filter(shoppingcart__user=user)
        serializer = RecipeShopSerializer(
            recipes, many=True, context={"request": request}
        )
        data = functions.txt_file(serializer.data)
        return Response(
            data, content_type='text/plain', status=status.HTTP_200_OK
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk=None):
        """Получение списка продуктов."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            serializer = FavoriteRecipesSerializer(
                data={'user': user.id, 'recipe': recipe.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = RecipeSerializer(
                recipe,
                context={
                    'request': request,
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = RecipeSerializer(
            recipe,
            context={
                'request': request,
            },
        )
        try:
            recipe_in_fav = FavoriteRecipes.objects.get(
                user=user,
                recipe=recipe
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_in_fav.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class UserViewSet(views.UserViewSet):
    """Класс пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(
        methods=[
            'get',
        ],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request):
        """Моя страница."""
        user = request.user
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    @action(
        methods=['put', 'delete'],
        url_path='me/avatar',
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def avatar(self, request):
        """Изменение и удаление аватарки."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                if 'avatar' in request.data:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, id=None):
        """Подписка на пользователя."""
        subscriber = self.request.user
        user = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data={'subscriber': subscriber.id, 'user': user.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipes_limit = request.query_params.get('recipes_limit')
            serializer = SubscriptionSerializer(
                user,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = SubscriptionSerializer(
            user,
            context={
                'request': request,
            },
        )
        try:
            subscriptions = Subscriptions.objects.get(
                user=user,
                subscriber=subscriber
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        subscriptions.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=[
            'get',
        ],
        detail=False,
    )
    def subscriptions(self, request):
        """Список подписок."""
        paginator = LimitOffsetPagination()
        users = User.objects.filter(subscriber__subscriber=request.user)
        paginated_users = paginator.paginate_queryset(
            users, request, view=self
        )
        recipes_limit = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            paginated_users,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return paginator.get_paginated_response(serializer.data)
