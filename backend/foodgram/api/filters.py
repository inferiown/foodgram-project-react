from django_filters.rest_framework import BaseInFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class CharFilterInFilter(BaseInFilter, CharFilter):
    pass


class RecipeFilter(FilterSet):
    tags = CharFilterInFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )
    name = CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'name')


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
