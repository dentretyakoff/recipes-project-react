from django_filters import rest_framework as django_filters
from rest_framework import filters

from recipes.models import Recipe, Tag


class IngredientSearch(filters.BaseFilterBackend):
    """Поиск по ингредиентам."""
    def filter_queryset(self, request, queryset, view):
        ingredient = request.query_params.get('name')
        if ingredient:
            queryset = queryset.filter(name__istartswith=ingredient)
        return queryset


class RecipeFilterSet(django_filters.FilterSet):
    """Набор фильтров для рецептов."""
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='recipe_tag__tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    author = django_filters.NumberFilter(
        field_name='author')

    class Meta:
        model = Recipe
        fields = []

    def filter_is_in_shopping_cart(self, queryset, name, is_in_shopping_cart):
        if bool(is_in_shopping_cart):
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, is_favorited):
        if bool(is_favorited):
            return queryset.filter(favorites__user=self.request.user)
        return queryset
