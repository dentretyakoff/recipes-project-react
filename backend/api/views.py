from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearch
from api.pagination import CustomPagination
from api.permissions import ReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserSerializer, ShoppingCartSerializer,
                             FavoriteSerializer)
from api.utils import custom_delete, make_file
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User


class TagListRetrieveViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """Получает теги списком или по одному."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [ReadOnly | IsAuthenticated]


class IngredientListRetrieveViewSet(mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """Получает ингердиенты списком или по одному."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [ReadOnly | IsAuthenticated]
    filter_backends = (IngredientSearch, filters.OrderingFilter)
    ordering = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Выполняет методы GET, POST, PATCH, DELETE с рецептами.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [ReadOnly | IsAuthenticated]
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-id',)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        is_favorited = self.request.query_params.get('is_favorited')
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')

        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_carts__user=user)
        if is_favorited is not None:
            queryset = queryset.filter(favorites__user=user)
        if tags:
            queryset = queryset.filter(
                recipe_tag__tag__slug__in=tags).distinct()
        if author is not None:
            queryset = queryset.filter(author=author)

        return queryset

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk) -> Response:
        """Добавляет/удаляет рецепт в корзине."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        # Создание записи
        if request.method == 'POST':
            serilizer = ShoppingCartSerializer(
                recipe,
                data={},
                context={'request': request})
            serilizer.is_valid(raise_exception=True)
            user.shopping_carts.create(recipe=recipe)

            return Response(serilizer.data, status=status.HTTP_201_CREATED)

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
            serilizer = FavoriteSerializer(
                recipe,
                data={},
                context={'request': request})
            serilizer.is_valid(raise_exception=True)
            user.favorites.create(recipe=recipe)

            return Response(serilizer.data, status=status.HTTP_201_CREATED)

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
        shopping_cart = user.shopping_carts.all().select_related('recipe')

        for shopping_cart in shopping_cart:
            recipe = shopping_cart.recipe
            recipe_ingredients = recipe.recipe_igredient.all().select_related(
                'ingredient')
            for recipe_ingredient in recipe_ingredients:
                name = (f'{recipe_ingredient.ingredient.name} '
                        f'({recipe_ingredient.ingredient.measurement_unit})')
                amount = recipe_ingredient.amount
                ingr_list.setdefault(name, 0)
                ingr_list[name] += amount
        return make_file(ingr_list)


class CustomUserViewSet(DjoserUserViewSet):
    """
    Расширяет стандарный UserViewSet из djoser, для работы
    url-ов subscriptions и subscribe.
    """
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-id',)
    permission_classes = [ReadOnly | IsAuthenticated]

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок пользователя."""
        pagination = CustomPagination()
        authors_id = request.user.follower.all().values_list('author')
        authors = (User.objects.filter(id__in=authors_id)
                   .prefetch_related('recipes'))
        page = pagination.paginate_queryset(authors, request)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request})

        return pagination.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id) -> Response:
        """Создает/удаляет подписку на автора."""
        author = get_object_or_404(User, id=id)
        user = request.user

        # Создание записи
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author,
                data={},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            user.follower.create(author=author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Удаление записи
        if request.method == 'DELETE':
            message = 'Подписка отсутсвует.'
            response = custom_delete(data={'author': author, 'user': user},
                                     model=Follow, message=message)
            return response

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Переопределил me для ограничения до метода GET."""
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
