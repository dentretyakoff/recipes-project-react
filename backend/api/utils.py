from django.shortcuts import get_object_or_404
from recipes.models import (Ingredient, Recipe, Recipe_Ingredient, Recipe_Tag,
                            Tag)


def create_recipe_tag_relation(recipe: Recipe, tags_data: list) -> None:
    """Добавление новых тегов рецептам."""
    for tag_id in tags_data:
        tag = get_object_or_404(Tag, id=tag_id)
        Recipe_Tag.objects.get_or_create(recipe=recipe, tag=tag)


def create_recipe_ingredient_relation(
        recipe: Recipe, ingredients_data: dict) -> None:
    """Добавление новых ингредиентов к рецептам."""
    for ingredient_data in ingredients_data:
        ingredient = get_object_or_404(Ingredient,
                                       id=ingredient_data.get('id'))
        amount = ingredient_data.get('amount')
        Recipe_Ingredient.objects.update_or_create(
            recipe=recipe,
            ingredient=ingredient,
            defaults={'amount': amount})
