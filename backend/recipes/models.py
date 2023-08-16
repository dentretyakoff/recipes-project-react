from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    "Модель рецептов."
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/')
    text = models.TextField('Текстовое описание блюда')
    cooking_time = models.DurationField('Время приготовления')

    def _str_(self):
        return self.name


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


class RecipeTag(models.Model):
    "Связь рецептов с тегами."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='tags',
                               verbose_name='Рецепт')
    tag = models.ForeignKey('Tag',
                            on_delete=models.CASCADE,
                            related_name='recipes',
                            verbose_name='Тег')


class RecipeIngredient(models.Model):
    "Связь рецептов с ингредиентами."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey('Ingredient',
                                   on_delete=models.CASCADE,
                                   related_name='recipes',
                                   verbose_name='Ингредиент')
    amount = models.DecimalField('Колчичество',
                                 max_digits=5,
                                 decimal_places=2)


class Favorite(models.Model):
    "Избранные рецепты."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')


class ShoppingCart(models.Model):
    "Список покупок."
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')
    user = models.ForeignKey('User',
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
