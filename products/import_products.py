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
    if isinstance(data, list):
        data = data[0] if data else {}
    elif not isinstance(data, dict):
        raise ValueError('Ожидается объект магазина')

    with transaction.atomic():
        supplier_name = data.get('shop')
        if not supplier_name:
            raise ValueError('Не указано название магазина (shop)')

        supplier, _ = Supplier.objects.get_or_create(
            company_name=supplier_name,
            defaults={'user': None}
        )

        # Сохраняем категории с их id для сопоставления
        categories_by_id = {}
        for cat in data.get('categories', []):
            cat_id = cat.get('id')
            cat_name = cat.get('name')
            if cat_id and cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name)
                categories_by_id[cat_id] = category

        # Импорт товаров из списка goods
        goods = data.get('goods', [])
        for item in goods:
            product_name = item.get('model')
            if not product_name:
                continue

            cat_id = item.get('category')
            category = categories_by_id.get(cat_id)

            product, created = Product.objects.update_or_create(
                name=product_name,
                supplier=supplier,
                defaults={
                    'category': category,
                    'description': item.get('description', ''),
                    'price': item.get('price', 0),
                    'quantity': item.get('quantity', 0),
                    'is_available': True,
                }
            )

            if not created:
                product.characteristics.all().delete()

            params = item.get('parameters', {})
            for key, value in params.items():
                ProductCharacteristic.objects.create(
                    product=product,
                    name=key,
                    value=str(value)
                )
    return True