from django.db import models
from django.conf import settings
from products.models import Product


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Пользователь'
    )
    address = models.TextField(verbose_name='Адрес доставки')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.user.email} - {self.address[:50]}'


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        CONFIRMED = 'confirmed', 'Подтверждён'
        PROCESSING = 'processing', 'В обработке'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Контакт доставки'
    )
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


    def __str__(self):
        return f'Заказ №{self.id} от {self.user.email}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    @property
    def total_price(self):
        return self.price * self.quantity
