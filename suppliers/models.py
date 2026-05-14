from django.db import models
from django.conf import settings


class Supplier(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supplier_profile',
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    company_name = models.CharField(max_length=200, verbose_name='Название компании')
    is_active = models.BooleanField(default=True, verbose_name='Принимает заказы')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = verbose_name

        def __str__(self):
            return self.company_name