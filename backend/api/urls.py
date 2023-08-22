from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet, TagListRetrieveViewSet,  # isort: skip
                       IngredientListRetrieveViewSet,  # isort: skip
                       Shopping_CartViewSet)  # isort: skip


router = DefaultRouter()
router.register('tags', TagListRetrieveViewSet)
router.register('ingredients', IngredientListRetrieveViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                Shopping_CartViewSet,
                basename='shopping_cart')


urlpatterns = [
    # path(f'{API_VERSION}/', include('djoser.urls.jwt')),
    # path('recipes/<int:recipe_id>/shopping_cart/',
    #      Shopping_CartViewSet.as_view()),
    path('', include(router.urls)),
]
