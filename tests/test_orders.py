import pytest
from rest_framework.test import APIClient
from rest_framework import status
from users.factories import UserFactory, ProductFactory
from suppliers.models import Supplier
from cart.services import CartService
from orders_app.models import Order

@pytest.mark.django_db
def test_confirm_order_empty_cart():
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.post('/api/v1/orders/confirm/', {'address': 'Test', 'phone': '+79991234567'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_confirm_order_success():
    supplier_user = UserFactory(user_type='supplier')
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
    product = ProductFactory(supplier=supplier, quantity=10)
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)

    CartService.add_item(buyer, product.id, 2)
    resp = client.post('/api/v1/orders/confirm/', {'address': 'ул. Тестовая, 1', 'phone': '+79991234567'})
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data['status'] == 'new'
    assert Order.objects.filter(user=buyer).exists()

@pytest.mark.django_db
def test_confirm_order_insufficient_stock():
    supplier_user = UserFactory(user_type='supplier')
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
    product = ProductFactory(supplier=supplier, quantity=1)
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)

    CartService.add_item(buyer, product.id, 5)
    resp = client.post('/api/v1/orders/confirm/', {'address': 'Test', 'phone': '+79991234567'})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Недостаточно товара' in resp.data['Ошибка']