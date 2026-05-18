from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from .services import OrderService

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

    def post(self, request):
        order, error = OrderService.create_order_from_cart(request.user, request.data)
        if error:
            return error

        # Асинхронная отправка email
        try:
            from api.tasks import send_order_confirmation
            send_order_confirmation.delay(order.id)
        except (ImportError, Exception):
            pass

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)