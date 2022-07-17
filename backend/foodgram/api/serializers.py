from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipeAmount,
                            Recipe, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer
from .validators import ingredients_validator

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


class CreateTagSerializer(serializers.ModelSerializer):
    """Сериализатор для создания тэгов"""
    class Meta:
        model = Tag
        fields = ('id')
        lookup_field = 'slug'


class RecipeIngredient(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецептах"""

    class Meta:
        model = IngredientRecipeAmount
        fields = ('id', 'amount',)
        read_only_fields = ('measurement_unit', 'name',)
        lookup_field = 'id'


class RecipeIngredientSerializerTest(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = IngredientRecipeAmount
        fields = ('id', 'amount', 'measurement_unit', 'name',)
        read_only_fields = ('measurement_unit', 'name',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializerTest(
        many=True,
        source='ingredient_amount',
        validators=[ingredients_validator])
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=False)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return Favorite.objects.filter(
                user=user,
                recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,)
    ingredients = RecipeIngredient(many=True,
                                   source='ingredient_amount')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=False)

    class Meta:
        model = Recipe
        fields = ('__all__')

    def generate_recipe_ingr(self, ingredients_data, recipe):

        ingredient_recipe_objs = []

        for ingredient in ingredients_data:
            ingredient_recipe_objs.append(
                IngredientRecipeAmount(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(
                        pk=ingredient['id']),
                    amount=ingredient['amount'])
            )
        return IngredientRecipeAmount.objects.bulk_create(
            ingredient_recipe_objs)

    def create(self, validated_data):
        ingredients = self.context['request'].data['ingredients']
        tags = validated_data.pop('tags')
        validated_data.pop('ingredient_amount')
        ingredients_validator(ingredients)

        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.generate_recipe_ingr(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        request = self.context['request']
        ingredients = request.data['ingredients']

        ingredients_validator(ingredients)

        IngredientRecipeAmount.objects.filter(recipe=instance).delete()

        self.generate_recipe_ingr(ingredients, instance)
        try:
            instance.image = validated_data['image']
        except KeyError:
            pass
        instance.author = request.user
        instance.tags.set(validated_data['tags'])
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.name = validated_data['name']

        instance.save()
        return instance


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


class FollowUserSerializer(CustomUserSerializer):
    """Сериализатор для вывода подписок"""
    recipes = FavoriteRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count',)


class FollowUserCreateSerializer(FollowUserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')


class ShoppingCartRecipeSerializer(FavoriteRecipeSerializer):
    """Сериализатор рецептов для ответа при создании записи в корзине"""
