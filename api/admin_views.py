import csv
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from api.permissions import IsAdmin
from orders_app.models import Order
from api.tasks import send_order_status_notification
from django.http import HttpResponse
from products.models import Product

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated,IsAdmin])
def change_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'Ошибка':'Заказ не найден'},status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if  not new_status or new_status not in dict(Order.Status.choices):
        return Response({'Ошибка':'Некорректный статус'},status=status.HTTP_400_BAD_REQUEST)

    old_status = order.status
    order.status = new_status
    order.save()

    # Асинхронная отправка уведомлений
    try:
        send_order_status_notification.delay(order_id, new_status)
    except Exception as e:
        pass

    return Response({
        'Cообщение': f'Статус заказа изменен с "{old_status}" на "{new_status}"'
    },status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated,IsAdmin])
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Категория', 'Поставщик', 'Цена', 'Остаток'])
    products = Product.objects.select_related('category','supplier').all()
    for p in products:
        writer.writerow([p.id,p.name,p.category.name,p.supplier.company_name,p.price,p.quantity])
    return response