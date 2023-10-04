from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=128,
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(3),
            UnicodeUsernameValidator(),
        ],
    )
    first_name = models.CharField(max_length=128, blank=False, null=False)
    last_name = models.CharField(max_length=128, blank=False, null=False)
    email = models.EmailField(
        max_length=254, unique=True, blank=False, null=False
    )
    password = models.CharField(max_length=254, blank=False, null=False)
    AbstractUser._meta.get_field(
        'groups'
    ).remote_field.related_name = 'custom_user_set'
    AbstractUser._meta.get_field(
        'user_permissions'
    ).remote_field.related_name = 'custom_user_set'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, related_name='follower', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='self_follow_forbidden',
            ),
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан(а) на {self.author}'


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
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipeingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipeingredient'
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)])


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
