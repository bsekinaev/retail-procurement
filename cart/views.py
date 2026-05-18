from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.shortcuts import get_object_or_404

class CartView(generics.RetrieveAPIView):
    # Просмотр корзины текущего пользователя
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemAddView(generics.CreateAPIView):
    # Добавление товара в корзину
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            return Response({'Ошибка': 'Количество должно быть положительным'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id, is_available=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemUpdateView(generics.UpdateAPIView):
    # Изменения количества товара в корзине
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class CartItemDeleteView(generics.DestroyAPIView):
    # Удаление позиции из корзины
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)