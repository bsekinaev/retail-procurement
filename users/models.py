from django.contrib.auth.models import AbstractUser
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

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
    is_verified = models.BooleanField(default=False, verbose_name='Email подтверждён')
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    avatar = ProcessedImageField(
        upload_to='avatars',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 80},
        blank=True,
        null=True
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.email} ({self.get_user_type_display()})'