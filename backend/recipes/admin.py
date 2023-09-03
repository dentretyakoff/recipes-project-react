from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from recipes.models import (Favorite, Ingredient,  # isort: skip
                            Recipe, RecipeIngredient,  # isort: skip
                            RecipeTag, ShoppingCart, Tag)  # isort: skip
from users.models import Follow  # isort: skip


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'text',
                    'cooking_time', 'author', 'favorite_count')
    fields = ('name', 'image', 'text', 'cooking_time',
              'author', 'favorite_count')
    readonly_fields = ('favorite_count',)
    inlines = (RecipeIngredientInline,)
    list_filter = ('name', 'author', 'tags')

    def favorite_count(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorites.all().count()

    favorite_count.short_description = 'Количество в избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
class IngredientAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ['name']


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient')


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'tag')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user')
