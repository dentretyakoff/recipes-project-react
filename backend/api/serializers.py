import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers

from api.utils import (create_recipe_ingredient_relation,
                       create_recipe_tag_relation)
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = '__all__'

    def to_internal_value(self, data):
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')

    def to_internal_value(self, data):
        return data


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
        max_length=150,
        validators=[RegexValidator(r"^[\w.@+-]+\Z$", "Некорректный формат.")],
    )
    email = serializers.EmailField(required=True, max_length=254)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

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
    """Сериализатор рецептов."""
    author = UserSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = data.get('ingredients')
        min_value = 1  # Минимальное количество ингредиента

        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ingredient_id is None:
                raise serializers.ValidationError(
                    {'message': 'Укажите id ингредиента.'})
            if amount is None:
                raise serializers.ValidationError(
                    {'message': 'Поле amount обязательно для заполнения.'})
            if int(amount) < min_value:
                raise serializers.ValidationError(
                    {'message': 'Количество должно быть больше 0.'})

        return super().validate(data)

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

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=author)

        # Создаем связь рецепта с тегами
        create_recipe_tag_relation(recipe, tags_data)

        # Создаем связь рецепта с ингредиентами
        create_recipe_ingredient_relation(recipe, ingredients_data)

        return recipe

    def update(self, recipe, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        # Обновялем поля рецепта
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.save()

        # Удаляем лишние теги
        tags_delete = RecipeTag.objects.filter(
            recipe=recipe).exclude(tag_id__in=tags_data)
        for tag in tags_delete:
            tag.delete()

        # Добавляем новые теги
        create_recipe_tag_relation(recipe, tags_data)

        # Удаляем лишние ингредиенты
        ingredients_delete = RecipeIngredient.objects.filter(
            recipe=recipe).exclude(ingredient_id__in=[
                ingredient_id.get('id') for ingredient_id in ingredients_data
            ])
        for ingredient in ingredients_delete:
            ingredient.delete()

        # Добавляем новые ингредиенты
        create_recipe_ingredient_relation(recipe, ingredients_data)

        return recipe


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов, с ограниченным списком полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, user: User) -> dict:
        """Рецепты пользователя."""
        request = self.context.get('request')
        default_recipes_limit = 3  # Лимит, если не передан параметр
        recipes_limit = request.query_params.get(
            'recipes_limit',
            default_recipes_limit)
        recipes = user.recipes.all().order_by('-id')[:int(recipes_limit)]

        return RecipeShortSerializer(recipes,
                                     many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, user: User) -> int:
        """Количество рецептов пользователя."""
        return user.recipes.all().count()
