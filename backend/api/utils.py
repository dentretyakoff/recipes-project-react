from datetime import datetime

from django.db import models
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient


def create_recipe_ingredient_relation(
        recipe: Recipe, ingredients_data: dict) -> None:
    """Добавление новых ингредиентов к рецептам."""
    for ingredient_data in ingredients_data:
        amount = ingredient_data.get('amount')
        RecipeIngredient.objects.update_or_create(
            recipe=recipe,
            ingredient_id=ingredient_data.get('id'),
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
