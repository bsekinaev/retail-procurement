from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

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
def send_verification_email(order_id):
    from orders_app.models import Order
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Заказ №{order.id} подтвержден'
        message = f'Ваш заказ на сумму {order.total_price} руб принят.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
    except Exception as e:
        pass
