import factory
from django.contrib.auth import get_user_model
from suppliers.models import Supplier
from products.models import Product, Category

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    user_type = 'client'
    is_active = True
    is_verified = True


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    company_name = factory.Sequence(lambda n: f'Supplier {n}')
    is_active = True

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    category = factory.SubFactory(CategoryFactory)
    supplier = factory.SubFactory(SupplierFactory)
    price = 1000.00
    quantity = 10
    is_available  = True