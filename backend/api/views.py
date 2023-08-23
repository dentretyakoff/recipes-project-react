from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            ShoppingCart)  # isort: skip
from api.serializers import (TagSerializer, RecipetSerializer,  # isort: skip
                             IngredientSerializer)  # isort: skip
from users.models import User  # isort: skip
from api.utils import make_file  # isort: skip


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
    """
    Выполняет методы GET, POST, PATCH, DELETE с рецептами.
    Добавляет/удаляет рецепт в корзине.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipetSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')

        # Создание записи в корзине
        if request.method == 'POST':
            try:
                ShoppingCart.objects.create(recipe=recipe, user=user)
                image_url = request.build_absolute_uri(recipe.image.url)
                return Response({'id': recipe.id,
                                 'name': recipe.name,
                                 'image': image_url,
                                 'cooking_time': recipe.cooking_time},
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'errors': 'Рецепт уже в корзине.'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Удаление записи из корзины
        if request.method == 'DELETE':
            try:
                shopping_cart = user.shopping_carts.get(recipe=recipe)
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response({'errors': 'Рецепт не найден в корзине.'},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingr_list = {}
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        shopping_carts = user.shopping_carts.all().select_related('recipe')

        for shopping_cart in shopping_carts:
            recipe = shopping_cart.recipe
            recipe_ingredients = recipe.recipe_igredient.all().select_related(
                'ingredient')
            for recipe_ingredient in recipe_ingredients:
                name = recipe_ingredient.ingredient.name
                amount = recipe_ingredient.amount
                ingr_list.setdefault(name, 0)
                ingr_list[name] += amount
        return make_file(ingr_list)
