from django.db import transaction, models
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem, Contact
from cart.models import Cart
from products.models import Product

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, contact_data):
        """
                Принимает пользователя и словарь contact_data с ключами:
                contact_id (опционально), address, phone.
                Возвращает кортеж: (Order, error_response)
                """
        # Получаем корзину
        cart = Cart.objects.filter(user=user).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            return None, Response({'Ошибка': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка остатков с блокировкой
        products = {}
        insufficient = []
        for item in cart.items.all():
            product = Product.objects.select_for_update().get(id=item.product.id)
            if item.quantity > product.quantity:
                insufficient.append(f'{product.name} (доступно {product.quantity})')
            else:
                products[item.product.id] = product

        if insufficient:
            return None, Response(
                {'Ошибка': 'Недостаточно товара: ' + ', '.join(insufficient)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём или используем контакт
        contact = None
        contact_id = contact_data.get('contact_id')
        if contact_id:
            contact = Contact.objects.filter(id=contact_id, user=user).first()
        if not contact:
            address = contact_data.get('address')
            phone = contact_data.get('phone')
            if not address or not phone:
                return None, Response(
                    {'Ошибка': 'Не указан адрес доставки и/или телефон!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            contact = Contact.objects.create(user=user, address=address, phone=phone)

        # Создаём заказ
        order = Order.objects.create(user=user, contact=contact)
        for item in cart.items.all():
            product = products[item.product.id]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )
            # Атомарное уменьшение остатка
            product.quantity = models.F('quantity') - item.quantity
            product.save(update_fields=['quantity'])

        # Очищаем корзину
        cart.items.all().delete()

        return order, None
