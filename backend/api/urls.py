from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet, TagListRetrieveViewSet,  # isort: skip
                       IngredientListRetrieveViewSet)  # isort: skip


router = DefaultRouter()
router.register('tags', TagListRetrieveViewSet)
router.register('ingredients', IngredientListRetrieveViewSet)
router.register('recipes', RecipeViewSet)


urlpatterns = [
    # path(f'{API_VERSION}/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
