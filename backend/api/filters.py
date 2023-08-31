from rest_framework import filters


class IngredientSearch(filters.BaseFilterBackend):
    """Поиск по ингредиентам."""
    def filter_queryset(self, request, queryset, view):
        ingredient = request.query_params.get('name')
        if ingredient:
            queryset = queryset.filter(name__istartswith=ingredient)
        return queryset
