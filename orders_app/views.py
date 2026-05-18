from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Order, OrderItem, Contact
from .serializers import OrderSerializer, OrderConfirmSerializer
from cart.models import Cart

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self,request):
        cart = Cart.objects.filter(user=request.user).prefetch_related('items__product').first()
        if not cart or not cart.items.exists():
            return Response({'Ошибка':'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем или используем контакт
        contact = None
        contact_id = request.data.get('contact_id')
        if contact_id:
            contact = Contact.objects.filter(id=contact_id, user=request.user).first()
        if not contact:
            address = request.data.get('address')
            phone = request.data.get('phone')
            if not address or not phone:
                return Response({'Ошибка':'Не указан адрес доставки и/или телефон!'}, status=status.HTTP_400_BAD_REQUEST)
            contact = Contact.objects.create(user=request.user, address=address, phone=phone)

        # Создаем заказ
        order = Order.objects.create(user=request.user, contact=contact)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            # Уменьшаем остаток товара
            item.product.quantity = max(0, item.product.quantity - item.quantity)
            item.product.save()

        # Очищаем корзину
        cart.items.all().delete()

        # Асинхронная отправка email (заглушка)
        try:
            from api.tasks import send_order_confirmation
            send_order_confirmation.delay(order.id)
        except (ImportError, Exception):
            pass

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
