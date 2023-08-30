from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.pagination import PageNumberPagination

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            ShoppingCart, Favorite)  # isort: skip
from api.serializers import (TagSerializer, RecipeSerializer,  # isort: skip
                             IngredientSerializer,  # isort: skip
                             UserSerializer,  # isort: skip
                             RecipeShortSerializer)  # isort: skip
from users.models import User, Follow  # isort: skip
from api.utils import (make_file,  # isort: skip
                       custom_post, custom_delete)  # isort: skip


class TagListRetrieveViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """Получает теги списком или по одному."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientListRetrieveViewSet(mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """Получает ингердиенты списком или по одному."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Выполняет методы GET, POST, PATCH, DELETE с рецептами.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk) -> Response:
        """Добавляет/удаляет рецепт в корзине."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        # Создание записи
        if request.method == 'POST':
            message = 'Рецепт уже в корзине.'
            response = custom_post(
                request, recipe, user, ShoppingCart, message)
            return response

        # Удаление записи
        if request.method == 'DELETE':
            message = 'Рецепт не найден в корзине.'
            response = custom_delete(data={'recipe': recipe, 'user': user},
                                     model=ShoppingCart, message=message)
            return response

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        """Добавляет/удаляет рецепт в избранном."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        # Создание записи
        if request.method == 'POST':
            message = 'Рецепт уже в избранном.'
            response = custom_post(
                request, recipe, user, Favorite, message)
            return response

        # Удаление записи
        if request.method == 'DELETE':
            message = 'Рецепт не найден в избранном.'
            response = custom_delete(data={'recipe': recipe, 'user': user},
                                     model=Favorite, message=message)
            return response

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingr_list = {}
        user = request.user
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


class CustomUserViewSet(DjoserUserViewSet):
    """
    Расширяет стандарный UserViewSet из djoser, для работы
    url-ов subscriptions и subscribe.
    """

    @action(detail=False)
    def subscriptions(self, request):
        """Список подписок пользователя."""
        pagination = PageNumberPagination()
        user = request.user
        follows = user.follower.all(
            ).select_related('author'
                             ).prefetch_related('author__recipes')
        authors = [follow.author for follow in follows]
        page = pagination.paginate_queryset(authors, request)
        data = UserSerializer(page,
                              many=True,
                              context={'request': request}).data

        for author in authors:
            for author_data in data:
                if author_data['id'] == author.id:
                    recipes = RecipeShortSerializer(
                        author.recipes.all(),
                        many=True,
                        context={'request': request}).data
                    author_data['recipes'] = recipes
                    author_data['recipes_count'] = author.recipes.all().count()

        return pagination.get_paginated_response(data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id) -> Response:
        """Создает/удаляет подписку на автора."""
        author = get_object_or_404(User, id=id)
        user = request.user

        # Создание записи
        if request.method == 'POST':
            try:
                Follow.objects.create(author=author, user=user)
                recipes = RecipeShortSerializer(
                        author.recipes.all(),
                        many=True,
                        context={'request': request}).data
                data = UserSerializer(author,
                                      context={'request': request}).data
                data['recipes'] = recipes
                data['recipes_count'] = author.recipes.all().count()
                return Response(data,
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'errors': 'Уже в подписках.'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Удаление записи
        if request.method == 'DELETE':
            message = 'Подписка отсутсвует'
            response = custom_delete(data={'author': author, 'user': user},
                                     model=Follow, message=message)
            return response
