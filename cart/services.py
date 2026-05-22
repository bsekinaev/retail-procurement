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
            return Response({'Ошибка':'Количество должно быть положительным'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id, is_available=True)
        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    @staticmethod
    def update_item(user, item_id, quantity):
        if quantity < 1:
            return Response({'Ошибка': 'Количество должно быть положительным'}, status=status.HTTP_400_BAD_REQUEST)
        item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        item.quantity = quantity
        item.save()
        return item


    @staticmethod
    def remove_item(user, item_id):
        # Удаление позиции из корзины
        item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        item.delete()
        return None