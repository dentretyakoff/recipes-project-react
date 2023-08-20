from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            Shopping_Cart)  # isort: skip
from api.serializers import (TagSerializer, RecipetSerializer,  # isort: skip
                             IngredientSerializer,  # isort: skip
                             Shopping_CartSerializer)  # isort: skip
from users.models import User  # isort: skip


class TagListRetrieveViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """Получает теги списком или по одному."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientListRetrieveViewSet(mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """Получает ингердиенты списком или по одному."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Позволяет выполнять методы GET, POST, PATCH, DELETE с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipetSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class Shopping_CartViewSet(viewsets.ModelViewSet):
    """Добавление рецепта в список покупок."""
    queryset = Shopping_Cart.objects.all()
    serializer_class = Shopping_CartSerializer
    http_method_names = ['post', 'delete']

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        serializer.save(recipe=recipe, user=user)
