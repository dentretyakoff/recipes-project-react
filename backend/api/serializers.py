import base64

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)
from rest_framework import serializers

from api.utils import create_recipe_ingredient_relation
from recipes.models import Ingredient, Recipe, Tag
from users.models import User

MIN_VALUE = settings.MIN_VALUE  # Минимальное количество ингредиента
REGEX_USERNAME = settings.REGEX_USERNAME
# Количество рецептов в подписках
DEFAULT_RECIPES_LIMIT = settings.DEFAULT_RECIPES_LIMIT
MAX_LEN_USERNAME = settings.MAX_LEN_USERNAME
MAX_LEN_EMAIL = settings.MAX_LEN_EMAIL
MAX_LEN_FIRST_NAME = settings.MAX_LEN_FIRST_NAME
MAX_LEN_LAST_NAME = settings.MAX_LEN_LAST_NAME


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор авторов рецептов."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed')

    def get_is_subscribed(self, author: User) -> bool:
        user = self.context['request'].user
        return (user.is_authenticated
                and user.follower.filter(author=author).exists())


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор создания пользователя."""
    username = serializers.CharField(
        max_length=MAX_LEN_USERNAME,
        validators=[RegexValidator(REGEX_USERNAME, 'Некорректный формат.')],
    )
    email = serializers.EmailField(required=True, max_length=MAX_LEN_EMAIL)
    first_name = serializers.CharField(
        required=True, max_length=MAX_LEN_FIRST_NAME)
    last_name = serializers.CharField(
        required=True, max_length=MAX_LEN_LAST_NAME)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'password')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""
    author = UserSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def to_representation(self, recipe):
        """Добавляем количество каждому ингредиенту."""
        recipe_ingredients = recipe.recipe_igredient.all()
        data = super().to_representation(recipe)
        for ingredient in data['ingredients']:
            ingredient['amount'] = recipe_ingredients.get(
                ingredient_id=ingredient['id']).amount
        return data

    def get_is_favorited(self, recipe: Recipe) -> bool:
        user = self.context['request'].user
        return (user.is_authenticated
                and user.favorites.filter(recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        user = self.context['request'].user
        return (user.is_authenticated
                and user.shopping_carts.filter(recipe=recipe).exists())


class RecipeWriteSerializer(RecipeSerializer):
    """Сериализатор записи рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    def validate(self, data):
        ingredients = data.get('ingredients')

        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ingredient_id is None:
                raise serializers.ValidationError('Укажите id ингредиента.')
            if amount is None:
                raise serializers.ValidationError(
                    'Поле amount обязательно для заполнения.')
            if int(amount) < MIN_VALUE:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0.')

        return super().validate(data)

    def create(self, validated_data):
        request = self.context['request']
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=request.user)

        # Создаем связь рецепта с тегами
        recipe.tags.set(tags_data)

        # Создаем связь рецепта с ингредиентами
        create_recipe_ingredient_relation(recipe, ingredients_data)

        return recipe

    def update(self, recipe, validated_data):
        request = self.context['request']
        tags_data = request.data.get('tags')
        ingredients_data = validated_data.pop('ingredients')

        # Обновляем теги
        recipe.tags.set(tags_data)

        # Удаляем лишние ингредиенты
        # Так как метод bulk_create игнорирует UniqueConstraint
        # использую .clear() вместо .remove(obj1, obj2,...)
        recipe.ingredients.clear()

        # Добавляем новые ингредиенты
        create_recipe_ingredient_relation(recipe, ingredients_data)

        return super().update(recipe, validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов, с ограниченным списком полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('username',)

    def get_recipes(self, user: User) -> dict:
        """Рецепты пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit',
            DEFAULT_RECIPES_LIMIT)
        recipes = user.recipes.all().order_by('-id')[:int(recipes_limit)]

        return RecipeShortSerializer(recipes,
                                     many=True,
                                     context={'request': request}).data

    def validate(self, data):
        author = self.instance
        request = self.context.get('request')

        if request.user.follower.filter(author=author).exists():
            raise serializers.ValidationError('Уже в подписках.')
        if request.user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя.')

        return data


class ShoppingCartSerializer(RecipeShortSerializer):
    """Сериализатор корзин."""

    class Meta(RecipeShortSerializer.Meta):
        read_only_fields = ('name', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        request = self.context.get('request')

        if request.user.shopping_carts.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине.')

        return data


class FavoriteSerializer(RecipeShortSerializer):
    """Сериализатор избранного."""

    class Meta(RecipeShortSerializer.Meta):
        read_only_fields = ('name', 'cooking_time', 'image')

    def validate(self, data):
        recipe = self.instance
        request = self.context.get('request')

        if request.user.favorites.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном.')

        return data
