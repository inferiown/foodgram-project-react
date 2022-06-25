from http import HTTPStatus
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from api.pagination import RecipePagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from api.serializers import (TagSerializer,
                             RecipeSerializer,
                             IngredientSerializer,
                             FollowSerializer,
                             FavoriteSerializer,
                             FavoriteRecipeSerializer,
                             ShoppingCartRecipeSerializer)
from recipes.models import Tag, Recipe, Ingredient, Follow, Favorite, ShoppingCart
from users.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import FileResponse, HttpRequest, HttpResponse


User = get_user_model()


class AllMethodsMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class ListCreateDestroyMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CreateDestroyMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class ListRetreiveMixin(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TagsViewSet(ListRetreiveMixin):
    """Вьюсет для обработки тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'id'
    pagination_class = None


class IngredientsViewSet(ListRetreiveMixin):
    """Вьюсет для обработки ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'id'


class RecipeViewSet(AllMethodsMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = 'id'


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet,):
    pagination_class = RecipePagination
    lookup_field = 'id'

    def list(self, request):
        user = request.user
        user_subscriptions = Follow.objects.filter(user=user)
        queryset = User.objects.filter(following__in=user_subscriptions)
        serializer = CustomUserSerializer(queryset, many=True)
        return Response(serializer.data)


class FollowCreateDestroyViewSet(CreateDestroyMixin):
    lookup_field = 'id'

    def create(self, request, pk):
        queryset = Follow.objects.all()
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if user == author:
            return Response('You can\'t follow yourself',
                            status=status.HTTP_400_BAD_REQUEST)
        elif not Follow.objects.filter(user=user, author=author):
            Follow.objects.create(user=user, author=author)
            queryset = author
            serializer = CustomUserSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(f'You\'re already following {author}',
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if not Follow.objects.filter(user=user, author=author):
            return Response(f'You\'re not following {author}',
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            Follow.objects.filter(user=user, author=author).delete()
            return Response(f'Successfully unfollowed user {author.username}',
                            status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateDestroyMixin):
    lookup_field = 'id'

    def create(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe):
            Favorite.objects.create(user=user, recipe=recipe)
            queryset = get_object_or_404(Recipe, pk=pk)
            serializer = FavoriteRecipeSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(f'You\'ve already added {recipe.name} to starred',
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe):
            return Response(f'You don\'t have {recipe.name} in starred',
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(f'Successfully removed {recipe.name} from starred',
                            status=status.HTTP_204_NO_CONTENT)


class CartViewSet(ListCreateDestroyMixin):
    def generate_shopping_list(self, user):
        ing_list = ''
        recipes_in_shopping_cart = ShoppingCart.objects.filter(user=user)
        for recipe in recipes_in_shopping_cart:
            ingredients = Ingredient.objects.filter(recipes=recipe.recipe)
            for ingredient in ingredients:
                ing_list += f'{ingredient.name} {ingredient.measurement_unit} \n'

        text = ing_list
        return text

    def list(self, request, *args, **kwargs):
        shopping_list = self.generate_shopping_list(request.user)
        response = HttpResponse(shopping_list,
                                status=status.HTTP_200_OK,
                                content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="my_shopping_list.txt"')
        return response

    def create(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe):
            ShoppingCart.objects.create(user=user, recipe=recipe)
            queryset = get_object_or_404(Recipe, pk=recipe_id)
            serializer = ShoppingCartRecipeSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(f'You\'ve already added {recipe.name}'
                            ' to shopping cart',
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe):
            return Response(f'You don\'t have {recipe.name} in shopping cart',
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(f'Successfully removed {recipe.name}'
                            ' from shopping cart',
                            status=status.HTTP_204_NO_CONTENT)
