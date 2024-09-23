"""Сериализаторы для работы с рецептами, ингредиентами и подписками."""
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from users.models import Subscriptions

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Для картинки."""

    def to_internal_value(self, data):
        """Форматирование."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер User."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True, required=False
    )
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Meta."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        """Получить is_subscribed."""
        current_user = self.context.get('request').user
        if isinstance(current_user, AnonymousUser):
            return False
        return Subscriptions.objects.filter(
            user=user, subscriber=current_user
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер Tag."""

    class Meta:
        """Meta."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ingredient."""

    class Meta:
        """Meta."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        """Meta."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()

    class Meta:
        """Meta."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер рецепта короткий."""

    class Meta:
        """Meta."""

        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер создания рецептов."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    name = serializers.CharField(max_length=100)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        """Meta."""

        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        """Валидация тэгов и ингредиентов."""
        ingredients_data = data.get('ingredients')
        tags_data = data.get('tags')
        ingredients = []
        tags = []
        if not ingredients_data:
            raise serializers.ValidationError('Добавьте ингредиенты.')
        if not tags_data:
            raise serializers.ValidationError('Добавьте тэги.')
        for ingredient in ingredients_data:
            try:
                Ingredient.objects.get(pk=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Такого ингредиента не существует.'
                )
            if ingredient in ingredients:
                raise serializers.ValidationError(
                    f'{Ingredient.objects.get(pk=ingredient["id"])} уже есть.'
                )
            ingredients.append(ingredient)
        for tag_id in tags_data:
            if tag_id in tags:
                raise serializers.ValidationError(
                    f'Тэг {Tag.objects.get(pk=tag_id)} добавлен повторно.'
                )
            try:
                Tag.objects.get(pk=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError('Такого тэга не существует.')
            tags.append(tag_id)
        return data

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients_data = validated_data.pop('ingredients')

        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:

            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'],
            )
        for tag_id in tags_data:
            recipe.tags.add(Tag.objects.get(pk=tag_id))
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        current_user = self.context.get('request').user
        if instance.author != current_user:
            raise PermissionDenied('У вас нет прав для изменений.')
        instance.ingredients.clear()
        instance.tags.clear()
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.text = validated_data.get('text', instance.text)
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                recipe=instance,
                amount=ingredient['amount'],
            )
        for tag_id in tags_data:
            instance.tags.add(Tag.objects.get(pk=tag_id))
        return instance

    def to_representation(self, instance):
        """Переопределение."""
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context['request']}
        )
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер получения рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True, required=False
    )

    class Meta:
        """Meta."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        """Получение ингредиентов."""
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        ingredients = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = IngredientSerializer(
                recipe_ingredient.ingredient).data
            ingredient_data['amount'] = recipe_ingredient.amount
            ingredients.append(ingredient_data)
        return ingredients

    def get_is_favorited(self, obj):
        """Добавлено ли в избранное."""
        current_user = self.context.get('request').user
        if isinstance(current_user, AnonymousUser):
            return False
        return FavoriteRecipes.objects.filter(
            user=current_user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Добавлено ли в список."""
        current_user = self.context.get('request').user
        if isinstance(current_user, AnonymousUser):
            return False
        return ShoppingCart.objects.filter(
            user=current_user, recipe=obj
        ).exists()


class RecipeShopSerializer(RecipeReadSerializer):
    """Сериалайзер Avatar."""

    class Meta:
        """Meta."""

        model = Recipe
        fields = ('name', 'ingredients')


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер Avatar."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Meta."""

        model = User
        fields = ('avatar',)


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер Subscribe."""

    class Meta:
        """Meta."""

        model = Subscriptions
        fields = ('user', 'subscriber')
        read_only = ('user', 'subscriber')

    def to_representation(self, instance):
        """Переопределение."""
        serializer = SubscriptionSerializer(
            instance, context={'request': self.context['request']}
        )
        return serializer.data

    def validate(self, data):
        """Валидация самоподписки."""
        user = data.get('user')
        subscriber = data.get('subscriber')
        if user == subscriber:
            raise ValidationError('Невозможно подписаться на себя.')
        return data


class SubscriptionSerializer(UserSerializer):
    """Сериалайзер Subscription."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """Рецепты с лимитом."""
        limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = obj.recipes.all()[: int(limit)]
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер ShoppingCart."""

    class Meta:
        """Meta."""

        model = ShoppingCart
        fields = ('user', 'recipe')


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер Favorite."""

    class Meta:
        """Meta."""

        model = FavoriteRecipes
        fields = ('user', 'recipe')
