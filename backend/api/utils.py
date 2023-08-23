from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import get_object_or_404

from recipes.models import (Ingredient, Recipe,  # isort: skip
                            RecipeIngredient,  # isort: skip
                            RecipeTag, Tag)  # isort: skip


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


def make_file(data):
    # Создаем временный объект для PDF-файла
    response = HttpResponse(content_type='text/plan')
    response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'
    cur_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    response.write(f'Foodgram список ингредиентов.\t{cur_datetime}\n')
    for key, value in data.items():
        response.write(
            f'{key}:\t{value}\n')

    return response
