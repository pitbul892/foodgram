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
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    image = models.ImageField(
        upload_to='api/images/'
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


class TagRecipe(models.Model):
    """Модель взаимодействия тэгов с рецептами."""

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'

    def __str__(self):
        """Имя."""
        return f'{self.tag} {self.recipe}'


class RecipeIngredient(models.Model):
    """Модель взаимодействия ингредиентов с рецептами."""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Meta."""

        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        """Имя."""
        return f'{self.ingredient} {self.recipe} {self.amount}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        ]

    def __str__(self):
        """Имя."""
        return f'{self.recipe} in shop {self.user} '


class FavoriteRecipes(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        """Meta."""

        verbose_name = 'Избранный рецепт пользователя.'
        verbose_name_plural = 'Избранные рецепты пользователей.'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            ),
        ]

    def __str__(self):
        """Имя."""
        return f'{self.recipe} in favorite {self.user} '
