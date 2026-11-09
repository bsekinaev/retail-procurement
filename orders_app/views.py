import logging

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.tasks import send_order_confirmation
from .models import Order
from .serializers import OrderSerializer
from .services import OrderService

logger = logging.getLogger(__name__)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

class OrderConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order, error = OrderService.create_order_from_cart(request.user, request.data)
        if error:
            return error

        # Заказ уже закоммичен сервисным слоем; сбой уведомления не
        # отменяет оформление. Ошибку брокера фиксируем без тела исключения:
        # оно может содержать адрес подключения или реквизиты.
        try:
            send_order_confirmation.delay(order.id)
        except Exception as exc:
            logger.error(
                "order_confirmation_enqueue_failed order_id=%s error_type=%s",
                order.id,
                type(exc).__name__,
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)