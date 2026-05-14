from celery import shared_task
from .import_products import  import_products_from_yaml

@shared_task(bind=True, max_retries=3)
def do_import(self, content=None, file_path=None):
    # Асинхронный импорт товара
    # Можно передать либо content (строка YAML), либо file_path.
    try:
        import_products_from_yaml(content=content, file_path=file_path)
        return {'status':'success'}
    except Exception as e:
        raise self.retry(exc=e)
