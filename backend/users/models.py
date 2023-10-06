from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator

USERNAME_MIN_LENGTH = 3


class User(AbstractUser):
    username = models.CharField(
        max_length=128,
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(USERNAME_MIN_LENGTH),
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
