from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TagsViewSet, IngredientsViewSet,
                       FollowListViewSet,
                       FollowCreateDestroyViewSet,
                       RecipeViewSet,
                       FavoriteViewSet,
                       CartViewSet)


router = DefaultRouter()

# Tags
router.register('tags',
                TagsViewSet,
                basename='tags')
# Ingredients
router.register('ingredients',
                IngredientsViewSet,
                basename='ingredients')
# Users
router.register('users/subscriptions',
                FollowListViewSet,
                basename='subscriptions')
router.register(r'users/(?P<pk>\d+)/subscribe',
                FollowCreateDestroyViewSet,
                basename='subscribe')
# Recipes
router.register('recipes/download_shopping_cart',
                CartViewSet,
                basename='download_shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                CartViewSet,
                basename='shopping_cart')
router.register(r'recipes/(?P<pk>\d+)/favorite',
                FavoriteViewSet,
                basename='favorite')
router.register('recipes',
                RecipeViewSet,
                basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
]
