import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **kwarg):
        try:
            with open('../data/ingredients.csv',
                      encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in tqdm(reader, desc='Ingredients'):
                    _, created = Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1])
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты загружены.'))
        except Exception as e:
            print(f'Ошибка загрузки данных: {e}')
