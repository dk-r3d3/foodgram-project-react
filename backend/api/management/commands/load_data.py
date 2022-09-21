import csv


from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from recipes.models import Ingredients


class Command(BaseCommand):
    """Скрипт для загрузки ингредиентов в БД на сервере."""

    help = 'loading ingredients from data in json'

    def handle(self, *args, **options):
        try:
            with open('api/data/ingredients.csv', 'r',
                      encoding='utf-8') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    name, measurement_unit = row
                    try:
                        Ingredients.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    except IntegrityError:
                        print(f'Ингредиент {name} {measurement_unit} '
                              f'уже есть в базе')
        except FileNotFoundError:
            raise CommandError('Файл отсутствует в директории data')
