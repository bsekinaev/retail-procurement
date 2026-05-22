import pytest
from rest_framework.test import APIClient
from rest_framework import status
from users.factories import UserFactory, ProductFactory
from suppliers.models import Supplier

@pytest.mark.django_db
def test_product_list():
    supplier_user = UserFactory(user_type='supplier')
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
    ProductFactory.create_batch(3, supplier=supplier)

    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.get('/api/v1/products/')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 3
    assert len(resp.data['results']) == 3

@pytest.mark.django_db
def test_product_filter_by_category():
    supplier_user = UserFactory(user_type='supplier')
    supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
    p1 = ProductFactory(supplier=supplier, category__name='Электроника')
    p2 = ProductFactory(supplier=supplier, category__name='Книги')

    buyer = UserFactory()
    client = APIClient()
    client.force_authenticate(user=buyer)
    resp = client.get('/api/v1/products/?category=Электроника')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 1
    assert resp.data['results'][0]['id'] == p1.id