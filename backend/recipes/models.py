from django.db import models

from users.models import User  # isort: skip


class Tag(models.Model):
    "Модель тегов."
    name = models.CharField('Тег', max_length=200)
    color = models.CharField('Цвет тега', max_length=7)
    slug = models.SlugField(unique=True)

    def _str_(self):
        return self.name


class Ingredient(models.Model):
    "Модель ингредиентов."
    name = models.CharField('Тег', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def _str_(self):
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
    cooking_time = models.IntegerField('Время приготовления')
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')

    def _str_(self):
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
    amount = models.IntegerField('Колчичество')


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
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='unique_shopping_cart')
        ]
