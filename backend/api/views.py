from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            ShoppingCart, Favorite)  # isort: skip
from api.serializers import (TagSerializer, RecipetSerializer,  # isort: skip
                             IngredientSerializer,  # isort: skip
                             UserSerializer,  # isort: skip
                             AuthorSerializer,  # isort: skip
                             RecipetShortSerializer)  # isort: skip
from users.models import User, Follow  # isort: skip
from api.utils import (make_file,  # isort: skip
                       add_delete_favorites_or_shopping_carts)  # isort: skip


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
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipetSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk) -> Response:
        """Добавляет/удаляет рецепт в корзине."""
        recipe = get_object_or_404(Recipe, id=pk)
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        message = {
            'post': 'Рецепт уже в корзине.',
            'delete': 'Рецепт не найден в корзине.'
        }

        response = add_delete_favorites_or_shopping_carts(
            request, recipe, user, ShoppingCart, message)
        return response

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        """Добавляет/удаляет рецепт в избранном."""
        recipe = get_object_or_404(Recipe, id=pk)
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        message = {
            'post': 'Рецепт уже в избранном.',
            'delete': 'Рецепт не найден в избранном.'
        }
        response = add_delete_favorites_or_shopping_carts(
            request, recipe, user, Favorite, message)
        return response

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


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # http_method_names = ['get', 'post']

    @action(detail=False)
    def subscriptions(self, request):
        """Список подписок пользователя."""
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        follows = user.follower.all(
            ).select_related('author'
                             ).prefetch_related('author__recipes')
        authors = [follow.author for follow in follows]
        data = AuthorSerializer(authors, many=True).data

        for author in authors:
            for author_data in data:
                if author_data['id'] == author.id:
                    recipes = RecipetShortSerializer(
                        author.recipes.all(),
                        many=True,
                        context={'request': request}).data
                    author_data['recipes'] = recipes
                    author_data['recipes_count'] = author.recipes.all().count()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk) -> Response:
        """Создает/удаляет подписку на автора."""
        author = get_object_or_404(User, pk=pk)
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')
        # Создание записи
        if request.method == 'POST':
            try:
                Follow.objects.create(author=author, user=user)
                recipes = RecipetShortSerializer(
                        author.recipes.all(),
                        many=True,
                        context={'request': request}).data
                data = AuthorSerializer(author).data
                data['recipes'] = recipes
                data['recipes_count'] = author.recipes.all().count()
                return Response(data,
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'errors': 'Уже в подписках.'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Удаление записи
        if request.method == 'DELETE':
            try:
                obj = Follow.objects.get(author=author, user=user)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Follow.DoesNotExist:
                return Response({'errors': 'Нет в подписках.'},
                                status=status.HTTP_404_NOT_FOUND)
