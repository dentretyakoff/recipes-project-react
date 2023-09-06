from datetime import datetime

from django.db import IntegrityError, models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User


def create_recipe_tag_relation(recipe: Recipe, tags_data: list) -> None:
    """Добавление новых тегов рецептам."""
    for tag_id in tags_data:
        tag = get_object_or_404(Tag, id=tag_id)
        RecipeTag.objects.get_or_create(recipe=recipe, tag=tag)


def create_recipe_ingredient_relation(
        recipe: Recipe, ingredients_data: dict) -> None:
    """Добавление новых ингредиентов к рецептам."""
    for ingredient_data in ingredients_data:
        ingredient = get_object_or_404(Ingredient,
                                       id=ingredient_data.get('id'))
        amount = ingredient_data.get('amount')
        RecipeIngredient.objects.update_or_create(
            recipe=recipe,
            ingredient=ingredient,
            defaults={'amount': amount})


def make_file(data: dict) -> HttpResponse:
    """Формирование файла со списком покупок."""
    response = HttpResponse(content_type='text/plan')
    response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
    cur_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    response.write(f'Foodgram список ингредиентов.\t{cur_datetime}\n')
    for name, amount in data.items():
        response.write(
            f'{name}:\t{amount}\n')

    return response


def custom_post(request: HttpRequest, recipe: Recipe, user: User,
                model: models.Model, message: str) -> Response:
    try:
        model.objects.create(recipe=recipe, user=user)
        image_url = request.build_absolute_uri(recipe.image.url)
        return Response({'id': recipe.id,
                         'name': recipe.name,
                         'image': image_url,
                         'cooking_time': recipe.cooking_time},
                        status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({'errors': message},
                        status=status.HTTP_400_BAD_REQUEST)


def custom_delete(data: dict, model: models.Model, message: str) -> Response:
    """
    Удаление объектов из M2M таблиц.
    Корзина, избранное, подписки.
    """
    try:
        obj = model.objects.get(**data)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except model.DoesNotExist:
        return Response({'errors': message},
                        status=status.HTTP_404_NOT_FOUND)
