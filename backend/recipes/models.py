from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

from users.models import User


# Минимальное время приготовления, для валидатора в модели Recipe
MIN_COOKING_TIME = settings.MIN_COOKING_TIME


class Tag(models.Model):
    "Модель тегов."
    name = models.CharField('Тег', max_length=200)
    color = models.CharField('Цвет тега', max_length=7)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    "Модель ингредиентов."
    name = models.CharField('Ингредиент', max_length=200, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Модель рецептов."
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/')
    text = models.TextField('Текстовое описание блюда')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            MIN_COOKING_TIME,
            message='Укажите время приготовления больше 0.')])
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  through='RecipeTag')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         through='RecipeIngredient')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    "Связь рецептов с тегами."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='recipe_tag',
                               verbose_name='Рецепт')
    tag = models.ForeignKey('Tag',
                            on_delete=models.CASCADE,
                            verbose_name='Тег')

    class Meta:
        verbose_name = 'Рецепт - Тег'
        verbose_name_plural = 'Рецепты - Теги'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='unique_recipe_tag')
        ]


class RecipeIngredient(models.Model):
    "Связь рецептов с ингредиентами."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='recipe_igredient',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey('Ingredient',
                                   on_delete=models.CASCADE,
                                   related_name='recipe_igredient',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = 'Рецепты - Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class Favorite(models.Model):
    "Избранные рецепты."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    "Список покупок."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='shopping_carts',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='unique_shopping_cart')
        ]
