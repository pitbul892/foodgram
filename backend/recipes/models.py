"""Модели рецептов и все что с ними связано."""
from core.constants import (INGR_NAME_MAX_LENGHT, INGR_UNIT_MAX_LENGHT,
                            RECIPE_NAME_MAX_LENGHT, TAG_MAX_LENGHT)
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(max_length=TAG_MAX_LENGHT, unique=True)
    slug = models.CharField(max_length=TAG_MAX_LENGHT, unique=True)

    class Meta:
        """Meta."""

        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        """Имя."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=INGR_NAME_MAX_LENGHT, unique=True)
    measurement_unit = models.CharField(max_length=INGR_UNIT_MAX_LENGHT)

    class Meta:
        """Meta."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Имя."""
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    tags = models.ManyToManyField(Tag, blank=False)
    image = models.ImageField(
        upload_to='api/images/',
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGHT)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Meta."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Имя."""
        return self.name

    @property
    def ingredients_with_amount(self):
        """Возвращает список ингредиентов с их количеством."""
        return RecipeIngredient.objects.filter(
            recipe=self).select_related('ingredient')


class RecipeIngredient(models.Model):
    """Модель взаимодействия ингредиентов с рецептами."""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='recipe_ingredients')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Meta."""

        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        """Имя."""
        return f'{self.ingredient} {self.recipe} {self.amount}'


class BaseShopAndFavorite(models.Model):
    """Абстрактная модель списка покупок и избранных."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        abstract = True

    def __str__(self):
        """Имя."""
        return f'{self.recipe} - {self.user} '


class ShoppingCart(BaseShopAndFavorite):
    """Модель списка покупок."""

    class Meta:
        """Meta."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок пользователей'
        db_table = 'shopping_list'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        ]


class FavoriteRecipes(BaseShopAndFavorite):
    """Модель избранных рецептов."""

    class Meta:
        """Meta."""

        verbose_name = 'Избранный рецепт пользователя.'
        verbose_name_plural = 'Избранные рецепты пользователей.'
        db_table = 'favorite_recipes'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            ),
        ]
