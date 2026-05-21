import pytest
from rest_framework.test import APIClient
from rest_framework import status
from users.factories import UserFactory, ProductFactory
from suppliers.models import Supplier
from cart.models import CartItem

@pytest.mark.django_db
def test_add_to_cart():
    # Добавление товара в корзину авторизованным пользователем
    # Подготовка: активный поставщик и товар
    supplier_user = UserFactory(user_type='supplier')
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
    product = ProductFactory(supplier=supplier, quantity=10)

    # Покупатель
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)

    response = client.post('/api/v1/cart/items/', {'product_id': product.id, 'quantity': 2})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['quantity'] == 2

    # Проверяем, что запись появилась в БД
    assert CartItem.objects.filter(cart__user=buyer, product=product).exists()

@pytest.mark.django_db
def test_add_to_cart_negative_quantity():
    # Отрицательное количество должно отклоняться
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    # Товар с фабрики (автоматически создаст поставщика и категорию)
    product = ProductFactory(quantity=10)
    response = client.post('/api/v1/cart/items/', {'product_id': product.id, 'quantity': -1})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_update_cart_quantity():
    # Изменение количества товара в корзине
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    product = ProductFactory(quantity=10)
    # Добавляем товар
    add_resp = client.post('/api/v1/cart/items/', {'product_id': product.id, 'quantity': 1})
    item_id = add_resp.data['id']

    # Обновляем количество
    update_resp = client.patch(f'/api/v1/cart/items/{item_id}/', {'quantity': 5})
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.data['quantity'] == 5

@pytest.mark.django_db
def test_delete_from_cart():
    # Удаление позиции из корзины
    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    product = ProductFactory(quantity=10)
    add_resp = client.post('/api/v1/cart/items/', {'product_id': product.id, 'quantity': 1})
    item_id = add_resp.data['id']

    delete_resp = client.delete(f'/api/v1/cart/items/{item_id}/delete/')
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT
    assert not CartItem.objects.filter(id=item_id).exists()