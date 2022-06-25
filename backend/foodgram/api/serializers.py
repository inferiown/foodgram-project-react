from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import get_user_model

from rest_framework.validators import UniqueTogetherValidator
from api.validators import validate_year
from recipes.models import (Tag, Recipe, Ingredient,
                            ShoppingCart, Follow, Favorite)
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')
        lookup_field = 'slug'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        lookup_field = 'id'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = ('__all__')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода подписок"""

    class Meta:
        model = Follow
        fields = '__all__'


class FavoriteSerializer(serializers.ModelField):
    """Сериализатор для избранного"""

    class Meta:
        model = Favorite
        fields = '__all__'


class FavoriteRecipeSerializer(RecipeSerializer):
    """Сериализатор рецептов для ответа при создании записи в избранном"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartRecipeSerializer(FavoriteRecipeSerializer):
    """Сериализатор рецептов для ответа при создании записи в корзине"""
