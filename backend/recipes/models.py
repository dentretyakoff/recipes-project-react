from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Recipe(models.Model):
    "Модель для рецептов."
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    name = models.CharField('Название рецецпта', max_length=150)
    image = models.ImageField('Картинка', upload_to='recipes/')
    description = models.TextField('Текстовое описание блюда')
    # igredient =
    tag = models.ForeignKey('Tag',
                            on_delete=models.SET_NULL,
                            related_name='recipes',
                            verbose_name='Тег рецепта')
    cooking_time = models.DateTimeField('Время приготовления')

    def _str_(self):
        return self.title
