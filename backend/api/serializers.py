"""Сериализаторы для работы с рецептами, ингредиентами и подписками."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Subscriptions

User = get_user_model()


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
    image = Base64ImageField(required=True, allow_null=False)
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

    def validate_image(self, value):
        """Пустое значение картинки."""
        if not value:
            raise serializers.ValidationError("Пустая строка не допустима.")
        return value

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
        validated_data['author'] = self.context['request'].user
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
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.text = validated_data.get('text', instance.text)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                recipe=instance,
                amount=ingredient['amount'],
            )
        instance.tags.set(tags_data)
        instance.save()
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
        recipe_ingredients = obj.ingredients.select_related('ingredient')
        return [
            {
                "id": recipe_ingredient.ingredient.id,
                "name": recipe_ingredient.ingredient.name,
                "measurement_unit":
                recipe_ingredient.ingredient.measurement_unit,
                "amount": recipe_ingredient.amount
            }
            for recipe_ingredient in recipe_ingredients
        ]

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
