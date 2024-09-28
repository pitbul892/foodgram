"""Модели пользователя и все что с ним связано."""
from core.constants import FIRST_LAST_NAME
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserEmail(AbstractUser):
    """Кастомная модель пользоваетля."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'username',
    ]
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_LAST_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=FIRST_LAST_NAME,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        null=True,
        blank=True,
    )

    class Meta:
        """Meta."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Имя."""
        return self.username


class Subscriptions(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        UserEmail, on_delete=models.CASCADE, related_name='user')
    subscriber = models.ForeignKey(
        UserEmail,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )

    class Meta:
        """Meta."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscriber')),
                name='check_user_subscriber'
            ),
            models.UniqueConstraint(
                fields=['user', 'subscriber'],
                name='unique_user_subscriber'
            ),
        ]

    def __str__(self):
        """Имя."""
        return f'{self.subscriber} подписан на {self.user}'
