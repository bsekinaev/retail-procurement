import pytest
from rest_framework.test import APIClient
from rest_framework import status
from users.factories import UserFactory, ProductFactory
from suppliers.models import Supplier
from users.models import User

@pytest.mark.django_db
def test_full_purchase():
    # 0. Подготовка тестовых данных
    # Создаём пользователя-поставщика
    supplier_user = UserFactory(user_type='supplier')
    # Создаём запись поставщика (сохраняем объект)
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')

    # Создаём товар, передавая уже существующего поставщика
    product = ProductFactory(supplier=supplier, quantity=10)


    # 1. Регистрация покупателя

    client = APIClient()
    register_data = {
        'email': 'buyer@example.com',
        'password': 'testpass123',
        'user_type': 'client',
    }
    response = client.post('/api/v1/auth/register/', data=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'Сообщение' in response.data


    # 2. Подтверждение email

    user = User.objects.get(email='buyer@example.com')
    verify_url = f'/api/v1/auth/verify-email/?token={user.verification_token}'
    response = client.get(verify_url)
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_verified
    assert user.is_active


    # 3. Вход в систему

    login_data = {'email': 'buyer@example.com', 'password': 'testpass123'}
    response = client.post('/api/v1/auth/login/', data=login_data)
    assert response.status_code == status.HTTP_200_OK
    access_token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    # 4. Получение списка товаров

    response = client.get('/api/v1/products/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] >= 1
    product_ids = [p['id'] for p in response.data['results']]
    assert product.id in product_ids


    # 5. Добавление товара в корзину

    cart_data = {'product_id': product.id, 'quantity': 2}
    response = client.post('/api/v1/cart/items/', data=cart_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['quantity'] == 2

    # 6. Оформление заказа

    order_data = {'address': 'Test Address', 'phone': '+79991234567'}
    response = client.post('/api/v1/orders/confirm/', data=order_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == 'new'
    order_id = response.data['id']

    # 7. Проверка заказа в списке

    response = client.get('/api/v1/orders/')
    assert response.status_code == status.HTTP_200_OK
    order_ids = [o['id'] for o in response.data['results']]
    assert order_id in order_ids