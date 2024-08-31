import base64

from django.core.files.base import ContentFile
from rest_framework import serializers, validators
import users, recipes
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, TagRecipe
from users.serializers import UserSerializer
from django.db.transaction import atomic


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')
        # validators = [
        #     validators.UniqueTogetherValidator(
        #         queryset=RecipeIngredient.objects.all(),
        #         fields=('recipe', 'ingredients')
        #     )
        # ]

class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
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
        read_only = ('author',)


class RecipeCreateSerializer(serializers.ModelSerializer):
   
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    name = serializers.CharField(max_length=100)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        # validators = [
        #     validators.UniqueTogetherValidator(
        #         queryset=Recipe.objects.all(),
        #         fields=('name', 'ingredients')
        #     )
        # ]

    # def validate_ingredients(self, data):

    # def validate_name(self, value):
    #     if Recipe.objects.filter(
    #         name=value,
    #         author=self.context['request'].user
    #     ).exists() and self.context['request'].method == 'POST':
    #         raise serializers.ValidationError(
    #             'У вас уже есть рецепт с таким названием.'
    #         )
    #     return value

    # def validate_ingredients(self, value):
    #     if not value:
    #         raise serializers.ValidationError(
    #             'Поле ингредиентов не должно быть пустым.'
    #         )
    #     ingredient_ids = []
    #     for ingredient in value:
    #         if ingredient['amount'] < 1:
    #             raise serializers.ValidationError(
    #                 'Количество ингредиентов не должно быть меньше 1.'
    #             )

    #         ingredient_id = ingredient['id']
    #         if ingredient_id in ingredient_ids:
    #             raise serializers.ValidationError(
    #                 'Не должно быть повторяющихся ингредиентов.'
    #             )
    #         ingredient_ids.append(ingredient_id)

    #         if not Ingredient.objects.filter(pk=ingredient_id).exists():
    #             raise serializers.ValidationError(
    #                 f'Ингредиента с id {ingredient_id} не существует.'
    #             )
    #     return value

    # def validate_tags(self, value):
    #     if not value:
    #         raise serializers.ValidationError(
    #             'Поле тэгов не должно быть пустым.'
    #         )

    #     if len(value) != len(set(value)):
    #         raise serializers.ValidationError(
    #             'Не должно быть повторяющихся тэгов.'
    #         )

    #     for tag in value:
    #         if not Tag.objects.filter(pk=tag).exists():
    #             raise serializers.ValidationError(
    #                 f'Тэга с id {tag} не существует.'
    #             )
    #     return value

    # def validate_cooking_time(self, value):
    #     if value < 1:
    #         raise serializers.ValidationError(
    #             'Время готовки должно быть не меньше 1.'
    #         )
    #     return value
    def validate(self, data):

        ingredients_data =  data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError('Добавьте ингредиенты.')
        return data
    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        

        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        ingredients = []
        for ingredient in ingredients_data:
            if ingredient in ingredients:
                raise serializers.ValidationError(f'Ингредиент {Ingredient.objects.get(pk=ingredient['id'])} добавлен повторно.')
            try:
                Ingredient.objects.get(pk=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError('Такого ингредиента не существует.')
            ingredients.append(ingredient)
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'],
            )
        for tag_id in tags_data:
            recipe.tags.add(Tag.objects.get(pk=tag_id))
        return recipe
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
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
    # def update(self, instance, validated_data):
    #     ingredients_data = validated_data.pop('ingredients')
    #     instance.ingredients.clear()
    #     create_recipe_ingredient(instance, ingredients_data)

    #     tags_data = validated_data.pop('tags')
    #     instance.tags.clear()
    #     add_tags_to_recipe(instance, tags_data)
    #     return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context['request']}
        )
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
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
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        ingredients = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = IngredientSerializer(recipe_ingredient.ingredient).data
            ingredient_data['amount'] = recipe_ingredient.amount
            ingredients.append(ingredient_data)
        return ingredients
    # def get_is_favorited(self, obj):
    #     return (
    #         self.context['request'].user.is_authenticated
    #         and UserFavoriteRecipes.objects.filter(
    #             user=self.context['request'].user,
    #             recipe=obj
    #         ).exists()
    #     )

    # def get_is_in_shopping_cart(self, obj):
    #     return (
    #         self.context['request'].user.is_authenticated
    #         and UserRecipeShoppingCart.objects.filter(
    #             user=self.context['request'].user,
    #             recipe=obj
    #         ).exists()
    #     )
