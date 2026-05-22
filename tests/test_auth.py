import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from django.core.cache import cache

@pytest.mark.django_db
def test_register():
    # Успешная регистрация нового пользователя
    client = APIClient()
    data = {
        'email': 'auth_test@example.com',
        'password': 'testpass123',
        'user_type': 'client'
    }
    response = client.post('/api/v1/auth/register/', data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'Сообщение' in response.data

@pytest.mark.django_db
def test_register_duplicate():
    #  Попытка зарегистрировать уже существующий email
    User.objects.create_user(email='duplicate@example.com', username='duplicate', password='testpass123')
    client = APIClient()
    data = {
        'email': 'duplicate@example.com',
        'password': 'testpass123',
        'user_type': 'client'
    }
    response = client.post('/api/v1/auth/register/', data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_login_success():
    # Успешный вход активного верифицированного пользователя
    user = User.objects.create_user(email='login_test@example.com', username='login_test', password='testpass123',
                                    is_active=True, is_verified=True)
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {'email': 'login_test@example.com', 'password': 'testpass123'})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_login_inactive_user():
    # Неактивный пользователь не может войти
    user = User.objects.create_user(email='inactive@example.com', username='inactive', password='testpass123',
                                    is_active=False, is_verified=False)
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {'email': 'inactive@example.com', 'password': 'testpass123'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_verify_email():
    #  Подтверждение email по валидному токену
    user = User.objects.create_user(email='verify@example.com', username='verify', password='testpass123',
                                    is_active=False, is_verified=False)
    token = 'abcdef123456'
    user.verification_token = token
    user.save()
    client = APIClient()
    response = client.get(f'/api/v1/auth/verify-email/?token={token}')
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.is_verified
    assert user.is_active

@pytest.mark.django_db
@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
})
def test_login_throttle():
    from django.core.cache import cache
    cache.clear()
    client = APIClient()
    url = '/api/v1/auth/login/'
    data = {'email': 'throttle@example.com', 'password': 'wrongpass'}
    # 5 запросов (лимит scope 'login')
    for _ in range(5):
        resp = client.post(url, data)
        assert resp.status_code == 401
    # 6-й запрос должен вернуть 429
    resp = client.post(url, data)
    assert resp.status_code == 429

@pytest.mark.django_db
def test_social_auth_redirect():
    client = APIClient()
    resp = client.get('/auth/social/login/google-oauth2/')
    assert resp.status_code == 302