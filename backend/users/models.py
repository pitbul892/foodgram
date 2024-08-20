from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    
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
    username = models.CharField(
        
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы',
            )
        ],
    
        max_length=150,
        verbose_name='Уникальный юзернейм',
        
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ('username',)

    def __str__(self):
        return self.username

class Subscriptions(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user')
    subscriber = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='subscriber')


    class Meta:
        verbose_name = 'Подписки'
