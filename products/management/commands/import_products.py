from django.core.management import BaseCommand
from products.import_products import import_products_from_yaml

class Command(BaseCommand):
    help = 'Импорт товаров из YAML‑файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            import_products_from_yaml(file_path=file_path)
            self.stdout.write(self.style.SUCCESS('Импорт успешно завершен'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка импорта:{e}'))