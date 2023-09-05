from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    """Права на чтение всем, без токена."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class CurrentUserOrAdminOrReadOnly(BasePermission):
    """Права на эндпоинт пользователей."""
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.is_staff
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        user = request.user
        print(user.is_authenticated)
        if user.is_authenticated:
            return user.is_staff
        if type(obj) == type(user) and obj == user:
            return True
        return request.method in SAFE_METHODS