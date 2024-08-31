from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import core
from core.constants import (
    INGR_NAME_MAX_LENGHT,
    INGR_UNIT_MAX_LENGHT,
    RECIPE_NAME_MAX_LENGHT,
    TAG_MAX_LENGHT
)

User = get_user_model()
class Tag(models.Model):
    name = models.CharField(max_length=TAG_MAX_LENGHT, unique=True)
    slug = models.CharField(max_length=TAG_MAX_LENGHT, unique=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=INGR_NAME_MAX_LENGHT, unique=True)
    measurement_unit = models.CharField(max_length=INGR_UNIT_MAX_LENGHT)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    # , through_fields=('recipe', 'ingredient'),
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    image = models.ImageField(
        upload_to='api/images/'
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGHT)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()

    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe} {self.amount}'

