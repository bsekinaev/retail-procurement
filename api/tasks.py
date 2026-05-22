from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.base import ContentFile
import requests

@shared_task
def send_verification_email(user_id):
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        subject = 'Подтверждение регистрации'
        message = f'Ваш код подтверждения: {user.verification_token}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return f'Письмо успешно отправлено!'
    except User.DoesNotExist:
        return 'Пользователь не найден'

@shared_task
def send_order_confirmation(order_id):
    from orders_app.models import Order
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Заказ №{order.id} подтвержден'
        message = f'Ваш заказ на сумму {order.total_price} руб принят.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
    except Exception as e:
        pass


@shared_task
def send_order_status_notification(order_id, new_status):
    from orders_app.models import Order
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Статус заказа №{order.id} изменён'
        message = f'Ваш заказ переведён в статус "{new_status}"'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
    except Order.DoesNotExist:
        pass

@shared_task
def process_avatar_async(user_id, image_url):
    from users.models import User
    user = User.objects.get(id=user_id)
    # Загружаем изображение по URL (например, из соцсети)
    response = requests.get(image_url)
    if response.status_code == 200:
        # Имя файла можно вытащить из URL или сгенерировать
        filename = f'avatar_{user_id}.jpg'
        user.avatar.save(filename, ContentFile(response.content), save=True)