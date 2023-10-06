from django.db import models
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
)

from users.models import User

MIN_VALUE = 1


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    validators = [
        RegexValidator(
            '^#([a-fA-F0-9]{6})',
            message='Поле должно содержать соответствующий HEX-цвет',
        )
    ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes_images/', blank=True)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='recipeingredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(MIN_VALUE)]
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipeingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipeingredient'
    )
    amount = models.IntegerField(validators=[MinValueValidator(MIN_VALUE)])


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.recipe.name} в избранном {self.user.username}'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.recipe.name} в корзине {self.user.username}'
