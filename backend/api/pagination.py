from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Кастомная пагинация для управления
    количеством элементов на странице.
    """
    page_size_query_param = 'limit'
