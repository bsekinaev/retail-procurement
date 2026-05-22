from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from .models import Cart, CartItem
from products.models import Product
from django.shortcuts import get_object_or_404


class CartService:
    @staticmethod
    def add_item(user, product_id, quantity):
        # Добавление товара в корзину или увеличение кол-во
        if quantity < 1:
            return Response({'Ошибка': 'Количество должно быть положительным'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            product = get_object_or_404(Product, id=product_id, is_available=True)
            cart, _ = Cart.objects.get_or_create(user=user)
            item = CartItem.objects.select_for_update().filter(cart=cart, product=product).first()
            if item:
                item.quantity += quantity
                item.save()
            else:
                item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        return item

    @staticmethod
    def update_item(user, item_id, quantity):
        if quantity < 1:
            return Response({'Ошибка': 'Количество должно быть положительным'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            item = get_object_or_404(CartItem.objects.select_for_update(), id=item_id, cart__user=user)
            item.quantity = quantity
            item.save()
        return item


    @staticmethod
    def remove_item(user, item_id):
        # Удаление позиции из корзины
        with transaction.atomic():
            item = get_object_or_404(CartItem.objects.select_for_update(), id=item_id, cart__user=user)
            item.delete()
        return None