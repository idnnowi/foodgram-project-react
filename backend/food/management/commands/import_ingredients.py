import csv
from typing import Any

from django.core.management import BaseCommand, CommandParser

from food.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from .csv file'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--path', type=str, help="Path to .csv file")

    def handle(self, *args: Any, **options: Any):
        csv_file = options['path']

        with open(csv_file, 'rt', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
            self.stdout.write('The data from sheets imported.')
