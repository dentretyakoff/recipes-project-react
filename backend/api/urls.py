from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, IngredientListRetrieveViewSet,
                       RecipeViewSet, TagListRetrieveViewSet)

router = DefaultRouter()
router.register('tags', TagListRetrieveViewSet)
router.register('ingredients', IngredientListRetrieveViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
