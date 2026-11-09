"""Регрессии постановки email-уведомлений в Celery.

Сценарии проверяют сохранность заказа при недоступном брокере и
распространение ошибки worker, не отправляя настоящие письма.
"""

import logging
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from api.tasks import send_order_confirmation
from cart.models import CartItem
from cart.services import CartService
from orders_app.models import Contact, Order
from suppliers.models import Supplier
from users.factories import ProductFactory, UserFactory


@pytest.fixture
def checkout():
    supplier_user = UserFactory(user_type="supplier")
    supplier = Supplier.objects.create(
        user=supplier_user, company_name="Test Supplier"
    )
    product = ProductFactory(supplier=supplier, quantity=10)
    buyer = UserFactory()
    CartService.add_item(buyer, product.id, 2)

    client = APIClient()
    client.force_authenticate(user=buyer)
    return client, buyer, product


@pytest.mark.django_db
def test_confirm_order_enqueues_notification_once(checkout):
    client, buyer, product = checkout
    with patch("orders_app.views.send_order_confirmation.delay") as enqueue:
        response = client.post(
            "/api/v1/orders/confirm/",
            {"address": "Тестовая, 1", "phone": "+79990000000"},
        )

    assert response.status_code == status.HTTP_201_CREATED
    order = Order.objects.get(user=buyer)
    assert response.data["id"] == order.id
    enqueue.assert_called_once_with(order.id)


@pytest.mark.django_db
def test_broker_failure_does_not_rollback_or_duplicate_order(checkout, caplog):
    client, buyer, product = checkout
    sensitive_message = "FAKE_BROKER_TOKEN_MUST_NOT_APPEAR"

    with patch(
        "orders_app.views.send_order_confirmation.delay",
        side_effect=RuntimeError(sensitive_message),
    ) as enqueue:
        with caplog.at_level(logging.ERROR, logger="orders_app.views"):
            response = client.post(
                "/api/v1/orders/confirm/",
                {"address": "Тестовая, 1", "phone": "+79990000000"},
            )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "new"
    order = Order.objects.get(user=buyer)
    assert response.data["id"] == order.id
    enqueue.assert_called_once_with(order.id)

    product.refresh_from_db()
    assert product.quantity == 8
    assert not CartItem.objects.filter(cart__user=buyer).exists()

    assert "order_confirmation_enqueue_failed" in caplog.text
    assert f"order_id={order.id}" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
    assert sensitive_message not in caplog.text

    # Повтор после неопределённого статуса уведомления не должен
    # создавать второй заказ: корзина уже очищена.
    repeated = client.post(
        "/api/v1/orders/confirm/",
        {"address": "Тестовая, 1", "phone": "+79990000000"},
    )
    assert repeated.status_code == status.HTTP_400_BAD_REQUEST
    assert Order.objects.filter(user=buyer).count() == 1


@pytest.mark.django_db
def test_confirmation_worker_propagates_mail_failure():
    buyer = UserFactory()
    contact = Contact.objects.create(
        user=buyer, address="Тестовая, 1", phone="+79990000000"
    )
    order = Order.objects.create(user=buyer, contact=contact)

    with patch("api.tasks.send_mail", side_effect=RuntimeError("SMTP failure")):
        with pytest.raises(RuntimeError, match="SMTP failure"):
            send_order_confirmation.run(order.id)


@pytest.mark.django_db
def test_confirmation_worker_sends_to_order_owner():
    buyer = UserFactory()
    contact = Contact.objects.create(
        user=buyer, address="Тестовая, 1", phone="+79990000000"
    )
    order = Order.objects.create(user=buyer, contact=contact)

    with patch("api.tasks.send_mail", return_value=1) as send:
        send_order_confirmation.run(order.id)

    send.assert_called_once()
    args, _kwargs = send.call_args
    assert args[0] == f"Заказ №{order.id} подтвержден"
    assert args[3] == [buyer.email]


@pytest.mark.django_db
def test_confirmation_worker_rejects_zero_mail_result():
    buyer = UserFactory()
    contact = Contact.objects.create(
        user=buyer, address="Тестовая, 1", phone="+79990000000"
    )
    order = Order.objects.create(user=buyer, contact=contact)

    with patch("api.tasks.send_mail", return_value=0) as send:
        with pytest.raises(RuntimeError, match="order_confirmation_not_sent"):
            send_order_confirmation.run(order.id)

    send.assert_called_once()
