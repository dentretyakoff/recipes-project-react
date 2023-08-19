import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            Recipe_Ingredient, Recipe_Tag)  # isort: skip
from users.models import User  # isort: skip


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        exclude = ('recipes',)

    # Переопределите метод to_internal_value для записи
    def to_internal_value(self, data):
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        exclude = ('recipes',)

    # Переопределите метод to_internal_value для записи
    def to_internal_value(self, data):
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор авторов рецептов."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed')

    # !Дописать
    def get_is_subscribed(self, user: User) -> bool:
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipetSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    author = AuthorSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    # !Дописать
    def get_is_favorited(self, recipe: Recipe) -> bool:
        return False

    # !Дописать
    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        return False

    def create(self, validated_data):
        print(validated_data)
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        # !Юзера нужно получать из request
        author = User.objects.first()
        recipe = Recipe.objects.create(**validated_data, author=author)

        # Создаем связь рецепта с тегами
        for tag_id in tags_data:
            tag = get_object_or_404(Tag, id=tag_id)
            Recipe_Tag.objects.create(recipe=recipe, tag=tag)

        # Создаем связь рецепта с ингредиентами
        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_data.get('id'))
            amount = ingredient_data.get('amount')
            Recipe_Ingredient.objects.create(recipe=recipe,
                                             ingredient=ingredient,
                                             amount=amount)
        return recipe
