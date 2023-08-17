from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, TagListRetrieveViewSet  # isort: skip


router = DefaultRouter()
router.register('tag', TagListRetrieveViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    # path(f'{API_VERSION}/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
