from lib2to3.pytree import Base
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Fill database with ingredients'

    def handle(self, *args, **kwargs):
        file = open('recipes/management/commands/data/ingredients.json',
                    encoding='utf-8')
        data = json.loads(file.read())
        ingredient_objs = []
        for ingredient in data:
            name = ingredient['name']
            measurement_unit = ingredient['measurement_unit']
            ingredient_objs.append(
                Ingredient(
                    name=name,
                    measurement_unit=measurement_unit,)
                )
            Ingredient.objects.bulk_create(
                ingredient_objs, ignore_conflicts=True
            )
