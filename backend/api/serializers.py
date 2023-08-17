from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag, Recipe  # isort: skip

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipetSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
