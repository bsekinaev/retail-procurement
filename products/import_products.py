import yaml
from django.db import transaction
from suppliers.models import Supplier
from .models import Category, Product, ProductCharacteristic


def import_products_from_yaml(file_path=None, content=None):
    """
        Импорт товаров из YAML‑файла или строки.

        Ожидается структура:
          - shop: Название поставщика
            categories:
              - name: Название категории
                products:
                  - name: Название товара
                    price: ...
                    quantity: ...
                    parameters:
                      Характеристика1: значение1
                      ...
        """
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    elif content:
        data = yaml.safe_load(content)
    else:
        raise ValueError('Необходимо указать file_path или content')

        # Если данные не список, оборачиваем в список
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise ValueError('Ожидается список магазинов или объект магазина')

    with transaction.atomic():
        for shop_data in data:
            supplier_name = shop_data.get('shop')
            if not supplier_name:
                continue

            supplier, created = Supplier.objects.get_or_create(
                company_name=supplier_name,
                defaults={'user': None}
            )

            categories_data = shop_data.get('categories', [])
            for cat_data in categories_data:
                cat_name = cat_data.get('name')
                if not cat_name:
                    continue

                category, _ = Category.objects.get_or_create(name=cat_name)

                products_data = cat_data.get('products', [])
                for prod_data in products_data:
                    product_name = prod_data.get('name')
                    if not product_name:
                        continue

                    product, product_created = Product.objects.update_or_create(
                        name=product_name,
                        supplier=supplier,
                        defaults={
                            'category': category,
                            'description': prod_data.get('description', ''),
                            'price': prod_data.get('price', 0),
                            'quantity': prod_data.get('quantity', 0),
                            'is_available': True,
                        }
                    )

                    if not product_created:
                        product.characteristics.all().delete()

                    params = prod_data.get('parameters', {})
                    for key, value in params.items():
                        ProductCharacteristic.objects.create(
                            product=product,
                            name=key,
                            value=str(value)
                        )
    return True