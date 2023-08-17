from rest_framework import mixins, viewsets

from recipes.models import Tag, Recipe  # isort: skip
from api.serializers import TagSerializer, RecipetSerializer  # isort: skip


class TagListRetrieveViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """Получает теги списком или по одной."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Позволяет выполнять все операции CRUD с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipetSerializer
