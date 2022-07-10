from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from api.permissions import IsAuthorOrReadOnlyPermission
from api.serializers import (TagSerializer,
                             RecipeSerializer,
                             IngredientSerializer,
                             FavoriteRecipeSerializer,
                             ShoppingCartRecipeSerializer,
                             CreateRecipeSerializer,
                             FollowUserSerializer,
                             FollowUserCreateSerializer)
from recipes.models import (Tag,
                            Recipe,
                            Ingredient,
                            Follow,
                            Favorite,
                            ShoppingCart,
                            IngredientRecipeAmount)
from .filters import RecipeFilter, IngredientFilter
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.settings import api_settings
from django_filters.rest_framework import DjangoFilterBackend


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
    mixins.UpdateModelMixin,
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
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('name',)


class RecipeViewSet(AllMethodsMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    permission_classes = [AllowAny]
    permission_classes = [IsAuthorOrReadOnlyPermission,
                          IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = (
            self.request.query_params.get('is_in_shopping_cart'))
        if is_favorited == '1':
            favorite_recipes_list = []
            favorite = Favorite.objects.filter(user=self.request.user)
            for element in favorite:
                favorite_recipes_list.append(element.recipe.pk)
            queryset = Recipe.objects.filter(pk__in=favorite_recipes_list)
        if is_in_shopping_cart == '1':
            shopping_cart_list = []
            shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
            for element in shopping_cart:
                shopping_cart_list.append(element.recipe.pk)
            queryset = Recipe.objects.filter(pk__in=shopping_cart_list)
        return queryset

    # Create method
    def create(self, request, *args, **kwargs):
        serializer = CreateRecipeSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    # Update method
    def update(self, request, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CreateRecipeSerializer(instance,
                                            context={'request': request},
                                            data=request.data,
                                            partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet,):
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)

    def list(self, request):
        user = request.user
        user_subscriptions = Follow.objects.filter(user=user)
        queryset = User.objects.filter(following__in=user_subscriptions)
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(page, many=True,
                                          context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
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
            serializer = FollowUserCreateSerializer(
                                              queryset,
                                              context={'request': request,
                                                       'pk': pk})
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
        ing_list = {}
        text = 'Ваш список покупок: \n\n'
        recipes_in_shopping_cart = ShoppingCart.objects.filter(user=user)
        for recipe in recipes_in_shopping_cart:
            ingredient_recipe = IngredientRecipeAmount.objects.filter(
                recipe=recipe.recipe)
            for element in ingredient_recipe:
                if element.ingredient.name in ing_list:
                    ing_list[element.ingredient.name]['Количество'] += (
                        element.amount)
                else:
                    ing_list.update(
                        {element.ingredient.name: {
                            'Количество': element.amount,
                            'Единицы': element.ingredient.measurement_unit}})
        for ing in ing_list:
            amount = ing_list[ing]['Количество']
            unit = ing_list[ing]['Единицы']
            text += ing + ' ' + str(amount) + ' ' + unit + '\n'
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
