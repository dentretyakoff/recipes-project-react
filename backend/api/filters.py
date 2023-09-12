from rest_framework import filters


class IngredientSearch(filters.BaseFilterBackend):
    """Поиск по ингредиентам."""
    def filter_queryset(self, request, queryset, view):
        ingredient = request.query_params.get('name')
        if ingredient:
            queryset = queryset.filter(name__istartswith=ingredient)
        return queryset


class IsInShoppingCartFilter(filters.BaseFilterBackend):
    """Фильтр по наличию рецептов в корзине покупок пользователя."""
    def filter_queryset(self, request, queryset, view):
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart is not None:
            return queryset.filter(shopping_carts__user=request.user)
        return queryset


class IsFavoritedFilter(filters.BaseFilterBackend):
    """Фильтр по наличию рецептов в избранном пользователя."""
    def filter_queryset(self, request, queryset, view):
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited:
            return queryset.filter(favorites__user=request.user)
        return queryset


class TagsFilter(filters.BaseFilterBackend):
    """Фильтр по тегам."""
    def filter_queryset(self, request, queryset, view):
        tags = request.query_params.getlist('tags')
        if tags:
            return queryset.filter(recipe_tag__tag__slug__in=tags).distinct()
        return queryset


class AuthorFilter(filters.BaseFilterBackend):
    """Фильтр по автору рецептов."""
    def filter_queryset(self, request, queryset, view):
        author = request.query_params.get('author')
        if author:
            return queryset.filter(author=author)
        return queryset
