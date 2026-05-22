from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .services import CartService

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
        # Вызываем сервис
        result = CartService.add_item(request.user, product_id, quantity)
        # Если сервис вернул Response (ошибка), сразу возвращаем её
        if isinstance(result, Response):
            return result
        # Иначе сериализуем созданный/обновлённый item
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemUpdateView(generics.UpdateAPIView):
    # Изменения количества товара в корзине
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def patch(self, request, *args, **kwargs):
        item_id = kwargs['pk']
        quantity = int(request.data.get('quantity', 1))
        result = CartService.update_item(request.user, item_id, quantity)
        if isinstance(result, Response):
            return result
        serializer = self.get_serializer(result)
        return Response(serializer.data)

class CartItemDeleteView(generics.DestroyAPIView):
    # Удаление позиции из корзины
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_destroy(self, instance):
        CartService.remove_item(self.request.user, instance.id)