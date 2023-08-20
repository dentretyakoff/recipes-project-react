import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Tag, Recipe, Ingredient,  # isort: skip
                            Recipe_Ingredient, Recipe_Tag,  # isort: skip
                            Shopping_Cart)  # isort: skip
from users.models import User  # isort: skip
from .utils import (create_recipe_tag_relation,  # isort: skip
                    create_recipe_ingredient_relation)  # isort: skip


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

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'measurement_unit': instance.measurement_unit,
            'amount': instance.recipe_igredient.first().amount
        }

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
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        # !Юзера нужно получать из request
        author = User.objects.first()
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
        recipe.image = validated_data.get('iamge', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.save()

        # Удаляем лишние теги
        tags_delete = Recipe_Tag.objects.filter(
            recipe=recipe).exclude(tag_id__in=tags_data)
        for tag in tags_delete:
            tag.delete()

        # Добавляем новые теги
        create_recipe_tag_relation(recipe, tags_data)

        # Удаляем лишние ингредиенты
        ingredients_delete = Recipe_Ingredient.objects.filter(
            recipe=recipe).exclude(ingredient_id__in=[
                ingredient_id.get('id') for ingredient_id in ingredients_data
            ])
        for ingredient in ingredients_delete:
            ingredient.delete()

        # Создаем связь рецепта с ингредиентами
        create_recipe_ingredient_relation(recipe, ingredients_data)

        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""


class Shopping_CartSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""
    class Meta:
        model = Shopping_Cart
        fields = '__all__'

    def validate(self, data):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        # !Юзера нужно получать из request
        user = User.objects.get(username='follower')

        return data

    def to_representation(self, shopping_cart):
        request = self.context.get('request')
        image_url = request.build_absolute_uri(shopping_cart.recipe.image.url)
        return {
            'id': shopping_cart.recipe.id,
            'name': shopping_cart.recipe.name,
            'image': image_url,
            'cooking_time': shopping_cart.recipe.cooking_time
        }

    def to_internal_value(self, data):
        return data
