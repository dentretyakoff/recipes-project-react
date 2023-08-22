from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

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


class Shopping_CartViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Добавление/удаление рецепта в списке покупок."""
    queryset = Shopping_Cart.objects.all()
    serializer_class = Shopping_CartSerializer
    # http_method_names = ['post', 'delete']

    def perform_create(self, serializer):
        # recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        print(serializer)
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        serializer.save(user=user)

    def get_object(self):
        return get_object_or_404(Recipe,
                                 id=self.kwargs.get('recipe_id'))

    # def post(self, request):
    #     serializer = Shopping_CartSerializer()
    #     serializer.is_valid(raise_exception=True)
    #     print(serializer)

    #     # !Юзера нужно получать из request
    #     user = User.objects.get(username='follower')
    #     # recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))

    #     shopping_cart = Shopping_Cart.objects.create(recipe=recipe, user=user)

    #     request = self.context.get('request')
    #     image_url = request.build_absolute_uri(shopping_cart.recipe.image.url)

    #     return Response(
    #         {
    #             'id': shopping_cart.recipe.id,
    #             'name': shopping_cart.recipe.name,
    #             'image': image_url,
    #             'cooking_time': shopping_cart.recipe.cooking_time
    #         }, status=status.HTTP_201_CREATED)
