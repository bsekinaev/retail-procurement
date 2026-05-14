from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        CLIENT = 'client', 'Покупатель'
        SUPPLIER = 'supplier', 'Поставщик'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField('email address', unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name='Тип пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} ({self.get_user_type_display()})'
