from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from .models import Supplier
from orders_app.serializers import OrderSerializer
from products.tasks import do_import


class SupplierOrdersView(generics.ListAPIView):
    # Заказы, содержащие товары данного поставщика
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        supplier = Supplier.objects.filter(user=self.request.user).first()
        if not supplier:
            return Supplier.objects.none()
        return Order.objects.filter(items__product__supplier=supplier).distinct()


class SupplierStatusView(APIView):
    # Включение/отключение приема заказов поставщиком
    permission_classes = [permissions.IsAuthenticated]

    def put(self,request):
        supplier = Supplier.objects.filter(user=self.request.user).first()
        if not supplier:
            return Response({'Ошибка':'Вы не являетесь поставщиком'}, status=403)
        is_active = request.data.get('is_active', True)
        supplier.is_active = is_active
        supplier.save()
        return Response({'status':'ok','is_active':supplier.is_active})


class SupplierImportView(APIView):
    # Запуск импорта товаров через Celery
    permission_classes = [permissions.IsAdminUser]

    def post(self,request):
        file_path = request.data.get('file_path')
        content = request.data.get('content')
        if not file_path and not content:
            return Response({'Ошибка':'Укажите file_path или content'}, status=400)
        task = do_import.delay(file_path=file_path,content=content)
        return Response({'task_id': task.task_id}, status=202)
